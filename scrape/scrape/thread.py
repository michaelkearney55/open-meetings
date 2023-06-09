from io import TextIOWrapper
import datetime as dt
from typing import Tuple, Iterator, Callable, Any
import threading
from concurrent.futures import ThreadPoolExecutor
from requests import Response
from time import sleep
from progress.bar import Bar
import traceback
from sqlite3 import Connection

from io_utils import threadsafe_write_if_log, add_event

# def build_scrape_resource_into_database(
#         get_resource: Callable[[int], Iterator[Any]],
# )

def build_download_unique_resource(
    request_resource: Callable[[int], Response],
    is_duplicate: Callable[[int], bool],
    is_response_success: Callable[[Response], bool],
    write_to_file: Callable[[int, Response], str],
    try_count: int,
    try_pause: float,
    bar_and_lock: Tuple[Bar, threading.Lock] | None = None,
    log_and_lock: Tuple[TextIOWrapper, threading.Lock] | None = None,
    verbose: bool = False,
    resource_name:str = 'resource'
    ) -> Callable[[int], Tuple[int, int, int]]:
    """
    build_donwload_unique_resource constructs a function to download a resource with a unique int identifier. The function has built-in error handling, work-deduplication, amd logging.
    
    :param request_resource: requests resource with unique identifier
    :param is_duplicate: if resource was already downloaded
    :param is_response_success: if the response was successful
    :param generate_filename: geneartes filename from unique identifier
    :param try_count: how many times to try downloading each resource
    :param wait_secs_before_retry: after failure, seconds to wait before retry
    :param log_and_lock: the file and thread lock on it to write the log to
    :param verbose: if true, also writes non-error downloads to log.
    :param resource_name: short name of the resource type, e.g. 'meeting'
    :return: a function that downloads a resource
    """
    def download_unique_resource(id: int) -> Tuple[int, int, int]:
        """
        Downloads a a unique resource.

        :param id: a unique identifier for the resource
        :return: (id, outcome, try_count) where
                    id: id of resource
                    outcome: 0=success, 1=duplicate, 2=error
                    try_count: number of tries attempted
        """
        # Setup
        count: int = 0
        log_header = f'\nDownload report for {resource_name} {id}:\n'
        running_log: str = ''
        def before_return(is_error: bool):
            if verbose or is_error:
                threadsafe_write_if_log(log_header + running_log, log_and_lock)
            if bar_and_lock:
                with bar_and_lock[1]:
                    bar_and_lock[0].next()
        
        # Check if resource was already downloaded
        if is_duplicate(id):
            running_log = add_event(f"{resource_name} {id} is duplicate.", running_log)
            before_return(is_error=False)
            return (id, 1, count)
        # Request resource
        while count < try_count:
            count += 1
            try:
                before = dt.datetime.utcnow().timestamp()
                response = request_resource(id)
                elapsed = dt.datetime.utcnow().timestamp() - before
                # Download was successful
                if is_response_success(response):
                    running_log = add_event(f"Request #{count} successful in {elapsed} seconds.", running_log)
                    # Write to file was successful
                    try:
                        filename: str = write_to_file(id, response)
                        running_log = add_event(f"{resource_name} successfully written to {filename}.", running_log)
                        before_return(is_error=False)
                        return (id, 0, count)
                    # Write to file was not successful
                    except Exception as e:
                        running_log = add_event(f"Downloaded {resource_name} but could not create file due to {str(type(e))}.", running_log)
                        before_return(is_error=True)
                        return (id, 2, count)
                # Download was not successful, retry
                running_log = add_event(f"Request #{count} was not successful in {elapsed} seconds. Retrying...", running_log)
            # Download was not successful, retry
            except Exception as e:
                running_log = add_event(f"Request #{count} raised {str(type(e))}. Retrying...", running_log)
            # Wait before retrying download
            sleep(try_pause)

        # Download was not successful after exhausting try_count
        running_log = add_event(f"Could not complete request after {count} tries.", running_log)
        before_return(is_error=True)
        return (id, 2, count)
        
    return download_unique_resource

def build_write_to_file(generate_filename: Callable[[int], str]) -> Callable[[int, Response], str]:

    def write_to_file(id: int, response: Response) -> str:
        filename = generate_filename(id)
        # Write to file was successful
        with open(filename, 'xb') as f:
                for chunk in response.iter_content(chunk_size=128):
                    f.write(chunk)
        return filename
    return write_to_file

def mock_write_to_file(id: int, response: Response) -> str:
    return 'test'

def build_process_unique_resource(
    is_duplicate: Callable[[int, Connection], bool],
    process_resource: Callable[[int, Connection], None],
    db_connection: Connection,
    bar: Bar | None,
    log: TextIOWrapper | None,
    verbose: bool = False,
    resource_name:str = 'resource'
    ) -> Callable[[int], Tuple[int, int]]:
    """
    Construct a function to download a resource
    
    :param get_local_resource: gets local resource with unique identifier
    :param is_duplicate: if resource was already processed
    :param process_resource: processes the resource
    :param log_and_lock: the file and thread lock on it to write the log to
    :param verbose: if true, also writes non-error downloads to log.
    :param resource_name: short name of the resource type, e.g. 'meeting'
    """
    def process_unique_resource(id: int) -> Tuple[int, int]:
        """
        Downloads a a unique resource.

        :param id: a unique identifier for the resource
        :return: (id, outcome) where
                    id: id of resource
                    outcome: 0=success, 1=duplicate, 2=error
        """
        log_header = f'\nDownload report for {resource_name} {id}:\n'
        running_log: str = ''

        def before_return(is_error: bool):
            if log and (verbose or is_error):
                log.write(log_header + running_log)
            if bar:
                bar.next()

        # Check if resource was already processed
        if is_duplicate(id, db_connection):
            running_log = add_event(f"{resource_name} {id} is duplicate.", running_log)
            before_return(True)
            return (id, 1)
        try:
            process_resource(id, db_connection)
        except Exception as e:
            running_log = add_event(f"Error processing {resource_name} {id}: exception {str(type(e))} occurred:", running_log)
            before_return(True)
            return(id, 2)
        running_log = add_event(f"{resource_name} {id} processed.", running_log)
        before_return(True)
        return (id, 0)
    return process_unique_resource


def threaded_action_by_id(
    ids: Iterator[int],
    action: Callable[[int], int],
    max_workers: int,
    log_and_lock: Tuple[TextIOWrapper, threading.Lock] | None = None
    ) -> Iterator[int]:
    """
    Processes resources in a multi-threaded way

    :param ids: unique ids to process
    :param process_resource: processes a unique resource
    :param max_workers: maximum number of threads to use
    :param log_and_lock: the file and thread lock on it to write the log to
    :return: 
    """
    print(f'Threading...')
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        try:
            return executor.map(action, ids)
        except Exception as e:
            traceback.print_exc()
            if log_and_lock is not None:
                with log_and_lock[1]:
                    log_and_lock[0].write(f"Exception {str(type(e))}:\n")
                    traceback.print_exc(file=log_and_lock[0])
            raise e