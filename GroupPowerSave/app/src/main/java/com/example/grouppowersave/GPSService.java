package com.example.grouppowersave;


import android.app.IntentService;
import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.support.annotation.Nullable;
import android.util.Log;

public class GPSService extends IntentService {
    public GPSService() {
        super("GPSService");
    }
    @Override
    protected void onHandleIntent(Intent workIntent) {
        Log.e("GPSService","started");
        //execute code here, information can be passed to this methode via the intent, but we won't use it most likely
    }

    /*
    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        //code for executed service here
        Log.e("testTag","testMsg");
        return super.onStartCommand(intent, flags, startId);
    }
    */
}