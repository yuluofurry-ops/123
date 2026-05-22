#!/usr/bin/env python
"""Rebuild APK with new icon, name, and fullscreen."""

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

# Clean previous build
echo "=== 清理旧构建 ==="
./gradlew clean 2>&1 | tail -3

# Build
echo ""
echo "=== 开始构建 APK ==="
JAVA_HOME=$JAVA_HOME ANDROID_HOME=$ANDROID_HOME ./gradlew assembleDebug 2>&1 | tail -15

# Check result
echo ""
echo "=== 结果 ==="
APK="/opt/FurryChatApp/android/app/build/outputs/apk/debug/app-debug.apk"
if [ -f "$APK" ]; then
    echo "✅ BUILD SUCCESSFUL"
    echo "APK: $APK"
    ls -lh "$APK"
    cp "$APK" "/opt/FurryChat.apk"
    echo "已复制到 /opt/FurryChat.apk"
else
    echo "❌ BUILD FAILED"
fi
"""

stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("STDERR:", err[:500])

client.close()
