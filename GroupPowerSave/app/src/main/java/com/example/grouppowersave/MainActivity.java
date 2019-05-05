package com.example.grouppowersave;

import android.app.Activity;
import android.content.Intent;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;


import android.util.Log;
public class MainActivity extends AppCompatActivity implements SensorEventListener {



    private SensorManager mSensorManager;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        startService(new Intent(this, GPSService.class));

        mSensorManager=(SensorManager) getSystemService(SENSOR_SERVICE);
        //have to change position of registerListener when we want to use accelerometer.
        mSensorManager.registerListener(this,
                mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER), SensorManager.SENSOR_DELAY_NORMAL);


    }

    @Override
    public void onSensorChanged(SensorEvent sensorEvent) {
        if(sensorEvent.sensor.getType()==Sensor.TYPE_ACCELEROMETER){
            double x=sensorEvent.values[0], y=sensorEvent.values[1], z=sensorEvent.values[2];
            //send this values when we want.
        //    Log.d("x,y,z",x+","+y+","+z);
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int i) {

    }

}