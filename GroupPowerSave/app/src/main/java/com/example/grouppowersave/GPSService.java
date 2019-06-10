package com.example.grouppowersave;

import android.Manifest;
import android.app.AlarmManager;
import android.app.IntentService;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
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
import android.os.IBinder;
import android.os.SystemClock;
import android.provider.Settings;
import android.support.v4.app.ActivityCompat;
import android.telephony.TelephonyManager;
import android.util.Log;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class GPSService extends Service implements SensorEventListener {

    //public GPSService() {super("GPSService");}

    public static double ACC_THRESHOLD = 2.0;
    public static int lag = 50;
    public static double threshold = 4;
    public static double influence = 0.1;
    public static String url = "http://54.180.101.171:8080/";
    private static SensorManager mSensorManager;
    LocationManager mLocationManager;
    private static Context mContext;
    private static GPSService GPSService;
    static HttpClient client;
    Handler handler;
    Runner runner;
    int ACC_DATASET_SIZE = 350;
    double[][] accData = new double[ACC_DATASET_SIZE][4];
    public double[][] accData_rdy;
    int accCounter = 0;
    int count = 0;
    int count2 = 0;
    int change=0;
    static Location currentLocation;
    static String uniqueUserID = "IDnotSet";
    static int groupStatus = 0;
    LocationListener locationListenerGPS = new LocationListener() {
        @Override
        public void onLocationChanged(android.location.Location location) {
            if (location == null) {
                Log.e("locationupdate", "location is null");
            }
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
    public IBinder onBind(Intent arg0) {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // TODO Auto-generated method stub
        return START_STICKY;
    }

    @Override
    public void onTaskRemoved(Intent rootIntent) {
        // TODO Auto-generated method stub
        Intent restartService = new Intent(getApplicationContext(),
                this.getClass());
        restartService.setPackage(getPackageName());
        PendingIntent restartServicePI = PendingIntent.getService(
                getApplicationContext(), 1, restartService,
                PendingIntent.FLAG_ONE_SHOT);

        //Restart the service once it has been killed android


        AlarmManager alarmService = (AlarmManager) getApplicationContext().getSystemService(Context.ALARM_SERVICE);
        alarmService.set(AlarmManager.ELAPSED_REALTIME, SystemClock.elapsedRealtime() + 100, restartServicePI);

    }

    @Override
    public void onCreate() {
        // TODO Auto-generated method stub
        super.onCreate();

        //start a separate thread and start listening to your network object

        uniqueUserID = Settings.Secure.getString(getBaseContext().getContentResolver(), Settings.Secure.ANDROID_ID);

        //INITIALISATION
        Log.e("GPSService", "started");
        client = new HttpClient();
        mSensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);
        //have to change position of registerListener when we want to use accelerometer.
        mContext = this;
        GPSService=this;
        connectToServer();
        handler = new Handler();
        runner = new Runner();
        handler.post(runner);

    }


    @Override
    public void onDestroy() {
        super.onDestroy();
        handler.removeCallbacks(runner);
        Log.e("Background Service: ","Terminated");
    }

    public static void connectToServer() {
        Log.e("ConnectToServer", uniqueUserID);
        final JSONObject jsonO = new JSONObject();
        try {
            jsonO.put("id", uniqueUserID);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        final String jsonS = jsonO.toString();

        new AsyncTask<Void, Void, String>() {

            @Override
            protected String doInBackground(Void... voids) {
                try {

                    String body = client.register(url, jsonS);
                    Log.e("Registration", body);
                } catch (IOException ioe) {
                    ioe.printStackTrace();
                }
                return null;
            }
        }.execute();
    }
    private void getRealLocation(){
        mLocationManager = (LocationManager) getApplicationContext().getSystemService(Context.LOCATION_SERVICE);
        mLocationManager = (LocationManager) mContext.getSystemService(Context.LOCATION_SERVICE);
        try {
            mLocationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER,
                    100,
                    0, locationListenerGPS);

        } catch (SecurityException e) {
            Log.e("SecurityException", e.toString());
        }
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

        newLocation.setLatitude(currentLocation.getLatitude());
        newLocation.setLongitude(currentLocation.getLongitude());
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

    public void sendAccData() throws JSONException, IOException {
        SignalDetector signalDetector = new SignalDetector();
        ArrayList<Double> list = new ArrayList<>();
        for(int i=0;i<ACC_DATASET_SIZE;i++){
            double f = accData_rdy[i][0]*accData_rdy[i][0]+accData_rdy[i][1]*accData_rdy[i][1]+accData_rdy[i][2]*accData_rdy[i][2];
            f=Math.sqrt(f);
            list.add(f);
        }
        HashMap<String, List> result = signalDetector.analyzeDataForSignals(list, lag, threshold, influence);
        List<Integer> signals = result.get("signals");
        JSONArray time = new JSONArray();
        JSONArray magnitude = new JSONArray();
        final JSONObject obj = new JSONObject();
        for(int i=0;i<ACC_DATASET_SIZE;i++){
            if(signals.get(i)==1){
                time.put((long)accData_rdy[i][3]);
                magnitude.put(list.get(i));
            }
        }
        obj.put("time", time);
        obj.put("magnitude", magnitude);

        Log.d("accel",obj.toString());

        new AsyncTask<Void, Void, String>() {

            @Override
            protected String doInBackground(Void... voids) {
                try {
                    String response = client.provideAcceleration(url, uniqueUserID, obj.toString());
                } catch (IOException ioe) {
                    ioe.printStackTrace();
                }
                return null;
            }
        }.execute();
    }

    @Override
    public void onSensorChanged(SensorEvent sensorEvent) {
        if (sensorEvent.sensor.getType() == Sensor.TYPE_LINEAR_ACCELERATION) {
            double x = sensorEvent.values[0], y = sensorEvent.values[1], z = sensorEvent.values[2];

            if(accCounter==0 || (accCounter!=0 && System.currentTimeMillis()-accData[accCounter-1][3]>=200)) {
                accData[accCounter][0] = x;
                accData[accCounter][1] = y;
                accData[accCounter][2] = z;
                accData[accCounter][3] = System.currentTimeMillis();
                Log.d("accel", (long) accData[accCounter][3] + "");
                accCounter++;
                if (accCounter == ACC_DATASET_SIZE) {
                    accCounter = 0;
                    accData_rdy = accData;
                    accData = new double[ACC_DATASET_SIZE][4];
                    mSensorManager.unregisterListener(this);
                    try {
                        sendAccData();
                    } catch (JSONException e) {
                        e.printStackTrace();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            }
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int i) {

    }

    public static void providePosition() {
        final JSONObject jsonO = new JSONObject();
        try {
            if(currentLocation != null){
                jsonO.put("latitude", currentLocation.getLatitude());
                jsonO.put("longitude", currentLocation.getLongitude());
                jsonO.put("time", System.currentTimeMillis());
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
        final String jsonS = jsonO.toString();

        new AsyncTask<Void, Void, String>() {

            @Override
            protected String doInBackground(Void... voids) {
                try {
                    Log.e("ProvideLocationToServer", jsonS);
                    String response = client.providePosition(url, uniqueUserID, jsonS);
                    Log.d("ProvideLocationToServer",response);
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
                    Log.e("location update",pos);

                    JSONObject object = new JSONObject(pos);
                    if(object.has("latitude")) {
                        Location location = new Location("");
                        location.setLongitude(object.getDouble("latitude"));
                        location.setLongitude(object.getDouble("longitude"));
                        currentLocation=location;
                    }

                } catch (IOException ioe) {
                    ioe.printStackTrace();
                } catch (JSONException e) {
                    e.printStackTrace();
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
                    /*need_acceleration -> true -> user data put 1 mins
                    * status : integer / 0 : non-member, 1 : member, 2 : leader*/

                    JSONObject object = new JSONObject(ans);
                    if(object.getBoolean("need_acceleration")){
                        mSensorManager.registerListener(GPSService,
                                mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER), SensorManager.SENSOR_DELAY_NORMAL);
                    }

                    if(object.has("status")){
                        groupStatus=object.getInt("status");
                    }


                } catch (IOException ioe) {
                    ioe.printStackTrace();
                } catch (JSONException e) {
                    e.printStackTrace();
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
        Log.e("str to loc result",loc.toString());
        return loc;
    }

    int x = 0;

    public class Runner implements Runnable {
        //Should run every 5 seconds
        @Override
        public void run() {
            Log.e("Duty cycle", "Running");

            long curTime = System.currentTimeMillis();
            long t = (curTime/1000+1)*1000;

            handler.postDelayed(this, t-curTime);
            count++;
            count2++;
            change++;
            if(count==10) {
                count=0;
                receiveGroupStatus();
                //groupStatus=1;
            }

            Log.d("time", t-curTime+"");
            Log.d("currentState", groupStatus+"");
            Log.d("count", count+"");

            if(groupStatus == 2){
                getRealLocation();
                providePosition();
            }else if(groupStatus == 0 && count%2==0){
                getRealLocation();
                providePosition();
            }else if(groupStatus == 1 && count%5==0){
                receivePosition();
            //    getMockLocation();
            }

            if(count2==30){
                if(groupStatus==1){
                    getRealLocation();
                    providePosition();
                }
                count2=0;
            }

        }
    }
}
