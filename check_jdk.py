#!/usr/bin/env python
"""Check JDK versions available on the server and fix the build."""

import paramiko
import time

HOST = "38.92.8.234"
PORT = 2222
USER = "root"
PASSWORD = "Luotianyu6.."

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=15)

# Check available JDK packages
stdin, stdout, _ = client.exec_command("apt-cache search openjdk | grep -E '^openjdk-' | sort", timeout=15)
print("=== 可用 JDK 包 ===")
print(stdout.read().decode().strip())

# Check what's installed
stdin, stdout, _ = client.exec_command("ls /usr/lib/jvm/", timeout=10)
print("=== 已安装 JVM ===")
print(stdout.read().decode().strip())

# Check current JAVA_HOME alternatives
stdin, stdout, _ = client.exec_command("update-alternatives --list java 2>/dev/null", timeout=10)
print("=== Java alternatives ===")
print(stdout.read().decode().strip())

# Check Gradle Java version requirement by looking at the build files
stdin, stdout, _ = client.exec_command("head -10 /opt/FurryChatApp/android/gradle/wrapper/gradle-wrapper.properties", timeout=10)
print("=== Gradle Wrapper 属性 ===")
print(stdout.read().decode().strip())

# Check Android Gradle Plugin version
stdin, stdout, _ = client.exec_command("grep -E 'agp|android.*plugin|compileSdk|javaVersion|jvmTarget' /opt/FurryChatApp/android/variables.gradle 2>/dev/null || cat /opt/FurryChatApp/android/build.gradle 2>/dev/null || cat /opt/FurryChatApp/android/app/build.gradle 2>/dev/null | head -40", timeout=10)
print("=== Gradle 构建配置 ===")
print(stdout.read().decode().strip())

client.close()
