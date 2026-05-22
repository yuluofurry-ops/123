#!/usr/bin/env python
"""Build APK with correct env vars."""

import paramiko

HOST = "38.92.8.234"
PORT = 2222
USER = "root"
PASSWORD = "Luotianyu6.."

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=15)

cmd = """
export JAVA_HOME=/usr/lib/jvm/jdk-21.0.6+7
export ANDROID_HOME=/opt/android-sdk
export ANDROID_SDK_ROOT=/opt/android-sdk

cd /opt/FurryChatApp/android

# Create local.properties
echo "sdk.dir=$ANDROID_HOME" > local.properties

# Build
echo "JAVA_HOME=$JAVA_HOME"
echo "ANDROID_HOME=$ANDROID_HOME"
echo "Starting gradle build..."

JAVA_HOME=$JAVA_HOME ANDROID_HOME=$ANDROID_HOME ./gradlew assembleDebug 2>&1 | tail -30

echo ""
echo "=== APK 检查 ==="
ls -lh /opt/FurryChatApp/android/app/build/outputs/apk/debug/app-debug.apk 2>/dev/null || echo "APK not found"
"""

stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("STDERR:", err[:500])

client.close()
