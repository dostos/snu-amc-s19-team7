package com.example.grouppowersave;


import android.app.IntentService;
import android.content.Intent;
import android.os.AsyncTask;
import android.util.Log;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import org.json.JSONObject;


public class GPSService extends IntentService {

    public GPSService() {
        super("GPSService");
    }

    public static URL url;

    {
        try {
            url = new URL("https://webhook.site/90286341-1ec0-4499-990b-1cb2e7dcaa7e");                      //enter URl here
        } catch (MalformedURLException e) {
            Log.d("Service","URL failed");
        }
    }

    @Override
    protected void onHandleIntent(Intent workIntent) {
        Log.e("GPSService","started");
        //execute code here, information can be passed to this methode via the intent, but we won't use it most likely
        connectToServer();

    }
public static void connectToServer(){
        final JSONObject jsonO = new JSONObject();
        final String jsonS = jsonO.toString();

        new AsyncTask<Void, Void, String>(){

            @Override
            protected String doInBackground(Void... voids) {
                try {
                    HttpClientExample hce = new HttpClientExample();
                    String body = hce.post("https://webhook.site/90286341-1ec0-4499-990b-1cb2e7dcaa7e", "11data=test data");
                    System.out.println(body);
                } catch(IOException ioe) {
                    ioe.printStackTrace();
                }
                return null;
            }
        }.execute();
}
}