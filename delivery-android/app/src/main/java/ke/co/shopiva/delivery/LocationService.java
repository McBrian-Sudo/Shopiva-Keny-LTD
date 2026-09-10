package ke.co.shopiva.delivery;

import android.Manifest;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ServiceInfo;
import android.location.Location;
import android.os.Build;
import android.os.IBinder;

import androidx.annotation.Nullable;

import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.android.gms.location.LocationCallback;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationResult;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.location.Priority;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

import android.webkit.CookieManager;

public class LocationService extends Service {
    public static final String ACTION_START = "ke.co.shopiva.delivery.START";
    public static final String ACTION_STOP = "ke.co.shopiva.delivery.STOP";

    private static final int NOTIFICATION_ID = 4101;
    private static final String CHANNEL_ID = "shopiva_delivery_tracking";

    private FusedLocationProviderClient fusedClient;
    private LocationCallback locationCallback;

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        fusedClient = LocationServices.getFusedLocationProviderClient(this);

        locationCallback = new LocationCallback() {
            @Override
            public void onLocationResult(LocationResult result) {
                if (result == null || result.getLastLocation() == null) return;
                sendLocationAsync(result.getLastLocation());
            }
        };
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        String action = intent != null ? intent.getAction() : ACTION_START;
        if (ACTION_STOP.equals(action)) {
            stopTracking();
            stopSelf();
            return START_NOT_STICKY;
        }

        if (!hasLocationPermission()) {
            stopSelf();
            return START_NOT_STICKY;
        }

        startAsForeground();
        requestLocationUpdates();
        return START_STICKY;
    }

    private boolean hasLocationPermission() {
        return checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                || checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED;
    }

    private void startAsForeground() {
        Intent openIntent = new Intent(this, MainActivity.class);
        PendingIntent contentIntent = PendingIntent.getActivity(
                this,
                1,
                openIntent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        Notification notification = new Notification.Builder(this, CHANNEL_ID)
                .setContentTitle("Shopiva delivery tracking active")
                .setContentText("Your location is being shared for active deliveries.")
                .setSmallIcon(android.R.drawable.ic_menu_mylocation)
                .setContentIntent(contentIntent)
                .setOngoing(true)
                .setCategory(Notification.CATEGORY_SERVICE)
                .build();

        if (Build.VERSION.SDK_INT >= 29) {
            startForeground(
                    NOTIFICATION_ID,
                    notification,
                    ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
            );
        } else {
            startForeground(NOTIFICATION_ID, notification);
        }
    }

    @SuppressWarnings("MissingPermission")
    private void requestLocationUpdates() {
        if (!hasLocationPermission()) return;

        LocationRequest request = new LocationRequest.Builder(
                Priority.PRIORITY_HIGH_ACCURACY,
                ShopivaConfig.UPDATE_INTERVAL_MS
        )
                .setMinUpdateIntervalMillis(ShopivaConfig.FASTEST_INTERVAL_MS)
                .setWaitForAccurateLocation(false)
                .build();

        fusedClient.requestLocationUpdates(request, locationCallback, getMainLooper());
    }

    private void stopTracking() {
        if (fusedClient != null && locationCallback != null) {
            fusedClient.removeLocationUpdates(locationCallback);
        }
        NotificationManager manager = getSystemService(NotificationManager.class);
        if (manager != null) manager.cancel(NOTIFICATION_ID);
    }

    private void sendLocationAsync(Location location) {
        new Thread(() -> sendLocation(location), "shopiva-location-upload").start();
    }

    private void sendLocation(Location location) {
        HttpURLConnection connection = null;
        try {
            String cookies = CookieManager.getInstance().getCookie(ShopivaConfig.BASE_URL);
            if (cookies == null || cookies.isEmpty()) return;

            String csrfToken = readCookie(cookies, "csrftoken");
            if (csrfToken == null || csrfToken.isEmpty()) return;

            URL url = new URL(ShopivaConfig.LOCATION_ENDPOINT);
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setDoOutput(true);
            connection.setConnectTimeout(10000);
            connection.setReadTimeout(10000);
            connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
            connection.setRequestProperty("Cookie", cookies);
            connection.setRequestProperty("X-CSRFToken", csrfToken);
            connection.setRequestProperty("User-Agent", "Shopiva-Delivery-Android/1.0");

            String body = "latitude=" + encode(String.valueOf(location.getLatitude()))
                    + "&longitude=" + encode(String.valueOf(location.getLongitude()))
                    + "&accuracy=" + encode(String.valueOf(location.getAccuracy()))
                    + "&speed=" + encode(String.valueOf(Math.max(0f, location.getSpeed())))
                    + "&heading=" + encode(String.valueOf(Math.max(0f, location.getBearing())));

            byte[] payload = body.getBytes(StandardCharsets.UTF_8);
            try (OutputStream output = connection.getOutputStream()) {
                output.write(payload);
            }

            int code = connection.getResponseCode();
            if (code >= 400) {
                readResponse(connection.getErrorStream());
            } else {
                readResponse(connection.getInputStream());
            }
        } catch (Exception ignored) {
            // Network failures are expected occasionally; the next location update retries.
        } finally {
            if (connection != null) connection.disconnect();
        }
    }

    private static String readCookie(String cookies, String name) {
        for (String item : cookies.split(";")) {
            String[] parts = item.trim().split("=", 2);
            if (parts.length == 2 && parts[0].equals(name)) return parts[1];
        }
        return null;
    }

    private static String encode(String value) throws Exception {
        return URLEncoder.encode(value, StandardCharsets.UTF_8.name());
    }

    private static String readResponse(InputStream stream) {
        if (stream == null) return "";
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8))) {
            StringBuilder builder = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) builder.append(line);
            return builder.toString();
        } catch (Exception ignored) {
            return "";
        }
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT < 26) return;
        NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "Shopiva Delivery Tracking",
                NotificationManager.IMPORTANCE_LOW
        );
        channel.setDescription("Shows when Shopiva delivery location tracking is active.");
        NotificationManager manager = getSystemService(NotificationManager.class);
        if (manager != null) manager.createNotificationChannel(channel);
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onDestroy() {
        stopTracking();
        super.onDestroy();
    }
}
