#!/usr/bin/env python
"""Update Android project: fullscreen, app name, capacitor config."""

import paramiko

HOST = "38.92.8.234"
PORT = 2222
USER = "root"
PASSWORD = "Luotianyu6.."

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=15)

# Read current files
def read_file(path):
    stdin, stdout, _ = client.exec_command(f"cat {path}", timeout=10)
    return stdout.read().decode()

def write_file(path, content):
    # Use heredoc to avoid quoting issues
    import base64
    encoded = base64.b64encode(content.encode('utf-8')).decode()
    cmd = f"echo '{encoded}' | base64 -d > {path}"
    stdin, stdout, _ = client.exec_command(cmd, timeout=10)
    return stdout.read().decode()

# 1. Update capacitor.config.json - app name + fullscreen
print("📝 更新 Capacitor 配置...")
cap_config = read_file("/opt/FurryChatApp/capacitor.config.json")
import json
config = json.loads(cap_config)
config["appName"] = "福瑞酒馆"
config["plugins"]["SplashScreen"] = {
    "launchShowDuration": 2000,
    "backgroundColor": "#1a1a2e",
    "androidSplashResourceName": "splash",
    "androidScaleType": "CENTER_CROP",
    "showSpinner": False,
    "splashFullScreen": True,
    "splashImmersive": True
}
write_file("/opt/FurryChatApp/capacitor.config.json", json.dumps(config, ensure_ascii=False, indent=2))
print("  ✅ appName → 福瑞酒馆")

# 2. Update strings.xml - app name
print("\n📝 更新 strings.xml...")
strings = read_file("/opt/FurryChatApp/android/app/src/main/res/values/strings.xml")
strings = strings.replace("FurryChat", "福瑞酒馆")
# Also update app_name
import re
strings = re.sub(r'<string name="app_name">.*?</string>', '<string name="app_name">福瑞酒馆</string>', strings)
write_file("/opt/FurryChatApp/android/app/src/main/res/values/strings.xml", strings)
print("  ✅ app_name → 福瑞酒馆")

# 3. Update AndroidManifest.xml for fullscreen + immersive
print("\n📝 更新 AndroidManifest.xml...")
manifest = read_file("/opt/FurryChatApp/android/app/src/main/AndroidManifest.xml")

# Add fullscreen theme
manifest = manifest.replace(
    'android:theme="@style/AppTheme"',
    'android:theme="@style/AppTheme.Fullscreen"'
)

# Add FLAG_FULLSCREEN and FLAG_LAYOUT_IN_SCREEN via activity attributes
# Also add android:windowSoftInputMode for keyboard handling
if "android:windowSoftInputMode" not in manifest:
    manifest = manifest.replace(
        'android:theme="@style/AppTheme.Fullscreen"',
        'android:theme="@style/AppTheme.Fullscreen"\n            android:windowSoftInputMode="adjustResize"'
    )

write_file("/opt/FurryChatApp/android/app/src/main/AndroidManifest.xml", manifest)
print("  ✅ Fullscreen theme applied")

# 4. Update styles.xml for fullscreen
print("\n📝 更新 styles.xml...")
styles = read_file("/opt/FurryChatApp/android/app/src/main/res/values/styles.xml")

fullscreen_style = '''
    <style name="AppTheme.Fullscreen" parent="Theme.AppCompat.NoActionBar">
        <item name="android:windowFullscreen">true</item>
        <item name="android:windowNoTitle">true</item>
        <item name="windowNoTitle">true</item>
        <item name="android:windowContentOverlay">@null</item>
    </style>
'''
# Only add if not already present
if "AppTheme.Fullscreen" not in styles:
    styles = styles.replace("</resources>", f"{fullscreen_style}\n</resources>")
    write_file("/opt/FurryChatApp/android/app/src/main/res/values/styles.xml", styles)
    print("  ✅ Fullscreen style added")
else:
    print("  ⏭️  Fullscreen style already exists")

# 5. Update app/build.gradle - set status bar / navigation bar colors
print("\n📝 更新 build.gradle...")
build_gradle = read_file("/opt/FurryChatApp/android/app/build.gradle")

# Add immersive mode configuration
if "activity.requestedOrientation" not in build_gradle:
    print("  ⏭️  Immersive mode will be handled by Capacitor plugin")

# 6. Sync Capacitor config
print("\n📝 同步 Capacitor 配置...")
stdin, stdout, _ = client.exec_command(
    "cd /opt/FurryChatApp && export PATH=$PATH:$(pwd)/node_modules/.bin && npx cap sync android 2>&1 | tail -5",
    timeout=30
)
print(stdout.read().decode())

print("\n✅ 所有配置更新完成！")
client.close()
