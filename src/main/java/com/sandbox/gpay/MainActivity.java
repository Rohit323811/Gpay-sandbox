package com.sandbox.gpay;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.provider.ContactsContract;
import android.view.View;
import android.view.Window;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    private WebView webView;
    private PermissionRequest pendingCameraRequest;

    private static final int REQ_PERMS = 1001;
    private static final int REQ_CAMERA = 1002;
    private static final int BG = Color.parseColor("#121212");

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Window w = getWindow();
        w.setStatusBarColor(BG);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            w.setNavigationBarColor(BG);
        }

        webView = new WebView(this);
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setCacheMode(WebSettings.LOAD_NO_CACHE);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        webView.setBackgroundColor(BG);
        webView.setWebViewClient(new WebViewClient());
        // The QR scanner asks the page for getUserMedia(); the WebView only hands the
        // camera over when the app itself holds the CAMERA permission.
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        boolean wantsVideo = false;
                        for (String res : request.getResources()) {
                            if (PermissionRequest.RESOURCE_VIDEO_CAPTURE.equals(res)) {
                                wantsVideo = true;
                            }
                        }
                        if (!wantsVideo) {
                            request.deny();
                        } else if (hasPermission(Manifest.permission.CAMERA)) {
                            request.grant(request.getResources());
                        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                            pendingCameraRequest = request;
                            requestPermissions(new String[] { Manifest.permission.CAMERA }, REQ_CAMERA);
                        } else {
                            request.deny();
                        }
                    }
                });
            }
        });
        // Lets the page pull the phone's own contacts (real names for real numbers).
        webView.addJavascriptInterface(new ContactsBridge(this), "AndroidBridge");
        setContentView(webView);
        webView.loadUrl("file:///android_asset/gpay.html");
        // Dark app chrome: keep system-bar icons light on the dark status bar.
        webView.setSystemUiVisibility(View.SYSTEM_UI_FLAG_LAYOUT_STABLE);

        String[] wanted = { Manifest.permission.READ_CONTACTS };
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M
                && checkSelfPermission(Manifest.permission.READ_CONTACTS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(wanted, REQ_PERMS);
        }
    }

    private boolean hasPermission(String p) {
        return Build.VERSION.SDK_INT < Build.VERSION_CODES.M
                || checkSelfPermission(p) == PackageManager.PERMISSION_GRANTED;
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQ_PERMS && webView != null) {
            // If contacts were granted, let the page re-pull the contact list.
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                webView.evaluateJavascript("syncContacts();", null);
            }
        }
        if (requestCode == REQ_CAMERA) {
            PermissionRequest pending = pendingCameraRequest;
            pendingCameraRequest = null;
            if (pending != null) {
                if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED
                        && hasPermission(Manifest.permission.CAMERA)) {
                    pending.grant(pending.getResources());
                } else {
                    pending.deny();
                }
            }
        }
        // The scanner asks for the camera again each time it opens and silently
        // falls back to the simulated feed when the permission was declined.
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    /** Exposed to JS as AndroidBridge.contacts() -> JSON array of {name, num}. */
    static class ContactsBridge {
        private final Context context;

        ContactsBridge(Context c) {
            context = c;
        }

        @JavascriptInterface
        public String contacts() {
            Context c = context;
            if (c == null) return "[]";
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M
                    && c.checkSelfPermission(Manifest.permission.READ_CONTACTS)
                        != PackageManager.PERMISSION_GRANTED) {
                return "[]";
            }
            StringBuilder sb = new StringBuilder("[");
            Cursor cr = null;
            int count = 0;
            try {
                cr = c.getContentResolver().query(
                        ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                        new String[] {
                                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME_PRIMARY,
                                ContactsContract.CommonDataKinds.Phone.NUMBER },
                        ContactsContract.CommonDataKinds.Phone.HAS_PHONE_NUMBER + "!=0 AND "
                                + ContactsContract.CommonDataKinds.Phone.NUMBER + " IS NOT NULL",
                        null,
                        ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME_PRIMARY + " COLLATE NOCASE ASC");
                if (cr != null) {
                    while (cr.moveToNext() && count < 300) {
                        String nm = cr.getString(0);
                        String ph = cr.getString(1);
                        if (nm == null || ph == null) continue;
                        // Normalise to the 10-digit Indian mobile form the sandbox uses.
                        String digits = ph.replaceAll("[^0-9]", "");
                        if (digits.length() >= 11 && digits.startsWith("91")) digits = digits.substring(2);
                        if (digits.startsWith("0")) digits = digits.substring(1);
                        if (digits.length() > 10) digits = digits.substring(digits.length() - 10);
                        if (digits.length() < 10) continue;
                        sb.append(count == 0 ? "" : ",");
                        sb.append("{\"name\":").append(json(nm)).append(",\"num\":").append(json(digits)).append("}");
                        count++;
                    }
                }
            } catch (Throwable ignored) {
                // No contacts access — the page keeps its demo directory.
            } finally {
                if (cr != null) cr.close();
            }
            return sb.append("]").toString();
        }

        private static String json(String raw) {
            String s = raw.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ");
            return "\"" + s + "\"";
        }
    }
}
