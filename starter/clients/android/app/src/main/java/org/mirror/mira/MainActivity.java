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
import android.content.pm.PackageManager;
import android.net.Uri;
import android.nfc.NfcAdapter;
import android.nfc.Tag;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.ParcelUuid;
import android.util.SparseArray;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.webkit.WebViewAssetLoader;

import com.google.android.gms.tasks.Task;
import com.google.mlkit.vision.barcode.common.Barcode;
import com.google.mlkit.vision.codescanner.GmsBarcodeScanner;
import com.google.mlkit.vision.codescanner.GmsBarcodeScanning;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.List;
import java.util.Map;

public final class MainActivity extends Activity {
    private static final int FILE_CHOOSER_REQUEST = 2001;
    private static final int BLE_PERMISSION_REQUEST = 2002;
    private WebView webView;
    private ValueCallback<Uri[]> fileCallback;
    private NfcAdapter nfcAdapter;
    private boolean nfcReaderActive = false;
    private BluetoothLeScanner bleScanner;
    private boolean bleScanActive = false;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestNotificationPermissionIfNeeded();
        nfcAdapter = NfcAdapter.getDefaultAdapter(this);

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
