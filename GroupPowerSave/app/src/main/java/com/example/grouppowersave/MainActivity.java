package com.example.grouppowersave;

import android.content.Context;
import android.content.Intent;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.location.LocationProvider;
import android.os.Build;
import android.os.SystemClock;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import java.net.MalformedURLException;
import java.net.URL;

public class MainActivity extends AppCompatActivity {
    public static URL url;
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

        mContext = this;
        mLocationManager = (LocationManager) mContext.getSystemService(Context.LOCATION_SERVICE);
        try {
            mLocationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER,
                    2000,
                    10, locationListenerGPS);
   //         isLocationEnabled();
                getMockLocation();
            Log.e("Location!!!:", mLocationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER).toString());


        }catch(SecurityException e){
            Log.e("SecurityException",e.toString());
        }

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

        newLocation.setLatitude (10);
        newLocation.setLongitude(10);
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
}