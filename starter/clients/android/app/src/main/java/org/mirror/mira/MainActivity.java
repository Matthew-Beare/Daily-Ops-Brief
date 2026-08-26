package org.mirror.mira;

import android.Manifest;
import android.app.Activity;
import android.app.AlarmManager;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanRecord;
import android.bluetooth.le.ScanResult;
import android.content.Context;
import android.content.Intent;
import android.content.IntentSender;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.nfc.NfcAdapter;
import android.nfc.Tag;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.ParcelUuid;
import android.util.Base64;
import android.util.SparseArray;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.webkit.WebViewAssetLoader;

import com.google.android.gms.auth.api.identity.AuthorizationClient;
import com.google.android.gms.auth.api.identity.AuthorizationRequest;
import com.google.android.gms.auth.api.identity.AuthorizationResult;
import com.google.android.gms.auth.api.identity.Identity;
import com.google.android.gms.common.Scope;
import com.google.android.gms.common.api.ApiException;
import com.google.android.gms.tasks.Task;
import com.google.mlkit.vision.barcode.common.Barcode;
import com.google.mlkit.vision.codescanner.GmsBarcodeScanner;
import com.google.mlkit.vision.codescanner.GmsBarcodeScanning;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public final class MainActivity extends Activity {
    private static final int FILE_CHOOSER_REQUEST = 2001;
    private static final int BLE_PERMISSION_REQUEST = 2002;
    private static final int GOOGLE_AUTH_REQUEST = 2003;
    private static final Set<String> GOOGLE_API_HOSTS = Set.of(
            "www.googleapis.com",
            "sheets.googleapis.com",
            "gmail.googleapis.com",
            "calendar.googleapis.com",
            "openidconnect.googleapis.com"
    );

    private WebView webView;
    private ValueCallback<Uri[]> fileCallback;
    private NfcAdapter nfcAdapter;
    private boolean nfcReaderActive = false;
    private BluetoothLeScanner bleScanner;
    private boolean bleScanActive = false;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private AuthorizationClient googleAuthorizationClient;
    private String googleAccessToken;
    private long googleAccessTokenExpiryMs = 0L;
    private final Set<String> googleGrantedScopes = new HashSet<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestNotificationPermissionIfNeeded();
        nfcAdapter = NfcAdapter.getDefaultAdapter(this);
        googleAuthorizationClient = Identity.getAuthorizationClient(this);

        WebViewAssetLoader assetLoader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(true);
        webView.addJavascriptInterface(new NativeBridge(), "MirrorNative");
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return assetLoader.shouldInterceptRequest(request.getUrl());
            }
        });
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (fileCallback != null) fileCallback.onReceiveValue(null);
                fileCallback = callback;
                Intent intent = params.createIntent();
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                startActivityForResult(intent, FILE_CHOOSER_REQUEST);
                return true;
            }
        });
        setContentView(webView);
        webView.loadUrl("https://appassets.androidplatform.net/assets/index.html");
    }

    @Override
    protected void onPause() {
        disableNfcReader();
        stopBleScan();
        super.onPause();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == GOOGLE_AUTH_REQUEST) {
            if (resultCode != RESULT_OK || data == null) {
                notifyGoogleAuthError("Google connection was canceled.");
                return;
            }
            try {
                AuthorizationResult result = googleAuthorizationClient.getAuthorizationResultFromIntent(data);
                acceptGoogleAuthorization(result);
            } catch (ApiException error) {
                notifyGoogleAuthError("Google connection failed: " + error.getStatusCode());
            }
            return;
        }
        if (requestCode != FILE_CHOOSER_REQUEST || fileCallback == null) return;
        Uri[] result = WebChromeClient.FileChooserParams.parseResult(resultCode, data);
        fileCallback.onReceiveValue(result);
        fileCallback = null;
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    private void requestNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU
                && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 1001);
        }
    }

    private void setWallDisplay(boolean enabled) {
        if (enabled) getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            WindowInsetsController controller = getWindow().getInsetsController();
            if (controller != null) {
                if (enabled) {
                    controller.hide(WindowInsets.Type.statusBars() | WindowInsets.Type.navigationBars());
                    controller.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
                } else {
                    controller.show(WindowInsets.Type.statusBars() | WindowInsets.Type.navigationBars());
                }
            }
        } else if (webView != null) {
            webView.setSystemUiVisibility(enabled
                    ? View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                    | View.SYSTEM_UI_FLAG_FULLSCREEN
                    | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                    | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                    | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                    | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                    : View.SYSTEM_UI_FLAG_VISIBLE);
        }
    }

    private List<Scope> googleScopesFor(String capabilities) {
        Set<String> requested = new HashSet<>();
        requested.add("openid");
        requested.add("email");
        requested.add("profile");
        // Cloud MIRA writes its own evidence through drive.file and also needs read-only
        // Drive metadata discovery so an app installed later can find the same MIRROR
        // workbook/manifest that MIRA may already have initialized through ChatGPT.
        requested.add("https://www.googleapis.com/auth/drive.file");
        requested.add("https://www.googleapis.com/auth/drive.metadata.readonly");
        String raw = capabilities == null ? "" : capabilities;
        for (String item : raw.split(",")) {
            switch (item.trim()) {
                case "drive" -> requested.add("https://www.googleapis.com/auth/drive.file");
                case "sheets" -> requested.add("https://www.googleapis.com/auth/spreadsheets");
                case "calendar" -> requested.add("https://www.googleapis.com/auth/calendar.events");
                case "gmail_read" -> requested.add("https://www.googleapis.com/auth/gmail.readonly");
                default -> { }
            }
        }
        List<Scope> scopes = new ArrayList<>();
        for (String scope : requested) scopes.add(new Scope(scope));
        return scopes;
    }

    private void authorizeGoogle(String capabilities) {
        if (googleAuthorizationClient == null) {
            notifyGoogleAuthError("Google Play Services authorization is unavailable on this device.");
            return;
        }
        AuthorizationRequest request = AuthorizationRequest.builder()
                .setRequestedScopes(googleScopesFor(capabilities))
                .build();
        googleAuthorizationClient.authorize(request)
                .addOnSuccessListener(result -> {
                    if (result.hasResolution() && result.getPendingIntent() != null) {
                        try {
                            startIntentSenderForResult(
                                    result.getPendingIntent().getIntentSender(),
                                    GOOGLE_AUTH_REQUEST,
                                    null,
                                    0,
                                    0,
                                    0
                            );
                        } catch (IntentSender.SendIntentException error) {
                            notifyGoogleAuthError("Android could not open the Google permission screen.");
                        }
                    } else {
                        acceptGoogleAuthorization(result);
                    }
                })
                .addOnFailureListener(error -> notifyGoogleAuthError(
                        "Google authorization is unavailable: " + (error.getMessage() == null ? error.getClass().getSimpleName() : error.getMessage())
                ));
    }

    private void acceptGoogleAuthorization(AuthorizationResult result) {
        String token = result.getAccessToken();
        if (token == null || token.isBlank()) {
            notifyGoogleAuthError("Google approved the account but did not return an access token.");
            return;
        }
        googleAccessToken = token;
        googleGrantedScopes.clear();
        if (result.getGrantedScopes() != null) googleGrantedScopes.addAll(result.getGrantedScopes());
        long expiresInSeconds = 3300L;
        Bundle params = result.getTokenResponseParams();
        if (params != null && params.containsKey("expires_in")) {
            Object raw = params.get("expires_in");
            try { expiresInSeconds = Long.parseLong(String.valueOf(raw)); } catch (Exception ignored) { }
        }
        googleAccessTokenExpiryMs = System.currentTimeMillis() + Math.max(60L, expiresInSeconds - 60L) * 1000L;
        JSONObject payload = new JSONObject();
        try {
            payload.put("connected", true);
            payload.put("granted_scopes", new JSONArray(googleGrantedScopes));
            payload.put("expires_at", googleAccessTokenExpiryMs);
        } catch (Exception ignored) { }
        runOnUiThread(() -> webView.evaluateJavascript(
                "window.onMirrorNativeGoogleAuthResult && window.onMirrorNativeGoogleAuthResult(" + JSONObject.quote(payload.toString()) + ")",
                null));
    }

    private void notifyGoogleAuthError(String message) {
        runOnUiThread(() -> webView.evaluateJavascript(
                "window.onMirrorNativeGoogleAuthError && window.onMirrorNativeGoogleAuthError(" + JSONObject.quote(message) + ")",
                null));
    }

    private boolean googleTokenReady() {
        return googleAccessToken != null && !googleAccessToken.isBlank() && System.currentTimeMillis() < googleAccessTokenExpiryMs;
    }

    private boolean allowedGoogleApiUrl(String rawUrl) {
        try {
            URL url = new URL(rawUrl);
            return "https".equalsIgnoreCase(url.getProtocol()) && GOOGLE_API_HOSTS.contains(url.getHost());
        } catch (Exception ignored) {
            return false;
        }
    }

    private byte[] readAll(InputStream stream) throws Exception {
        if (stream == null) return new byte[0];
        try (InputStream input = stream; ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[8192];
            int read;
            while ((read = input.read(buffer)) >= 0) output.write(buffer, 0, read);
            return output.toByteArray();
        }
    }

    private void googleApiRequest(String requestId, String method, String rawUrl, byte[] body, String contentType) {
        new Thread(() -> {
            int status = 0;
            String responseText = "";
            try {
                if (!googleTokenReady()) throw new IllegalStateException("Google access needs to be refreshed. Tap Continue with Google again.");
                if (!allowedGoogleApiUrl(rawUrl)) throw new SecurityException("MIRA blocked a Google request to an unapproved host.");
                String normalizedMethod = method == null ? "GET" : method.trim().toUpperCase();
                if (!Set.of("GET", "POST", "PUT", "PATCH", "DELETE").contains(normalizedMethod)) {
                    throw new SecurityException("Unsupported Google API method.");
                }
                HttpURLConnection connection = (HttpURLConnection) new URL(rawUrl).openConnection();
                connection.setConnectTimeout(20000);
                connection.setReadTimeout(120000);
                connection.setRequestMethod(normalizedMethod);
                connection.setRequestProperty("Authorization", "Bearer " + googleAccessToken);
                connection.setRequestProperty("Accept", "application/json");
                if (body != null && body.length > 0) {
                    connection.setDoOutput(true);
                    connection.setRequestProperty("Content-Type", contentType == null || contentType.isBlank() ? "application/json; charset=utf-8" : contentType);
                    connection.setFixedLengthStreamingMode(body.length);
                    try (OutputStream output = connection.getOutputStream()) { output.write(body); }
                }
                status = connection.getResponseCode();
                byte[] response = readAll(status >= 400 ? connection.getErrorStream() : connection.getInputStream());
                responseText = new String(response, StandardCharsets.UTF_8);
                connection.disconnect();
            } catch (Exception error) {
                status = status == 0 ? 599 : status;
                responseText = "{\"error\":\"" + String.valueOf(error.getMessage()).replace("\\", "\\\\").replace("\"", "\\\"") + "\"}";
            }
            final int finalStatus = status;
            final String finalResponse = responseText;
            runOnUiThread(() -> webView.evaluateJavascript(
                    "window.onMirrorNativeGoogleApiResponse && window.onMirrorNativeGoogleApiResponse(" +
                            JSONObject.quote(requestId) + "," + finalStatus + "," + JSONObject.quote(finalResponse) + ")",
                    null));
        }, "mira-google-api").start();
    }

    private void startNfcReader() {
        if (nfcAdapter == null) {
            notifyNfcError("This Android device does not expose an NFC adapter.");
            return;
        }
        if (!nfcAdapter.isEnabled()) {
            notifyNfcError("NFC is turned off. Enable NFC in Android settings and try again.");
            return;
        }
        int flags = NfcAdapter.FLAG_READER_NFC_A
                | NfcAdapter.FLAG_READER_NFC_B
                | NfcAdapter.FLAG_READER_NFC_F
                | NfcAdapter.FLAG_READER_NFC_V;
        nfcReaderActive = true;
        nfcAdapter.enableReaderMode(this, this::onNfcTagDiscovered, flags, null);
    }

    private void disableNfcReader() {
        if (nfcAdapter != null && nfcReaderActive) {
            nfcAdapter.disableReaderMode(this);
            nfcReaderActive = false;
        }
    }

    private void onNfcTagDiscovered(Tag tag) {
        String uid = bytesToHex(tag.getId());
        JSONArray technologies = new JSONArray();
        for (String tech : tag.getTechList()) technologies.put(tech);
        runOnUiThread(() -> {
            disableNfcReader();
            String script = "window.onMirrorNativeNfcResult(" + JSONObject.quote(uid) + "," + technologies + ")";
            webView.evaluateJavascript(script, null);
        });
    }

    private void notifyNfcError(String message) {
        runOnUiThread(() -> webView.evaluateJavascript(
                "window.onMirrorNativeNfcError && window.onMirrorNativeNfcError(" + JSONObject.quote(message) + ")",
                null));
    }

    private boolean hasBlePermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            return checkSelfPermission(Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED
                    && checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED;
        }
        return checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED;
    }

    private void requestBlePermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            requestPermissions(new String[]{Manifest.permission.BLUETOOTH_SCAN, Manifest.permission.BLUETOOTH_CONNECT}, BLE_PERMISSION_REQUEST);
        } else {
            requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION}, BLE_PERMISSION_REQUEST);
        }
    }

    private void startBleScan() {
        if (!hasBlePermissions()) {
            requestBlePermissions();
            notifyBleError("Android opened the Nearby devices permission prompt. Allow it, then tap Scan BLE tags again.");
            return;
        }
        BluetoothManager manager = (BluetoothManager) getSystemService(Context.BLUETOOTH_SERVICE);
        BluetoothAdapter adapter = manager == null ? null : manager.getAdapter();
        if (adapter == null) {
            notifyBleError("This Android device does not expose Bluetooth Low Energy.");
            return;
        }
        if (!adapter.isEnabled()) {
            notifyBleError("Bluetooth is turned off. Enable Bluetooth and try again.");
            return;
        }
        stopBleScan();
        bleScanner = adapter.getBluetoothLeScanner();
        if (bleScanner == null) {
            notifyBleError("Bluetooth LE scanning is unavailable on this device.");
            return;
        }
        bleScanActive = true;
        bleScanner.startScan(bleScanCallback);
        mainHandler.postDelayed(this::stopBleScan, 10000L);
        notifyBleState("Scanning for BLE advertisements for 10 seconds. Signal strength is proximity evidence, not distance.");
    }

    private void stopBleScan() {
        mainHandler.removeCallbacksAndMessages(null);
        if (bleScanner != null && bleScanActive && hasBlePermissions()) {
            try { bleScanner.stopScan(bleScanCallback); } catch (SecurityException ignored) { }
        }
        if (bleScanActive) notifyBleState("BLE scan complete.");
        bleScanActive = false;
        bleScanner = null;
    }

    private final ScanCallback bleScanCallback = new ScanCallback() {
        @Override
        public void onScanResult(int callbackType, ScanResult result) {
            publishBleResult(result);
        }

        @Override
        public void onBatchScanResults(List<ScanResult> results) {
            for (ScanResult result : results) publishBleResult(result);
        }

        @Override
        public void onScanFailed(int errorCode) {
            bleScanActive = false;
            notifyBleError("Bluetooth LE scan failed with Android error " + errorCode + ".");
        }
    };

    private void publishBleResult(ScanResult result) {
        try {
            JSONObject payload = new JSONObject();
            payload.put("address", result.getDevice().getAddress());
            payload.put("rssi", result.getRssi());
            ScanRecord record = result.getScanRecord();
            if (record != null) {
                String name = record.getDeviceName();
                if (name != null && !name.isBlank()) payload.put("name", name);
                JSONArray serviceUuids = new JSONArray();
                List<ParcelUuid> uuids = record.getServiceUuids();
                if (uuids != null) for (ParcelUuid uuid : uuids) serviceUuids.put(uuid.toString());
                payload.put("service_uuids", serviceUuids);

                JSONArray manufacturers = new JSONArray();
                SparseArray<byte[]> manufacturerData = record.getManufacturerSpecificData();
                for (int i = 0; i < manufacturerData.size(); i++) {
                    int manufacturerId = manufacturerData.keyAt(i);
                    String data = bytesToHex(manufacturerData.valueAt(i));
                    JSONObject item = new JSONObject();
                    item.put("manufacturer_id", manufacturerId);
                    item.put("data_hex", data);
                    manufacturers.put(item);
                }
                payload.put("manufacturer_data", manufacturers);

                JSONArray serviceData = new JSONArray();
                for (Map.Entry<ParcelUuid, byte[]> entry : record.getServiceData().entrySet()) {
                    JSONObject item = new JSONObject();
                    item.put("service_uuid", entry.getKey().toString());
                    item.put("data_hex", bytesToHex(entry.getValue()));
                    serviceData.put(item);
                }
                payload.put("service_data", serviceData);

                String stableHint = null;
                if (serviceData.length() > 0) {
                    JSONObject first = serviceData.getJSONObject(0);
                    stableHint = "service:" + first.getString("service_uuid") + ":" + first.getString("data_hex");
                } else if (manufacturers.length() > 0) {
                    JSONObject first = manufacturers.getJSONObject(0);
                    stableHint = "manufacturer:" + first.getInt("manufacturer_id") + ":" + first.getString("data_hex");
                }
                if (stableHint != null) payload.put("stable_identifier_hint", stableHint);
            }
            String script = "window.onMirrorNativeBleObservation && window.onMirrorNativeBleObservation(" + JSONObject.quote(payload.toString()) + ")";
            runOnUiThread(() -> webView.evaluateJavascript(script, null));
        } catch (Exception ignored) {
            // One malformed advertisement must not terminate the scan.
        }
    }

    private void notifyBleState(String message) {
        runOnUiThread(() -> webView.evaluateJavascript(
                "window.onMirrorNativeBleState && window.onMirrorNativeBleState(" + JSONObject.quote(message) + ")",
                null));
    }

    private void notifyBleError(String message) {
        runOnUiThread(() -> webView.evaluateJavascript(
                "window.onMirrorNativeBleError && window.onMirrorNativeBleError(" + JSONObject.quote(message) + ")",
                null));
    }

    private static String bytesToHex(byte[] value) {
        if (value == null || value.length == 0) return "";
        StringBuilder out = new StringBuilder(value.length * 2);
        for (byte item : value) out.append(String.format("%02X", item));
        return out.toString();
    }

    private final class NativeBridge {
        @JavascriptInterface
        public void speak(String text) {
            runOnUiThread(() -> SpeechService.start(MainActivity.this, "manual-" + System.currentTimeMillis(), "MIRA reminder", text));
        }

        @JavascriptInterface
        public void scheduleReminder(String reminderId, long fireAtEpochMs, String title, String speechText) {
            runOnUiThread(() -> ReminderScheduler.schedule(MainActivity.this, reminderId, fireAtEpochMs, title, speechText));
        }

        @JavascriptInterface
        public void openExternal(String url) {
            runOnUiThread(() -> startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))));
        }

        @JavascriptInterface
        public void setWallDisplay(boolean enabled) {
            runOnUiThread(() -> MainActivity.this.setWallDisplay(enabled));
        }

        @JavascriptInterface
        public void authorizeGoogle(String capabilities) {
            runOnUiThread(() -> MainActivity.this.authorizeGoogle(capabilities));
        }

        @JavascriptInterface
        public boolean hasGoogleAuthorization() {
            return googleTokenReady();
        }

        @JavascriptInterface
        public String googleGrantedScopes() {
            return new JSONArray(googleGrantedScopes).toString();
        }

        @JavascriptInterface
        public void googleApiRequest(String requestId, String method, String url, String body, String contentType) {
            byte[] bytes = body == null ? new byte[0] : body.getBytes(StandardCharsets.UTF_8);
            MainActivity.this.googleApiRequest(requestId, method, url, bytes, contentType);
        }

        @JavascriptInterface
        public void googleApiRequestBase64(String requestId, String method, String url, String bodyBase64, String contentType) {
            byte[] bytes;
            try { bytes = Base64.decode(bodyBase64 == null ? "" : bodyBase64, Base64.DEFAULT); }
            catch (Exception error) { bytes = new byte[0]; }
            MainActivity.this.googleApiRequest(requestId, method, url, bytes, contentType);
        }

        @JavascriptInterface
        public void scanBarcode() {
            runOnUiThread(() -> {
                GmsBarcodeScanner scanner = GmsBarcodeScanning.getClient(MainActivity.this);
                Task<Barcode> task = scanner.startScan();
                task.addOnSuccessListener(barcode -> {
                    String value = barcode.getRawValue();
                    if (value == null) value = "";
                    String format = barcodeFormat(barcode.getFormat());
                    String script = "window.onMirrorNativeScanResult(" + JSONObject.quote(value) + "," + JSONObject.quote(format) + ")";
                    webView.evaluateJavascript(script, null);
                });
            });
        }

        @JavascriptInterface
        public void scanNfcTag() {
            runOnUiThread(MainActivity.this::startNfcReader);
        }

        @JavascriptInterface
        public boolean hasNfc() {
            return nfcAdapter != null;
        }

        @JavascriptInterface
        public void scanBleTags() {
            runOnUiThread(MainActivity.this::startBleScan);
        }

        @JavascriptInterface
        public void stopBleTags() {
            runOnUiThread(MainActivity.this::stopBleScan);
        }
    }

    private static String barcodeFormat(int format) {
        return switch (format) {
            case Barcode.FORMAT_QR_CODE -> "QR_CODE";
            case Barcode.FORMAT_UPC_A -> "UPC_A";
            case Barcode.FORMAT_EAN_13 -> "EAN_13";
            case Barcode.FORMAT_EAN_8 -> "EAN_8";
            case Barcode.FORMAT_CODE_128 -> "CODE_128";
            default -> "UNKNOWN";
        };
    }

    @SuppressWarnings("unused")
    private String exactAlarmStatus() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.S) return "exact";
        AlarmManager manager = (AlarmManager) getSystemService(Context.ALARM_SERVICE);
        return manager != null && manager.canScheduleExactAlarms() ? "exact" : "inexact-fallback";
    }
}
