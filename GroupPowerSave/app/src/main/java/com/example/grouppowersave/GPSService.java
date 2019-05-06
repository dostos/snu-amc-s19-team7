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
import android.os.Handler;
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
    static HttpClient client;
    Handler handler;
    Runner runner;
    static Location currentLocation;
    static String uniqueUserID = "IDnotSet";
    static int groupStatus = 0;
    LocationListener locationListenerGPS = new LocationListener() {
        @Override
        public void onLocationChanged(android.location.Location location) {
            currentLocation = location;
            double latitude = location.getLatitude();
            double longitude = location.getLongitude();
            String msg = "New Latitude: " + latitude + "New Longitude: " + longitude;
            Log.e("location", msg);
            Log.e("locationString", currentLocation.toString());

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
        //INITIALISATION
        Log.e("GPSService", "started");
        client = new HttpClient();
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
        handler = new Handler();
        runner = new Runner();
        handler.post(runner);
        connectToServer();
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        handler.removeCallbacks(runner);
        Log.e("Background Service: ","Terminated");
    }

    public static void connectToServer() {
        final JSONObject jsonO = new JSONObject();
        try {
            jsonO.put("register", "Dieser Wert hat keinen Sinn, aber ich schreib ihn mal auf deutsch.");
        } catch (JSONException e) {
            e.printStackTrace();
        }
        final String jsonS = jsonO.toString();

        new AsyncTask<Void, Void, String>() {

            @Override
            protected String doInBackground(Void... voids) {
                try {

                    String body = client.register(url, jsonS);
                    Log.e("UniqueID (registration)", body);
                    uniqueUserID = body;
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
    public static void providePosition() {
        final JSONObject jsonO = new JSONObject();
        try {
            if(currentLocation != null){
            jsonO.put("user-data", uniqueUserID+currentLocation.toString());}
        } catch (JSONException e) {
            e.printStackTrace();
        }
        final String jsonS = jsonO.toString();

        new AsyncTask<Void, Void, String>() {

            @Override
            protected String doInBackground(Void... voids) {
                try {
                    Log.e("ProvideLocationToServer", jsonS);
                    client.providePosition(url, jsonS);
                } catch (IOException ioe) {
                    ioe.printStackTrace();
                }
                return null;
            }
        }.execute();
    }
    public static void receivePosition(){
        new AsyncTask<Void, Void, String>() {

            @Override
            protected String doInBackground(Void... voids) {
                try {
                    String pos = client.getPosition(url, uniqueUserID);
                    Log.e("LocationReceived", pos);
                    currentLocation = stringToLocation(pos);


                } catch (IOException ioe) {
                    ioe.printStackTrace();
                }
                return null;
            }
        }.execute();
    }
    public static void receiveGroupStatus(){
        new AsyncTask<Void, Void, String>() {

            @Override
            protected String doInBackground(Void... voids) {
                try {
                    String ans = client.ping(url, uniqueUserID);
                    Log.e("GroupStatusReceived", ans);
                    groupStatus = Integer.parseInt(ans);

                } catch (IOException ioe) {
                    ioe.printStackTrace();
                }
                return null;
            }
        }.execute();
    }

    //location.toString fromat looks like gps 75.000000,75.000000 acc=500 et=+1d22h29m13s93ms mock
    public static Location stringToLocation(String locS){
        char[] locC = locS.toCharArray();
        String locSpre = "";
        for(int i = 1; i< locS.length(); i++){
            if(!(locC[i] != '0' && locC[i] != '1' && locC[i] != '2' && locC[i] != '3' && locC[i] != '4' && locC[i] != '5' && locC[i] != '6' && locC[i] != '7' &&locC[i] != '8' && locC[i] != '9' && locC[i] != ' ' && locC[i] != ',' && locC[i] != '.')){
                locSpre = locSpre + locC[i];
            }
        }
        String[] locA = locSpre.split(" ");
        String[] longlatS = locA[1].split(",");
        Location loc = new Location(currentLocation);
        loc.setLatitude(Double.parseDouble(longlatS[0]));
        loc.setLongitude(Double.parseDouble(longlatS[1]));
        loc.setAccuracy(Float.parseFloat(locA[2]));
        //Time has format like +1d22h29m13s93ms - not needed but could be added
        return loc;
    }
    public class Runner implements Runnable {
        //Should run every 5 seconds
        @Override
        public void run() {
            Log.d("AndroidClarified", "Running");
            handler.postDelayed(this, 1000 * 5);
            receiveGroupStatus();
            if(groupStatus == 0){
                providePosition();
            }else {
                receivePosition();
            }
        }
    }
}
