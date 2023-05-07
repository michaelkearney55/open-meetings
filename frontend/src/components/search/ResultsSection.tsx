import styles from "./ResultsSection.module.css";

import { MeetingResult, Search } from "../../meetingTypes";
import SearchResult from "./SearchResult";
import Sidebar from "./Sidebar";

interface ResultSectionProps {
  search: Search;
  handleBodySelect: (body: string | null) => void;
  handleDate: (dateStart: Date | null, dateEnd: Date | null) => void;
  searchParams: URLSearchParams;
}

export default function ResultSection({
  search,
  handleBodySelect,
  handleDate,
  searchParams,
}: ResultSectionProps) {
  return (
    <div className={styles.ResultsSection}>
      <Sidebar
        search={search}
        handleBodySelect={handleBodySelect}
        handleDate={handleDate}
        searchParams={searchParams}
      />
      <main id={styles["results"]}>
        {search.results.map((result: MeetingResult) => (
          <SearchResult key={result.id} result={result} />
        ))}
      </main>
    </div>
  );
}