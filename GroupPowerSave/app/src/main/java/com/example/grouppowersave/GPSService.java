package com.example.grouppowersave;


import android.app.IntentService;
<<<<<<< HEAD
import android.content.Intent;
import android.os.AsyncTask;
import android.util.Log;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
=======
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
>>>>>>> b8b4ea582082b1f6d7d26b1091d0ca5d5a140ff6
import java.net.URL;
import org.json.JSONObject;


public class GPSService extends IntentService {

    public GPSService() {
        super("GPSService");
    }

<<<<<<< HEAD
    public static URL url;

    {
        try {
            url = new URL("https://webhook.site/90286341-1ec0-4499-990b-1cb2e7dcaa7e");                      //enter URl here
=======
    public URL url;

    {
        try {
            url = new URL("http://jsonplaceholder.typicode.com/");                      //enter URl here
>>>>>>> b8b4ea582082b1f6d7d26b1091d0ca5d5a140ff6
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
<<<<<<< HEAD
public static void connectToServer(){
=======
public void connectToServer(){
>>>>>>> b8b4ea582082b1f6d7d26b1091d0ca5d5a140ff6
        final JSONObject jsonO = new JSONObject();
        final String jsonS = jsonO.toString();

        new AsyncTask<Void, Void, String>(){

            @Override
            protected String doInBackground(Void... voids) {
<<<<<<< HEAD
                try {
                    HttpClientExample hce = new HttpClientExample();
                    String body = hce.post("https://webhook.site/90286341-1ec0-4499-990b-1cb2e7dcaa7e", "11data=test data");
                    System.out.println(body);
                } catch(IOException ioe) {
                    ioe.printStackTrace();
                }
=======
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


>>>>>>> b8b4ea582082b1f6d7d26b1091d0ca5d5a140ff6
                return null;
            }
        }.execute();
}
}