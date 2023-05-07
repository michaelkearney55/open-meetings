package edu.brown.cs.server.handlers;

import com.squareup.moshi.JsonAdapter;
import com.squareup.moshi.Moshi;

import edu.brown.cs.searcher.Tsearch;
import edu.brown.cs.server.helpers.MeetingData;
import spark.Request;
import spark.Response;
import spark.Route;

/**
 * This is the LoadMeetingHandler. It handles the query "meetingSearch", which
 * loads a Meeting.
 */
public class LoadMeetingHandler implements Route {

    private final Tsearch meetingData;

    /**
     * This is the LoadCSVHandler constructor.
     * 
     * @param container - wrapper class for loaded CSV
     */
    public LoadMeetingHandler(Tsearch container) {
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
        String id = request.queryParams("id");
        
        //if no id query
        if (id == null) {
            return new LoadMeetingRequestFailureResponse("Must include an 'id' query.").serialize();
        }



        // need to take in meeting from searcher? and return 
        try {
            this.meetingData.importDocs(id); // this is where we get data from Tsearcher
            Moshi m = new Moshi.Builder().build();
            MeetingData meeting = m.adapter(MeetingData.class).fromJson(this.meetingData.importDocs(id););
            return new LoadMeetingSuccessResponse(meeting).serialize();
        } catch (Exception e) {

            return new LoadMeetingDatasourceFailureResponse("Invalid Meeting.").serialize();
        }

    }

    /**
     * Success response object.
     * 
     * @param response_type - success
     * @param meeting       - meeting info based on JSON
     */
    public record LoadMeetingSuccessResponse(String response_type, MeetingData meeting) {
        public LoadMeetingSuccessResponse(MeetingData meeting) {
            this("success", meeting);
        }

        String serialize() {
            try {
                // Just like in SoupAPIUtilities.
                // (How could we rearrange these similar methods better?)
                Moshi moshi = new Moshi.Builder()
                        // .add(Map.class) //this is complex, something i'm introducing
                        .build();
                JsonAdapter<LoadMeetingHandler.LoadMeetingSuccessResponse> adapter = moshi
                        .adapter(LoadMeetingHandler.LoadMeetingSuccessResponse.class);
                return adapter.toJson(this);
            } catch (Exception e) {
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
    public record LoadMeetingJsonFailureResponse(String response_type, String output) {
        public LoadMeetingJsonFailureResponse(String output) {
            this("error_bad_json", output);
        }

        /**
         * @return this response, serialized as Json
         */
        String serialize() {
            Moshi moshi = new Moshi.Builder().build();
            return moshi.adapter(LoadMeetingJsonFailureResponse.class).toJson(this);
        }
    }

    /**
     * Response object to send if someone requested soup before any recipes were
     * loaded
     */
    public record LoadMeetingRequestFailureResponse(String response_type, String output) {
        public LoadMeetingRequestFailureResponse(String output) {
            this("error_bad_request", output);
        }

        /**
         * @return this response, serialized as Json
         */
        String serialize() {
            Moshi moshi = new Moshi.Builder().build();
            return moshi.adapter(LoadMeetingRequestFailureResponse.class).toJson(this);
        }
    }

    /**
     * Response object to send if someone requested soup before any recipes were
     * loaded
     */
    public record LoadMeetingDatasourceFailureResponse(String response_type, String output) {
        public LoadMeetingDatasourceFailureResponse(String output) {
            this("error_datasource", output);
        }

        /**
         * @return this response, serialized as Json
         */
        String serialize() {
            Moshi moshi = new Moshi.Builder().build();
            return moshi.adapter(LoadMeetingDatasourceFailureResponse.class).toJson(this);
        }
    }

}