package com.example.grouppowersave;

import android.content.Intent;
<<<<<<< HEAD
import android.os.AsyncTask;
=======
>>>>>>> b8b4ea582082b1f6d7d26b1091d0ca5d5a140ff6
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;

<<<<<<< HEAD
import org.json.JSONObject;

import java.io.DataOutputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

public class MainActivity extends AppCompatActivity {
    public static URL url;

    {
        try {
            url = new URL("https://webhook.site/90286341-1ec0-4499-990b-1cb2e7dcaa7e");                      //enter URl here
        } catch (MalformedURLException e) {
            Log.d("Service","URL failed");
        }
    }
=======
public class MainActivity extends AppCompatActivity {

>>>>>>> b8b4ea582082b1f6d7d26b1091d0ca5d5a140ff6
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        startService(new Intent(this, GPSService.class));
    }
<<<<<<< HEAD
=======


>>>>>>> b8b4ea582082b1f6d7d26b1091d0ca5d5a140ff6
}
