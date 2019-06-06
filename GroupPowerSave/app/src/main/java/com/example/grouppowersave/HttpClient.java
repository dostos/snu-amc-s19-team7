package com.example.grouppowersave;

import android.util.Log;

import java.io.BufferedReader;
import java.io.Closeable;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;

public class HttpClient {


    public static String getPosition(String getUrl, String id) throws IOException {
        //URL url = new URL(getUrl);             // use this if ID is transmitted via RequestPoperty
        URL url = appendUri(getUrl, "user-data"+id).toURL(); //generate query string
        String readLine = null;
        HttpURLConnection con = (HttpURLConnection) url.openConnection();
        con.setRequestMethod("GET");
        con.setRequestProperty("user-data", id);   //alternate way of transmitting ID - currently we are using query string so this is not checked
        int responseCode = con.getResponseCode();
        if (responseCode == HttpURLConnection.HTTP_OK) {
            BufferedReader in = new BufferedReader(
                    new InputStreamReader(con.getInputStream()));
            StringBuffer response = new StringBuffer();
            while ((readLine = in .readLine()) != null) {
                response.append(readLine);
            } in .close();

            return response.toString();

        } else {
            Log.e("GET position failed","returning 0");
            return "0";
        }
    }

    public static String ping(String getUrl, String id) throws IOException {
        //URL url = new URL(getUrl);             // use this if ID is transmitted via RequestProperty
        URL url = appendUri(getUrl, "ping"+id).toURL(); //generate query string
        String readLine = null;
        HttpURLConnection con = (HttpURLConnection) url.openConnection();
        con.setRequestMethod("GET");
        con.setRequestProperty("ping", id);   //alternate way of transmitting ID - currently we are using query string so this is not checked
        int responseCode = con.getResponseCode();
        if (responseCode == HttpURLConnection.HTTP_OK) {
            BufferedReader in = new BufferedReader(
                    new InputStreamReader(con.getInputStream()));
            StringBuffer response = new StringBuffer();
            while ((readLine = in .readLine()) != null) {
                response.append(readLine);
            } in .close();

            return response.toString();

        } else {
            Log.e("GET ping failed","returning 0");
            return "0";
        }
    }

        //post to server
    public String register(String postUrl, String data) throws IOException {
        URL url = new URL(postUrl);
        HttpURLConnection con = (HttpURLConnection) url.openConnection();
        con.setRequestMethod("POST");

        con.setDoOutput(true);

        this.sendData(con, data);

        return this.read(con.getInputStream());
    }

    public void providePosition (String putUrl, String data) throws IOException{

            URL url = new URL(putUrl);
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("PUT");
            con.setDoOutput(true);
            //con.setRequestProperty("Content-Type", "application/json");
            //con.setRequestProperty("Accept", "application/json");

            this.sendData(con, data);
            Log.d("Location sent response:", ""+con.getResponseCode());
    }


    protected void sendData(HttpURLConnection con, String data) throws IOException {
        DataOutputStream wr = null;
        try {
            wr = new DataOutputStream(con.getOutputStream());
            wr.writeBytes(data);
            wr.flush();
            wr.close();
        } catch(IOException exception) {
            throw exception;
        } finally {
            this.closeQuietly(wr);
        }
    }

    private String read(InputStream is) throws IOException {
        BufferedReader in = null;
        String inputLine;
        StringBuilder body;
        try {
            in = new BufferedReader(new InputStreamReader(is));

            body = new StringBuilder();

            while ((inputLine = in.readLine()) != null) {
                body.append(inputLine);
            }
            in.close();

            return body.toString();
        } catch(IOException ioe) {
            throw ioe;
        } finally {
            this.closeQuietly(in);
        }
    }

    protected void closeQuietly(Closeable closeable) {
        try {
            if( closeable != null ) {
                closeable.close();
            }
        } catch(IOException ex) {

        }
    }
    //save way of appending query string to URI
    public static URI appendUri(String uri, String appendQuery) {
        URI oldUri = null;
        try {
            oldUri = new URI(uri);
        } catch (URISyntaxException e) {
            e.printStackTrace();
        }

        String newQuery = oldUri.getQuery();
        if (newQuery == null) {
            newQuery = appendQuery;
        } else {
            newQuery += "&" + appendQuery;
        }

        URI newUri = null;
        try {
            newUri = new URI(oldUri.getScheme(), oldUri.getAuthority(),
                    oldUri.getPath(), newQuery, oldUri.getFragment());
        } catch (URISyntaxException e) {
            e.printStackTrace();
        }

        return newUri;
    }
}