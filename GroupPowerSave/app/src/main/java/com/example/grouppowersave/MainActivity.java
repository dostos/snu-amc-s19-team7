package com.example.grouppowersave;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
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
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        startService(new Intent(this, GPSService.class));
    }
}