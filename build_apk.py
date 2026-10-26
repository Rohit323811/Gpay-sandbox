"""One-shot manual APK build: aapt2 compile/link -> javac -> d8 -> package -> zipalign -> apksign.

Usage: python build_apk.py
Requires tooling/ JDK17+android SDK (already provisioned in this workspace).
"""
import subprocess, os, sys, shutil, zipfile, platform

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # thread workspace root
PROJ = os.path.join(ROOT, "gpay-apk")
BT   = os.path.join(ROOT, "tooling", "android", "build-tools", "34.0.0")
PLAT_JAR = os.path.join(ROOT, "tooling", "android", "platforms", "android-34", "android.jar")
JAVA = os.path.join(ROOT, "tooling", "jdk17", "jdk-17.0.20.1+1")
BUILD = os.path.join(PROJ, "build", "manual")

def run(cmd, **kw):
    print(">>", " ".join(os.path.basename(c) if os.sep not in c else c for c in cmd[:4]), "...")
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print(r.stdout); print(r.stderr)
        sys.exit(f"step failed: {cmd[0]} (exit {r.returncode})")
    if r.stdout.strip(): print(r.stdout.strip()[:600])

def main():
    env = dict(os.environ, JAVA_HOME=JAVA)
    os.makedirs(os.path.join(BUILD, "gen"), exist_ok=True)
    os.makedirs(os.path.join(BUILD, "obj"), exist_ok=True)
    os.makedirs(os.path.join(BUILD, "dex"), exist_ok=True)

    aapt2 = os.path.join(BT, "aapt2.exe")
    run([aapt2, "compile", "--dir", os.path.join(PROJ, "src", "main", "res"),
         "-o", os.path.join(BUILD, "res.zip")])
    run([aapt2, "link", "-o", os.path.join(BUILD, "base.apk"),
         "-I", PLAT_JAR,
         "--manifest", os.path.join(PROJ, "src", "main", "AndroidManifest.xml"),
         "-R", os.path.join(BUILD, "res.zip"),
         "--java", os.path.join(BUILD, "gen"),
         "--auto-add-overlay"])

    rjava = os.path.join(BUILD, "gen", "com", "sandbox", "gpay", "R.java")
    srcs = [rjava, os.path.join(PROJ, "src", "main", "java", "com", "sandbox", "gpay", "MainActivity.java")]
    run([os.path.join(JAVA, "bin", "javac.exe"), "--release", "8",
         "-cp", PLAT_JAR, "-d", os.path.join(BUILD, "obj")] + srcs)

    classes = []
    for dirpath, _, files in os.walk(os.path.join(BUILD, "obj")):
        classes += [os.path.join(dirpath, f) for f in files if f.endswith(".class")]
    run([os.path.join(JAVA, "bin", "java.exe"), "-cp", os.path.join(BT, "lib", "d8.jar"),
         "com.android.tools.r8.D8", "--release", "--lib", PLAT_JAR,
         "--output", os.path.join(BUILD, "dex")] + classes)

    unsigned = os.path.join(BUILD, "unsigned.apk")
    shutil.copyfile(os.path.join(BUILD, "base.apk"), unsigned)
    with zipfile.ZipFile(os.path.join(BUILD, "base.apk")) as zin, \
         zipfile.ZipFile(unsigned, "a", zipfile.ZIP_DEFLATED) as zout:
        zout.writestr(zipfile.ZipInfo("classes.dex"),
                      open(os.path.join(BUILD, "dex", "classes.dex"), "rb").read(),
                      zipfile.ZIP_DEFLATED)
        asset_dir = os.path.join(PROJ, "src", "main", "assets")
        for ad, _dirs, files in os.walk(asset_dir):
            for fn in files:
                rel = os.path.relpath(os.path.join(ad, fn), asset_dir).replace(os.sep, "/")
                zout.writestr(zipfile.ZipInfo("assets/" + rel),
                              open(os.path.join(ad, fn), "rb").read(),
                              zipfile.ZIP_DEFLATED)

    aligned = os.path.join(BUILD, "aligned.apk")
    run([os.path.join(BT, "zipalign.exe"), "-f", "-p", "4", unsigned, aligned])

    ks = os.path.join(BUILD, "debug.keystore")
    if not os.path.exists(ks):
        run([os.path.join(JAVA, "bin", "keytool.exe"), "-genkeypair", "-v",
             "-keystore", ks, "-storepass", "android", "-keypass", "android",
             "-alias", "androiddebugkey", "-keyalg", "RSA", "-keysize", "2048",
             "-validity", "10000", "-dname", "CN=Android Debug,O=Android,C=US"],
            env=env)

    final = os.path.join(BUILD, "gpay-sandbox.apk")
    if os.path.exists(final): os.remove(final)
    run([os.path.join(BT, "apksigner.bat"), "sign",
         "--ks", ks, "--ks-pass", "pass:android", "--key-pass", "pass:android",
         "--out", final, aligned], env=env)
    run([os.path.join(BT, "apksigner.bat"), "verify", final], env=env)
    print("\nBUILD OK ->", final, os.path.getsize(final), "bytes")

if __name__ == "__main__":
    main()
