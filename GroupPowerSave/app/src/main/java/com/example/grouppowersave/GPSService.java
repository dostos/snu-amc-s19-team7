package com.example.grouppowersave;

import android.app.IntentService;
import android.content.Context;
import android.content.Intent;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.location.LocationProvider;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.os.SystemClock;
import android.util.Log;

import java.io.IOException;

import org.json.JSONException;
import org.json.JSONObject;

public class GPSService extends IntentService implements SensorEventListener {

    public GPSService() {
        super("GPSService");
    }

    public static String url = "http://ec2-13-125-224-189.ap-northeast-2.compute.amazonaws.com:8080/register";
    private SensorManager mSensorManager;
    LocationManager mLocationManager;
    Context mContext;

    LocationListener locationListenerGPS = new LocationListener() {
        @Override
        public void onLocationChanged(android.location.Location location) {
            double latitude = location.getLatitude();
            double longitude = location.getLongitude();
            String msg = "New Latitude: " + latitude + "New Longitude: " + longitude;
            Log.e("location", msg);

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
        Log.e("GPSService", "started");
        mSensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);
        //have to change position of registerListener when we want to use accelerometer.
        mSensorManager.registerListener(this,
                mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER), SensorManager.SENSOR_DELAY_NORMAL);
        mContext = this;
        mLocationManager = (LocationManager) mContext.getSystemService(Context.LOCATION_SERVICE);
        try {
            mLocationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER,
                    2000,
                    0, locationListenerGPS);
            getMockLocation();

        } catch (SecurityException e) {
            Log.e("SecurityException", e.toString());
        }

        connectToServer();
    }

    public static void connectToServer() {
        final JSONObject jsonO = new JSONObject();
        try {
            jsonO.put("ID", "1");
        } catch (JSONException e) {
            e.printStackTrace();
        }
        final String jsonS = jsonO.toString();

        new AsyncTask<Void, Void, String>() {

            @Override
            protected String doInBackground(Void... voids) {
                try {
                    HttpClient client = new HttpClient();
                    String body = client.post(url, jsonS);
                    Log.e("Sever Answer:", body);
                } catch (IOException ioe) {
                    ioe.printStackTrace();
                }
                return null;
            }
        }.execute();
    }

    private void getMockLocation() {
        if (mLocationManager.getProvider(LocationManager.GPS_PROVIDER) != null) {
            mLocationManager.removeTestProvider(LocationManager.GPS_PROVIDER);
        }
        Log.e("locProvider", mLocationManager.getAllProviders().toString());
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

        newLocation.setLatitude(10 + System.currentTimeMillis() % 100);
        newLocation.setLongitude(10 + System.currentTimeMillis() % 100);
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

    @Override
    public void onSensorChanged(SensorEvent sensorEvent) {
        if (sensorEvent.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
            double x = sensorEvent.values[0], y = sensorEvent.values[1], z = sensorEvent.values[2];
            //send this values when we want.
            //    Log.d("x,y,z",x+","+y+","+z);
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int i) {

    }
}