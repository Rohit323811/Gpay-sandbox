"""Add classes.dex and assets/gpay.html into the linked base APK."""
import zipfile, shutil, os, sys

base = "gpay-apk/build/manual/base.apk"
out  = "gpay-apk/build/manual/unsigned.apk"
dex  = "gpay-apk/build/manual/dex/classes.dex"
html = "gpay-apk/src/main/assets/gpay.html"

shutil.copyfile(base, out)
with zipfile.ZipFile(base, "r") as zin, zipfile.ZipFile(out, "a", zipfile.ZIP_DEFLATED) as zout:
    # resources.arsc must be uncompressed & 4-byte aligned for API 30+, handled by zipalign next
    with open(dex, "rb") as f:
        zout.writestr(zipfile.ZipInfo("classes.dex"), f.read(), zipfile.ZIP_DEFLATED)
    with open(html, "rb") as f:
        zout.writestr(zipfile.ZipInfo("assets/gpay.html"), f.read(), zipfile.ZIP_DEFLATED)
print("wrote", out, os.path.getsize(out), "bytes")
