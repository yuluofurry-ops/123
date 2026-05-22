#!/usr/bin/env python
"""Download and install JDK 21 on the server, then build."""

import paramiko
import time

HOST = "38.92.8.234"
PORT = 2222
USER = "root"
PASSWORD = "Luotianyu6.."

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=15)

print("=== 步骤1: 尝试下载 JDK 21 (Adoptium) ===")

# Try downloading JDK 21 using curl
cmd_install_jdk21 = """
set -e
cd /opt

# Try to download JDK 21
if [ ! -f /opt/jdk21.tar.gz ]; then
    echo "Downloading JDK 21..."
    curl -sL --connect-timeout 20 --max-time 120 \
        "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.6%2B7/OpenJDK21U-jdk_x64_linux_hotspot_21.0.6_7.tar.gz" \
        -o /opt/jdk21.tar.gz && \
    echo "Downloaded OK, size: $(ls -lh /opt/jdk21.tar.gz | awk '{print $5}')" || \
    {
        echo "GitHub failed, trying API..."
        curl -sL --connect-timeout 20 --max-time 120 \
            "https://api.adoptium.net/v3/binary/version/jdk-21.0.6%2B7/linux/x64/jdk/hotspot/normal/eclipse" \
            -o /opt/jdk21.tar.gz && \
        echo "Downloaded OK from API, size: $(ls -lh /opt/jdk21.tar.gz | awk '{print $5}')" || \
        {
            echo "All sources failed"
            exit 1
        }
    }
fi

if [ -f /opt/jdk21.tar.gz ]; then
    echo "Extracting JDK 21..."
    tar xzf /opt/jdk21.tar.gz -C /usr/lib/jvm/
    JDK_DIR=$(ls -d /usr/lib/jvm/jdk-21* 2>/dev/null | head -1)
    if [ -n "$JDK_DIR" ]; then
        echo "JDK 21 extracted to: $JDK_DIR"
        # Register with update-alternatives
        update-alternatives --install /usr/bin/java java "$JDK_DIR/bin/java" 2100
        update-alternatives --set java "$JDK_DIR/bin/java"
        echo "Java version: $(java -version 2>&1 | head -1)"
    else
        echo "Could not find JDK 21 directory"
        ls /usr/lib/jvm/
        exit 1
    fi
fi
"""

stdin, stdout, stderr = client.exec_command(cmd_install_jdk21, timeout=180)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("STDERR:", err[:500])

print("\n=== 步骤2: 检查 Java 版本 ===")
stdin, stdout, _ = client.exec_command("java -version 2>&1; ls /usr/lib/jvm/", timeout=10)
print(stdout.read().decode())

print("\n=== 步骤3: 构建 APK ===")
# Set JAVA_HOME for the newly installed JDK and build
cmd_build = """
export JAVA_HOME=$(ls -d /usr/lib/jvm/jdk-21* /usr/lib/jvm/java-21* 2>/dev/null | head -1)
if [ -z "$JAVA_HOME" ]; then
    export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
fi
echo "Using JAVA_HOME=$JAVA_HOME"
cd /opt/FurryChatApp/android
JAVA_HOME=$JAVA_HOME ./gradlew assembleDebug 2>&1 | tail -20
"""

stdin, stdout, stderr = client.exec_command(cmd_build, timeout=600)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("STDERR:", err[:500])

print("\n=== 步骤4: 检查 APK ===")
stdin, stdout, _ = client.exec_command("ls -lh /opt/FurryChatApp/android/app/build/outputs/apk/debug/app-debug.apk 2>/dev/null || echo 'APK not found'", timeout=10)
print(stdout.read().decode())

client.close()
