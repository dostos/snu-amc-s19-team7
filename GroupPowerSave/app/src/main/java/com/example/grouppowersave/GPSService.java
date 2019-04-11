package com.example.grouppowersave;


import android.app.IntentService;
import android.app.Service;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.IBinder;
import android.support.annotation.Nullable;
import android.util.Log;
import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ProtocolException;
import java.net.URL;
import org.json.JSONObject;


public class GPSService extends IntentService {

    public GPSService() {
        super("GPSService");
    }

    public URL url;

    {
        try {
            url = new URL("http://jsonplaceholder.typicode.com/");                      //enter URl here
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
public void connectToServer(){
        final JSONObject jsonO = new JSONObject();
        final String jsonS = jsonO.toString();

        new AsyncTask<Void, Void, String>(){

            @Override
            protected String doInBackground(Void... voids) {
                DataOutputStream wr = null;
                try {
                    HttpURLConnection con = (HttpURLConnection)url.openConnection();
                    con.setRequestMethod("POST");

                        wr = new DataOutputStream(con.getOutputStream());
                        wr.writeBytes("data");
                        wr.flush();
                        wr.close();
                    } catch(IOException exception) {
                      Log.d("service","send json failed"); // more accurate error handling implementable if required
                    }finally{
                    try {
                        wr.close();
                    } catch (IOException e) {
                        Log.d("service","closing dataoutputstream failed");
                    }
                }


                return null;
            }
        }.execute();
}
}