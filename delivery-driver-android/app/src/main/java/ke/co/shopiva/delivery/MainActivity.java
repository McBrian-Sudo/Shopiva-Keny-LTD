package ke.co.shopiva.delivery;

import android.Manifest;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.webkit.CookieManager;
import android.webkit.GeolocationPermissions;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;

import androidx.annotation.NonNull;
import androidx.fragment.app.FragmentActivity;
import androidx.biometric.BiometricManager;
import androidx.biometric.BiometricPrompt;
import androidx.core.content.ContextCompat;

import java.nio.charset.StandardCharsets;
import java.security.KeyPairGenerator;
import java.security.KeyStore;
import java.security.Signature;
import java.security.spec.ECGenParameterSpec;
import java.util.concurrent.Executor;

public class MainActivity extends FragmentActivity {
    private static final int LOCATION_REQUEST = 1001;
    private static final String BASE_URL = "https://shopivakenya.top";
    private static final String PRIMARY_HOST = "shopivakenya.top";
    private static final String WWW_HOST = "www.shopivakenya.top";
    private static final String KEYSTORE = "AndroidKeyStore";
    private static final String KEY_ALIAS = "shopiva_delivery_biometric_v1";
    private static final String PREFS = "shopiva_delivery_security";
    private static final String PREF_BIOMETRIC_ENROLLED = "biometric_enrolled";

    private WebView webView;
    private String pendingGeoOrigin;
    private GeolocationPermissions.Callback pendingGeoCallback;
    private SharedPreferences securityPrefs;
    private boolean biometricGateChecked;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        securityPrefs = getSharedPreferences(PREFS, MODE_PRIVATE);

        FrameLayout root = new FrameLayout(this);
        webView = new WebView(this);
        WebSettings settings = webView.getSettings();

        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(false);
        settings.setSupportZoom(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setAllowUniversalAccessFromFileURLs(false);
        settings.setAllowFileAccessFromFileURLs(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);
        settings.setMediaPlaybackRequiresUserGesture(true);
        settings.setUserAgentString(settings.getUserAgentString() + " ShopivaDelivery/1.1");
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            settings.setSafeBrowsingEnabled(true);
        }

        CookieManager cookies = CookieManager.getInstance();
        cookies.setAcceptCookie(true);
        cookies.setAcceptThirdPartyCookies(webView, false);

