package edu.brown.cs.server.handlers;

import com.squareup.moshi.JsonAdapter;
import com.squareup.moshi.Moshi;

import edu.brown.cs.searcher.Tsearch;
import edu.brown.cs.server.helpers.MeetingData;
import spark.Request;
import spark.Response;
import spark.Route;


/**
 * This is the SearchHandler. It handles the query "meetingSearch", which
 * loads a Meeting.
 */
public class SearchHandler implements Route {

    private final Tsearch meetingData;

    /**
     * This is the LoadCSVHandler constructor.
     * @param container - wrapper class for loaded CSV
     */
    public SearchHandler(Tsearch container) {
        this.meetingData = container;
    }


    /**
     * This is what is called when a request is made.
     * @param request - request
     * @param response - response
     * @return - appropriate response object
     * @throws Exception
     */
    @Override
    public Object handle(Request request, Response response) throws Exception {
        String searchWord = request.queryParams("searchword");
        String page = request.queryParams("page"); // int, direct to tsense
        String perPage = request.queryParams("perpage"); // int, direct to tsense
        String publicBody = request.queryParams("publicbody");
        String dateStart = request.queryParams("datestart"); // int
        String dateEnd = request.queryParams("datend"); // int




        //if no param query
        if (searchWord == null) {
            return new SearchRequestFailureResponse("Must include an 'id' query.").serialize();
        }
        else{
            searchWord = this.meetingData.filterQuery(searchWord)
        }

        //if no optional query, repeat as needed
        if (page == null) {
            return "depends what message needs to be sent to the tsense endpoint"
        }



        // need to take in meeting results from searcher? and return the necessary info
        try {
            this.meetingData.searchDoc(searchWord, dateEnd); // this is where we get data from Tsearcher
            Moshi m = new Moshi.Builder().build();
            MeetingData meeting = m.adapter(MeetingData.class).fromJson(JSON);
            return new SearchSuccessResponse(meeting).serialize();
        } catch (Exception e) {

            return new SearchDatasourceFailureResponse("Invalid Meeting.").serialize();
        }

    }

    /**
     * Success response object.
     * @param response_type - success
     * @param meeting - meeting info based on JSON
     */
    public record SearchSuccessResponse(String response_type, int found, int out_of, int page, FacetCounts facet_counts, Hits hits) {
        public SearchSuccessResponse(int found, int out_of, int page, FacetCounts facet_counts, Hits hits) {
            this("success", found, out_of, page, facet_counts, hits);
        }

        String serialize() {
            try {
                // Just like in SoupAPIUtilities.
                //   (How could we rearrange these similar methods better?)
                Moshi moshi = new Moshi.Builder()
                        //.add(Map.class) //this is complex, something i'm introducing
                        .build();
                JsonAdapter<SearchHandler.SearchSuccessResponse> adapter = moshi.adapter(SearchHandler.SearchSuccessResponse.class);
                return adapter.toJson(this);
            } catch(Exception e) {
                // For debugging purposes, show in the console _why_ this fails
                // Otherwise we'll just get an error 500 from the API in integration
                // testing.
                e.printStackTrace();
                throw e;
            }
        }
    }

    /**
     * Response object to send if someone requested an invalid meeting
     */
    public record SearchJsonFailureResponse(String response_type, String output) {
        public SearchJsonFailureResponse(String output) { this("error_bad_json", output); }

        /**
         * @return this response, serialized as Json
         */
        String serialize() {
            Moshi moshi = new Moshi.Builder().build();
            return moshi.adapter(SearchJsonFailureResponse.class).toJson(this);
        }
    }

    /**
     * Response object to send if someone requested soup before any recipes were loaded
     */
    public record SearchRequestFailureResponse(String response_type, String output) {
        public SearchRequestFailureResponse(String output) { this("error_bad_request", output); }

        /**
         * @return this response, serialized as Json
         */
        String serialize() {
            Moshi moshi = new Moshi.Builder().build();
            return moshi.adapter(SearchRequestFailureResponse.class).toJson(this);
        }
    }

    /**
     * Response object to send if someone requested soup before any recipes were loaded
     */
    public record SearchDatasourceFailureResponse(String response_type, String output) {
        public SearchDatasourceFailureResponse(String output) { this("error_datasource", output); }

        /**
         * @return this response, serialized as Json
         */
        String serialize() {
            Moshi moshi = new Moshi.Builder().build();
            return moshi.adapter(SearchDatasourceFailureResponse.class).toJson(this);
        }
    }

}