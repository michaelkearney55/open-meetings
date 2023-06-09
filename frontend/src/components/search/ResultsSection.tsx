import styles from "./ResultsSection.module.css";

import {
  MeetingResult,
  SearchFilters,
  SearchResults,
} from "../../meetingTypes";
import SearchResult from "./SearchResult";
import Sidebar from "./Sidebar";

interface ResultSectionProps {
  searchResults: SearchResults;
  handleBodySelect: (body: string | null) => void;
  handleDate: (dateStart: Date | null, dateEnd: Date | null) => void;
  searchParams: URLSearchParams;
  filters: SearchFilters;
  keyphrase: string;
  bodyFacet: Map<string, number>;
}

export default function ResultSection({
  searchResults,
  handleBodySelect,
  handleDate,
  searchParams,
  filters,
  keyphrase,
  bodyFacet,
}: ResultSectionProps) {
  const getDateFilterInfo = (): string => {
    if (!filters.dateStart && !filters.dateEnd) {
      return "anytime";
    }
    const dateStartInfo: string = filters.dateStart
      ? filters.dateStart.toLocaleDateString()
      : "anytime";
    const dateEndInfo: string = filters.dateEnd
      ? filters.dateEnd.toLocaleDateString()
      : "anytime";
    return `between ${dateStartInfo} and ${dateEndInfo}`;
  };

  const dateFilterInfo: string = getDateFilterInfo();
  const bodyInfo: string = filters.body ? filters.body : "all bodies";
  const keyphraseInfo: string = keyphrase === "*" ? "all meetings" : keyphrase;

  return (
    <div className={styles.ResultsSection}>
      <Sidebar
        handleBodySelect={handleBodySelect}
        handleDate={handleDate}
        bodyFacet={bodyFacet}
        filters={filters}
      />
      <main className={styles["results"]} aria-label="Search results">

        <i aria-live="polite" aria-atomic="true" role="presentation">
          displaying {searchResults.results.length} out of{" "}
          {searchResults.resultsInfo.found} results
          <span className="sr-only">
            {keyphrase !== "*" ? (
              <span>Search Term: {keyphraseInfo}</span>
            ) : (
              <></>
            )}
            <span>Body: {bodyInfo}</span>
            <span>Date: {dateFilterInfo}</span>
          </span>
        </i>
        {searchResults.results.length != 0 ? (
          searchResults.results.map((result: MeetingResult) => (
            <SearchResult
              key={result.id}
              result={result}
              searchParams={searchParams}
            />
          ))
        ) : (
          <p>No results found</p>
        )}
      </main>
    </div>
  );
}
