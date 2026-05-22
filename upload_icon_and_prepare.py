#!/usr/bin/env python
"""Upload icon to server and generate Android icons there."""

import paramiko
import os

HOST = "38.92.8.234"
PORT = 2222
USER = "root"
PASSWORD = "Luotianyu6.."
LOCAL_ICON = r"C:\Users\Administrator\Downloads\Image_1779022239292_699.png"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=15)
sftp = client.open_sftp()

# Upload icon
sftp.put(LOCAL_ICON, "/opt/FurryChatApp/icon_source.png")
print("✅ 图标已上传")
sftp.close()

# Install ImageMagick if needed, then generate icons
cmd = """
set -e

# Install ImageMagick if needed
if ! command -v convert &> /dev/null; then
    echo "Installing ImageMagick..."
    apt install -y -qq imagemagick 2>&1 | tail -1
fi

ICON_DIR="/opt/FurryChatApp/android/app/src/main/res"
SOURCE="/opt/FurryChatApp/icon_source.png"

# Android icon sizes
declare -A SIZES
SIZES[mipmap-xxxhdpi]=192
SIZES[mipmap-xxhdpi]=144
SIZES[mipmap-xhdpi]=96
SIZES[mipmap-hdpi]=72
SIZES[mipmap-mdpi]=48

echo "Generating icons..."
for DIR in "${!SIZES[@]}"; do
    SIZE=${SIZES[$DIR]}
    TARGET_DIR="$ICON_DIR/$DIR"
    mkdir -p "$TARGET_DIR"
    
    # Generate legacy icon
    convert "$SOURCE" -resize ${SIZE}x${SIZE} "$TARGET_DIR/ic_launcher.png"
    convert "$SOURCE" -resize ${SIZE}x${SIZE} "$TARGET_DIR/ic_launcher_foreground.png"
    convert -size ${SIZE}x${SIZE} xc:white "$TARGET_DIR/ic_launcher_background.png"
    
    echo "  ✅ $DIR (${SIZE}px)"
done

# Also generate round icon
for DIR in "${!SIZES[@]}"; do
    SIZE=${SIZES[$DIR]}
    TARGET_DIR="$ICON_DIR/$DIR"
    # Round icon - same as regular for now
    cp "$TARGET_DIR/ic_launcher.png" "$TARGET_DIR/ic_launcher_round.png"
done

echo ""
echo "✅ All icons generated"

# Update AndroidManifest.xml for fullscreen
MANIFEST="/opt/FurryChatApp/android/app/src/main/AndroidManifest.xml"
echo ""
echo "Updating AndroidManifest.xml for fullscreen..."

# Check if already has fullscreen theme
if grep -q "Fullscreen" "$MANIFEST"; then
    echo "  Fullscreen already enabled"
else
    # Add fullscreen theme to the activity
    sed -i 's|android:theme="@style/AppTheme"|android:theme="@style/AppTheme.Fullscreen"|g' "$MANIFEST"
    
    # Add the fullscreen style
    STYLES="/opt/FurryChatApp/android/app/src/main/res/values/styles.xml"
    if [ -f "$STYLES" ]; then
        sed -i 's|</resources>|<style name="AppTheme.Fullscreen" parent="Theme.AppCompat.NoActionBar"><item name="android:windowFullscreen">true</item></style>\n</resources>|g' "$STYLES"
        echo "  ✅ Fullscreen style added"
    fi
    echo "  ✅ Fullscreen enabled"
fi

echo ""
echo "Done! Ready to build."
"""

stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
print(stdout.read().decode())
err = stderr.read().decode()
if err and "warning" not in err.lower():
    print("STDERR:", err[:500])

client.close()