        webView.addJavascriptInterface(new ShopivaBiometricBridge(), "ShopivaBiometric");

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return handleNavigation(request.getUrl());
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return handleNavigation(Uri.parse(url));
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onGeolocationPermissionsShowPrompt(
                    String origin, GeolocationPermissions.Callback callback) {
                if (!isTrustedOrigin(origin)) {
                    callback.invoke(origin, false, false);
                    return;
                }
                if (hasLocationPermission()) {
                    callback.invoke(origin, true, false);
                    return;
                }
                pendingGeoOrigin = origin;
                pendingGeoCallback = callback;
                requestLocationPermission();
            }
        });

        root.addView(webView, new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
        ));
        setContentView(root);

        if (hasBiometricKey() && isStrongBiometricAvailable()) {
            showBiometricGate();
        } else {
            loadDelivery();
        }
    }

    private void loadDelivery() {
        if (webView != null) {
            webView.loadUrl(BASE_URL + "/delivery/");
        }
    }

    private boolean isStrongBiometricAvailable() {
        return BiometricManager.from(this)
                .canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)
                == BiometricManager.BIOMETRIC_SUCCESS;
    }

    private boolean hasBiometricKey() {
        try {
            KeyStore keyStore = KeyStore.getInstance(KEYSTORE);
            keyStore.load(null);
            return keyStore.containsAlias(KEY_ALIAS) && securityPrefs.getBoolean(PREF_BIOMETRIC_ENROLLED, false);
        } catch (Exception ignored) {
            return false;
        }
    }

    private void showBiometricGate() {
        if (biometricGateChecked || webView == null) {
            return;
        }
        biometricGateChecked = true;

        Executor executor = ContextCompat.getMainExecutor(this);
        BiometricPrompt prompt = new BiometricPrompt(this, executor,
                new BiometricPrompt.AuthenticationCallback() {
                    @Override
                    public void onAuthenticationSucceeded(@NonNull BiometricPrompt.AuthenticationResult result) {
                        super.onAuthenticationSucceeded(result);
                        webView.post(() -> webView.loadUrl(BASE_URL + "/delivery/"));
                    }

                    @Override
                    public void onAuthenticationError(int errorCode, @NonNull CharSequence errString) {
                        super.onAuthenticationError(errorCode, errString);
                        biometricGateChecked = false;
                        webView.post(() -> webView.loadUrl(BASE_URL + "/delivery/login/"));
                    }

                    @Override
                    public void onAuthenticationFailed() {
                        super.onAuthenticationFailed();
                        // Keep the prompt available for another biometric attempt.
                    }
                });

        BiometricPrompt.PromptInfo promptInfo = new BiometricPrompt.PromptInfo.Builder()
                .setTitle("Shopiva Delivery verification")
                .setSubtitle("Verify your enrolled face or other strong biometric")
                .setDescription("Your biometric is processed by Android. Shopiva does not receive or store your face image or biometric template.")
                .setNegativeButtonText("Use password")
                .build();

        try {
            Signature signature = Signature.getInstance("SHA256withECDSA");
            KeyStore keyStore = KeyStore.getInstance(KEYSTORE);
            keyStore.load(null);
            SignatureKeyWrapper key = new SignatureKeyWrapper(keyStore, KEY_ALIAS);
            signature.initSign(key.privateKey);
            signature.update("SHOPIVA_DELIVERY_APP_UNLOCK".getBytes(StandardCharsets.UTF_8));
            prompt.authenticate(promptInfo, new BiometricPrompt.CryptoObject(signature));
        } catch (Exception e) {
            securityPrefs.edit().putBoolean(PREF_BIOMETRIC_ENROLLED, false).apply();
            loadDelivery();
        }
    }

    private void startBiometricEnrollment() {
        if (!isStrongBiometricAvailable()) {
            runJavascript("window.shopivaBiometricResult(false,'Strong device biometric is not available on this phone.');");
            return;
        }

        try {
            KeyStore keyStore = KeyStore.getInstance(KEYSTORE);
            keyStore.load(null);
            if (keyStore.containsAlias(KEY_ALIAS)) {
                keyStore.deleteEntry(KEY_ALIAS);
            }

            KeyPairGenerator generator = KeyPairGenerator.getInstance(
                    KeyProperties.KEY_ALGORITHM_EC, KEYSTORE);
            KeyGenParameterSpec.Builder builder = new KeyGenParameterSpec.Builder(
                    KEY_ALIAS,
                    KeyProperties.PURPOSE_SIGN
            )
                    .setAlgorithmParameterSpec(new ECGenParameterSpec("secp256r1"))
                    .setDigests(KeyProperties.DIGEST_SHA256)
                    .setUserAuthenticationRequired(true)
                    .setInvalidatedByBiometricEnrollment(true);

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                builder.setUserAuthenticationParameters(
                        0,
                        KeyProperties.AUTH_BIOMETRIC_STRONG
                );
            }

            generator.initialize(builder.build());
            generator.generateKeyPair();

            Signature signature = Signature.getInstance("SHA256withECDSA");
            keyStore.load(null);
            SignatureKeyWrapper key = new SignatureKeyWrapper(keyStore, KEY_ALIAS);
            signature.initSign(key.privateKey);
            signature.update("SHOPIVA_DELIVERY_BIOMETRIC_ENROLL".getBytes(StandardCharsets.UTF_8));

            Executor executor = ContextCompat.getMainExecutor(this);
            BiometricPrompt prompt = new BiometricPrompt(this, executor,
                    new BiometricPrompt.AuthenticationCallback() {
                        @Override
                        public void onAuthenticationSucceeded(@NonNull BiometricPrompt.AuthenticationResult result) {
                            securityPrefs.edit().putBoolean(PREF_BIOMETRIC_ENROLLED, true).apply();
                            String publicKey = key.publicKeyBase64();
                            runJavascript("window.shopivaBiometricEnrollmentReady(" + quoteJs(publicKey) + ");");
                        }

                        @Override
                        public void onAuthenticationError(int errorCode, @NonNull CharSequence errString) {
                            clearBiometricKey();
                            runJavascript("window.shopivaBiometricResult(false," + quoteJs(errString.toString()) + ");");
                        }
                    });

            BiometricPrompt.PromptInfo promptInfo = new BiometricPrompt.PromptInfo.Builder()
                    .setTitle("Enable Shopiva biometric login")
                    .setSubtitle("Confirm your enrolled face or other strong biometric")
                    .setDescription("This creates a device-bound key protected by Android biometric security. Shopiva never receives your biometric data.")
                    .setNegativeButtonText("Cancel")
                    .build();

            prompt.authenticate(promptInfo, new BiometricPrompt.CryptoObject(signature));
        } catch (Exception e) {
            clearBiometricKey();
            runJavascript("window.shopivaBiometricResult(false," + quoteJs("Could not prepare secure biometric login.") + ");");
        }
    }

    private void clearBiometricKey() {
        try {
            KeyStore keyStore = KeyStore.getInstance(KEYSTORE);
            keyStore.load(null);
            if (keyStore.containsAlias(KEY_ALIAS)) {
                keyStore.deleteEntry(KEY_ALIAS);
            }
        } catch (Exception ignored) {
        }
        securityPrefs.edit().putBoolean(PREF_BIOMETRIC_ENROLLED, false).apply();
    }

    private void runJavascript(String script) {
        if (webView != null) {
            webView.post(() -> webView.evaluateJavascript(script, null));
        }
    }

    private static String quoteJs(String value) {
        String safe = value == null ? "" : value
                .replace("\\", "\\\\")
                .replace("'", "\\'");
        return "'" + safe + "'";
    }

    private boolean handleNavigation(Uri uri) {
        String scheme = uri.getScheme();
        String host = uri.getHost();

        if ("https".equalsIgnoreCase(scheme) && isTrustedHost(host)) {
            return false;
        }

        if ("tel".equalsIgnoreCase(scheme)) {
            try {
                startActivity(new Intent(Intent.ACTION_DIAL, uri));
            } catch (Exception ignored) {
            }
            return true;
        }

        if ("http".equalsIgnoreCase(scheme) || "https".equalsIgnoreCase(scheme)) {
            try {
                startActivity(new Intent(Intent.ACTION_VIEW, uri));
            } catch (Exception ignored) {
            }
        }
        return true;
    }

    private boolean isTrustedHost(String host) {
        return PRIMARY_HOST.equalsIgnoreCase(host) || WWW_HOST.equalsIgnoreCase(host);
    }

    private boolean isTrustedOrigin(String origin) {
        return origin != null && origin.startsWith("https://")
                && (origin.equalsIgnoreCase("https://" + PRIMARY_HOST)
                || origin.equalsIgnoreCase("https://" + WWW_HOST));
    }

    private boolean hasLocationPermission() {
        return checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)
                == PackageManager.PERMISSION_GRANTED
                || checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION)
                == PackageManager.PERMISSION_GRANTED;
    }

    private void requestLocationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            requestPermissions(
                    new String[]{
                            Manifest.permission.ACCESS_FINE_LOCATION,
                            Manifest.permission.ACCESS_COARSE_LOCATION
                    },
                    LOCATION_REQUEST
            );
        }
    }

    @Override
    public void onRequestPermissionsResult(
            int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode != LOCATION_REQUEST || pendingGeoCallback == null) {
            return;
        }

        boolean granted = hasLocationPermission();
        GeolocationPermissions.Callback callback = pendingGeoCallback;
        String origin = pendingGeoOrigin;
        pendingGeoCallback = null;
        pendingGeoOrigin = null;
        callback.invoke(origin, granted, false);
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (pendingGeoCallback != null && pendingGeoOrigin != null) {
            pendingGeoCallback.invoke(pendingGeoOrigin, false, false);
            pendingGeoCallback = null;
            pendingGeoOrigin = null;
        }
        if (webView != null) {
            webView.stopLoading();
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }

    private class ShopivaBiometricBridge {
        @JavascriptInterface
        public boolean isAvailable() {
            return isStrongBiometricAvailable();
        }

        @JavascriptInterface
        public boolean isEnrolled() {
            return hasBiometricKey();
        }

        @JavascriptInterface
        public void enroll() {
            runOnUiThread(MainActivity.this::startBiometricEnrollment);
        }
    }

    private static class SignatureKeyWrapper {
        final java.security.PrivateKey privateKey;
        final java.security.PublicKey publicKey;

        SignatureKeyWrapper(KeyStore keyStore, String alias) throws Exception {
            KeyStore.PrivateKeyEntry entry = (KeyStore.PrivateKeyEntry) keyStore.getEntry(alias, null);
            if (entry == null) {
                throw new IllegalStateException("Biometric key not found");
            }
            privateKey = entry.getPrivateKey();
            publicKey = entry.getCertificate().getPublicKey();
        }

        String publicKeyBase64() {
            return android.util.Base64.encodeToString(publicKey.getEncoded(), android.util.Base64.NO_WRAP);
        }
    }
}
