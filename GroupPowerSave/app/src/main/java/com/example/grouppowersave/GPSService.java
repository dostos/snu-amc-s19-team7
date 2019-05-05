package com.example.grouppowersave;


import android.app.IntentService;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.location.LocationProvider;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.os.SystemClock;
import android.support.v7.app.AlertDialog;
import android.util.Log;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;

import org.json.JSONException;
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

    LocationManager mLocationManager;
    Context mContext;


    LocationListener locationListenerGPS=new LocationListener() {
        @Override
        public void onLocationChanged(android.location.Location location) {
            double latitude=location.getLatitude();
            double longitude=location.getLongitude();
            String msg="New Latitude: "+latitude + "New Longitude: "+longitude;
            Log.d("location",msg);

        }

        @Override
        public void onStatusChanged(String provider, int status, Bundle extras) {

        }

        @Override
        public void onProviderEnabled(String provider) {

        }

        @Override
        public void onProviderDisabled(String provider) {

        }
    };

    @Override
    protected void onHandleIntent(Intent workIntent) {
        //execute code here, information can be passed to this methode via the intent, but we won't use it most likely
        Log.e("GPSService","started");

        mContext = this;
        mLocationManager = (LocationManager) mContext.getSystemService(Context.LOCATION_SERVICE);
        try {
            mLocationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER,
                    2000,
                    10, locationListenerGPS);
            isLocationEnabled();
            getMockLocation();
//            Log.e("Location!!!:", mLocationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER).toString());


        }catch(SecurityException e){
            Log.e("SecurityException",e.toString());
        }

        connectToServer();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (requestingLocationUpdates) {
            startLocationUpdates();
        }
    }

    private void startLocationUpdates() {
        fusedLocationClient.requestLocationUpdates(locationRequest,
                locationCallback,
                null /* Looper */);
    }


    public static void connectToServer(){
        final JSONObject jsonO = new JSONObject();
        try {
            jsonO.put("ID","1");
        } catch (JSONException e) {
            e.printStackTrace();
        }
        final String jsonS = jsonO.toString();

        new AsyncTask<Void, Void, String>(){

            @Override
            protected String doInBackground(Void... voids) {
                try {
                    HttpClient client = new HttpClient();
                    String body = client.post("http://ec2-13-125-224-189.ap-northeast-2.compute.amazonaws.com:8080/register", jsonS);
                    Log.e("Sever Answer:", body);
                } catch(IOException ioe) {
                    ioe.printStackTrace();
                }
                return null;
            }
        }.execute();
    }
    private void getMockLocation()
    {
//        if(mLocationManager.getProvider(LocationManager.GPS_PROVIDER ) != null) {
        //         mLocationManager.removeTestProvider(LocationManager.GPS_PROVIDER);
        //   }

        mLocationManager.addTestProvider
                (
                        LocationManager.GPS_PROVIDER,
                        "requiresNetwork" == "",
                        "requiresSatellite" == "",
                        "requiresCell" == "",
                        "hasMonetaryCost" == "",
                        "supportsAltitude" == "",
                        "supportsSpeed" == "",
                        "supportsBearing" == "",

                        android.location.Criteria.POWER_LOW,
                        android.location.Criteria.ACCURACY_FINE
                );

        Location newLocation = new Location(LocationManager.GPS_PROVIDER);

        newLocation.setLatitude (10+System.currentTimeMillis()%100);
        newLocation.setLongitude(10+System.currentTimeMillis()%100);
        newLocation.setAccuracy(500);
        newLocation.setTime(System.currentTimeMillis());
        if (Build.VERSION.SDK_INT >= 17) {
            newLocation.setElapsedRealtimeNanos(SystemClock.elapsedRealtimeNanos());
        }

        mLocationManager.setTestProviderEnabled
                (
                        LocationManager.GPS_PROVIDER,
                        true
                );

        mLocationManager.setTestProviderStatus
                (
                        LocationManager.GPS_PROVIDER,
                        LocationProvider.AVAILABLE,
                        null,
                        System.currentTimeMillis()
                );

        mLocationManager.setTestProviderLocation
                (
                        LocationManager.GPS_PROVIDER,
                        newLocation
                );
    }
    private void isLocationEnabled() {
        mLocationManager = (LocationManager) mContext.getSystemService(Context.LOCATION_SERVICE);
        if( !mLocationManager.isProviderEnabled(LocationManager.GPS_PROVIDER) ) {
            new AlertDialog.Builder(mContext)
                    .setTitle("gps_not_found_title")  // GPS not found
                    .setMessage("gps_not_found_message") // Want to enable?
                    .setPositiveButton("yes", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialogInterface, int i) {
                            //  owner.startActivity(new Intent(android.provider.Settings.ACTION_LOCATION_SOURCE_SETTINGS));
                        }
                    })
                    .setNegativeButton("no", null)
                    .show();
        }
    }
}