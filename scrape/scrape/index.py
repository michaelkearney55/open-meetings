from resource_type import ResourceType
from download import generate_document_url
from pymongo.database import Database
from threading import Lock

def get_resource_by_id(rtype: ResourceType, db: Database, db_lock: Lock, id: int) -> dict:
    collection = db[rtype.collection_name()]
    result: dict | None = collection.find_one({'_id': id})
    if result:
        return result
    raise RuntimeError(f'Error: could not find resource of type {rtype} and id {id}')

def get_meeting(db: Database, db_lock: Lock, id: int) -> dict:
    return get_resource_by_id(ResourceType.MEETING, db, db_lock, id)

def get_body(db: Database, db_lock: Lock, id: int) -> dict:
    return get_resource_by_id(ResourceType.BODY, db, db_lock, id)

def get_document(db: Database, db_lock: Lock, id: int) -> dict:
    return get_resource_by_id(ResourceType.DOCUMENT, db, db_lock, id)

def get_snippet(db: Database, db_lock: Lock, id: int) -> dict:
    return get_resource_by_id(ResourceType.SNIPPET, db, db_lock, id)

def get_meeting_as_indexable(db: Database, db_lock: Lock, id: int) -> dict:
    d = {}
    meeting = get_meeting(db, db_lock, id)
    d['id'] = str(meeting['_id'])
    d['body'] = get_body(db, db_lock, meeting['body'])['name']
    d['meeting_dt'] = int(meeting['meeting_dt'])
    d['address'] = meeting['meeting_address']
    d['filing_dt'] = int(meeting['filing_dt'])
    for field in ['is_emergency', 'is_annual_calendar', 'is_public_notice']:
        d[field] = (field in meeting) and (meeting[field])
    d['is_cancelled'] = 'is_cancelled' in meeting and meeting['is_cancelled']
    if d['is_cancelled']:
        if 'cancelled_dt' in meeting:
            d['cancelled_dt'] = int(meeting['cancelled_dt'])
        if 'cancelled_reason' in meeting and 'cancelled_reason':
            d['cancelled_reason'] = meeting['cancelled_reason']
    if 'contact_name' in meeting:
        d['contactPerson'] = meeting['contact_name']
    if 'contact_email' in meeting:
        d['contactEmail'] = meeting['contact_email']
    if 'contact_phone' in meeting:
        d['contactPhone'] = meeting['contact_phone']
    if len(meeting['agendas']) > 0:
        latest_agenda = get_document(db, db_lock, meeting['agendas'][0])
        snippets = []
        for snippet in latest_agenda['snippets']:
            snippets.append(get_snippet(db, db_lock, snippet)['text'])
        d['latestAgenda'] = snippets
        d['latestAgendaLink'] = generate_document_url(latest_agenda['path'])
    if len(meeting['minutes']) > 0:
        latest_minutes = get_document(db, db_lock, meeting['minutes'][0])
        snippets = []
        for snippet in latest_minutes['snippets']:
            snippets.append(get_snippet(db, db_lock, snippet)['text'])
        d['latestMinutes'] = snippets
        d['latestMinutesLink'] = generate_document_url(latest_minutes['path'])
    return d

def get_body_as_indexable(db: Database, db_lock: Lock, id: int) -> dict:
    return get_body(db, db_lock, id)