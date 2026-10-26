#!/usr/bin/env bash
# Re-provision the manual APK build toolchain expected by build_apk.py:
#   /c/Projects/tooling/jdk17/jdk-17.0.20.1+1
#   /c/Projects/tooling/android/build-tools/34.0.0
#   /c/Projects/tooling/android/platforms/android-34/android.jar
set -euo pipefail

TOOLING="/c/Projects/tooling"
mkdir -p "$TOOLING"

echo "=== 1/4 JDK 17 ==="
if [ ! -x "$TOOLING/jdk17/jdk-17.0.20.1+1/bin/javac.exe" ]; then
  mkdir -p "$TOOLING/jdk17"
  curl -fL --retry 3 --connect-timeout 30 -o "$TOOLING/jdk17.zip" \
    "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse"
  cd "$TOOLING/jdk17"
  unzip -q -o "$TOOLING/jdk17.zip"
  rm -f "$TOOLING/jdk17.zip"
  # normalize folder name to the one build_apk.py expects
  inner="$(find "$TOOLING/jdk17" -maxdepth 1 -mindepth 1 -type d -name 'jdk-*' | head -1)"
  if [ -n "$inner" ] && [ "$inner" != "$TOOLING/jdk17/jdk-17.0.20.1+1" ]; then
    mv "$inner" "$TOOLING/jdk17/jdk-17.0.20.1+1"
  fi
fi
"$TOOLING/jdk17/jdk-17.0.20.1+1/bin/java.exe" -version

echo "=== 2/4 cmdline-tools ==="
export JAVA_HOME="$TOOLING/jdk17/jdk-17.0.20.1+1"
SDK="$TOOLING/android"
mkdir -p "$SDK/cmdline-tools"
if [ ! -x "$SDK/cmdline-tools/latest/bin/sdkmanager.bat" ]; then
  curl -fL --retry 3 --connect-timeout 30 -o "$TOOLING/cmdline-tools.zip" \
    "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
  cd "$SDK/cmdline-tools"
  unzip -q -o "$TOOLING/cmdline-tools.zip"
  rm -f "$TOOLING/cmdline-tools.zip"
  rm -rf "$SDK/cmdline-tools/latest"
  mv "$SDK/cmdline-tools/cmdline-tools" "$SDK/cmdline-tools/latest"
fi

echo "=== 3/4 sdk packages ==="
yes | "$SDK/cmdline-tools/latest/bin/sdkmanager.bat" --sdk_root="$SDK" --licenses >/dev/null 2>&1 || true
"$SDK/cmdline-tools/latest/bin/sdkmanager.bat" --sdk_root="$SDK" \
  "platforms;android-34" "build-tools;34.0.0" "platform-tools" 2>&1 | tail -5

echo "=== 4/4 verify ==="
ls -l "$SDK/build-tools/34.0.0/aapt2.exe" "$SDK/platforms/android-34/android.jar"
echo "TOOLING READY"
