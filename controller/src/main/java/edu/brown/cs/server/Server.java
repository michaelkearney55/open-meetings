package edu.brown.cs.server;

import static spark.Spark.after;
import java.util.List;
import edu.brown.cs.searcher.StopWords;
import edu.brown.cs.searcher.Tsearch;
import spark.Spark;
/*
 * top level class where we use spark to start the server and run endpoint handlers
 */
public class Server {

        // TODO: add more :)
        static StopWords sWords = new StopWords(List.of("a", "the", "you", "we", "me", "i", "them", "this", "that", "is", "and", "but", "as", "or"));
    public static void main(String[] args) {
        String api_key = System.getenv("TYPESENSE_API_KEY");

        if (api_key == null) {
            throw new RuntimeException("Error: no TYPESENSE_API_KEY variable set in shell environment.");
        }

        Spark.port(3232);

        after((request, response) -> {
            response.header("Access-Control-Allow-Origin", "*");
            response.header("Access-Control-Allow-Methods", "*");
        });

        Tsearch searcher = new Tsearch(new StopWords(List.of()));
        
        // put in all the endpoint handlers
        Spark.get("meetingSearch", new SearchHandler(searcher));
        Spark.get("getMeeting", new LoadMeetingHandler(searcher));
        Spark.init();
        Spark.awaitInitialization();
        System.out.println("Server started.");
    }
}
