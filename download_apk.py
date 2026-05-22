#!/usr/bin/env python
"""Download the built APK from server."""

import paramiko
import os

HOST = "38.92.8.234"
PORT = 2222
USER = "root"
PASSWORD = "Luotianyu6.."
REMOTE_APK = "/opt/FurryChatApp/android/app/build/outputs/apk/debug/app-debug.apk"
LOCAL_APK = r"C:\Users\Administrator\WorkBuddy\2026-05-22-21-43-05\FurryChatApp\FurryChat.apk"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=15)

sftp = client.open_sftp()
sftp.get(REMOTE_APK, LOCAL_APK)
sftp.close()
client.close()

size_mb = os.path.getsize(LOCAL_APK) / (1024 * 1024)
print(f"✅ APK 已下载到本地")
print(f"   路径: {LOCAL_APK}")
print(f"   大小: {size_mb:.1f} MB")
