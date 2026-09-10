package ke.co.shopiva.delivery;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.view.ViewGroup;
import android.webkit.CookieManager;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private static final int LOCATION_PERMISSION_REQUEST = 2001;
    private static final int NOTIFICATION_PERMISSION_REQUEST = 2002;

    private TextView statusView;
    private WebView webView;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.WHITE);

        LinearLayout controls = new LinearLayout(this);
        controls.setOrientation(LinearLayout.VERTICAL);
        controls.setPadding(18, 12, 18, 12);

        statusView = new TextView(this);
        statusView.setText("Shopiva Delivery • Tracking is OFF");
        statusView.setTextColor(Color.DKGRAY);
        statusView.setTextSize(14);
        controls.addView(statusView, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));

        LinearLayout buttons = new LinearLayout(this);
        buttons.setOrientation(LinearLayout.HORIZONTAL);
        buttons.setPadding(0, 10, 0, 0);

        Button start = new Button(this);
        start.setText("Start tracking");
        start.setOnClickListener(v -> startTrackingFlow());

        Button stop = new Button(this);
        stop.setText("Stop tracking");
        stop.setOnClickListener(v -> stopTracking());

        buttons.addView(start, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1));
        buttons.addView(stop, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1));
        controls.addView(buttons);

        root.addView(controls, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));

        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(true);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient());

        CookieManager.getInstance().setAcceptCookie(true);
        CookieManager.getInstance().setAcceptThirdPartyCookies(webView, false);

        webView.loadUrl(ShopivaConfig.BASE_URL + "/delivery/");
        root.addView(webView, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                0,
                1));

        setContentView(root);
    }

    private void startTrackingFlow() {
        if (!hasLocationPermission()) {
            requestLocationPermission();
            return;
        }

        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, NOTIFICATION_PERMISSION_REQUEST);
            return;
        }

        CookieManager.getInstance().flush();
        Intent intent = new Intent(this, LocationService.class);
        intent.setAction(LocationService.ACTION_START);
        startForegroundService(intent);
        statusView.setText("Shopiva Delivery • Tracking is ON");
        Toast.makeText(this, "Background tracking started", Toast.LENGTH_SHORT).show();
    }

    private void stopTracking() {
        Intent intent = new Intent(this, LocationService.class);
        intent.setAction(LocationService.ACTION_STOP);
        startService(intent);
        statusView.setText("Shopiva Delivery • Tracking is OFF");
        Toast.makeText(this, "Tracking stopped", Toast.LENGTH_SHORT).show();
    }

    private boolean hasLocationPermission() {
        return checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                || checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED;
    }

    private void requestLocationPermission() {
        if (Build.VERSION.SDK_INT >= 31) {
            requestPermissions(
                    new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION},
                    LOCATION_PERMISSION_REQUEST
            );
        } else {
            requestPermissions(
                    new String[]{Manifest.permission.ACCESS_FINE_LOCATION},
                    LOCATION_PERMISSION_REQUEST
            );
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == LOCATION_PERMISSION_REQUEST) {
            if (hasLocationPermission()) {
                startTrackingFlow();
            } else {
                Toast.makeText(this, "Shopiva needs location permission for delivery tracking", Toast.LENGTH_LONG).show();
                openAppSettings();
            }
        } else if (requestCode == NOTIFICATION_PERMISSION_REQUEST) {
            startTrackingFlow();
        }
    }

    private void openAppSettings() {
        Intent intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
        intent.setData(Uri.parse("package:" + getPackageName()));
        startActivity(intent);
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
