#!/bin/bash
# ============================================
# FurryChat App - Server Build Script
# 在服务器上安装构建环境并打包 APK
# ============================================

set -e

APP_DIR="/opt/FurryChatApp"
echo "=============================="
echo "FurryChat App 构建脚本"
echo "目标: 打包 APK"
echo "=============================="

# 1. 安装 JDK 17
echo ""
echo "[1/7] 安装 JDK 17..."
if ! command -v java &> /dev/null; then
    apt update -qq && apt install -y -qq openjdk-17-jdk-headless 2>&1 | tail -3
else
    echo "   JDK 已安装: $(java -version 2>&1 | head -1)"
fi

# 2. 安装 Android SDK 命令行工具
echo ""
echo "[2/7] 安装 Android SDK..."
SDK_DIR="/opt/android-sdk"
if [ ! -d "$SDK_DIR/cmdline-tools" ]; then
    mkdir -p "$SDK_DIR"
    cd "$SDK_DIR"
    # 下载命令行工具
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O cmdline-tools.zip
    unzip -q cmdline-tools.zip
    rm cmdline-tools.zip
    # 按 Google 要求的目录结构
    mkdir -p latest
    mv cmdline-tools/* latest/
    mv latest cmdline-tools/
    echo "   Android SDK 命令行工具已安装"
else
    echo "   Android SDK 已存在"
fi

# 设置环境变量
export ANDROID_HOME="$SDK_DIR"
export ANDROID_SDK_ROOT="$SDK_DIR"
export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools"
export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"

# 3. 安装所需 SDK 组件
echo ""
echo "[3/7] 安装 Android SDK 组件..."
yes | sdkmanager --sdk_root="$ANDROID_HOME" "platforms;android-34" "build-tools;34.0.0" 2>&1 | tail -5

# 4. 安装 Node.js 22 + npm 依赖
echo ""
echo "[4/7] 安装 Node.js 22..."
cd "$APP_DIR"
if ! command -v node &> /dev/null || [ "$(node -v | cut -d'.' -f1 | tr -d 'v')" -lt 22 ]; then
    echo "   安装 Node.js 22.x..."
    # 使用 NodeSource 源
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - 2>&1 | tail -3
    apt install -y -qq nodejs 2>&1 | tail -3
    echo "   Node.js $(node -v) 已安装"
else
    echo "   Node.js $(node -v) 已满足要求"
fi

echo ""
echo "[5/7] 安装 npm 依赖..."
npm install 2>&1 | tail -5

echo ""
echo "[6/7] 配置 Capacitor Android 平台..."
export PATH="$PATH:$(pwd)/node_modules/.bin"

# 添加 Android 平台
npx cap add android 2>&1 | tail -5

# 如果有 server.url 配置，同步
npx cap sync android 2>&1 | tail -5

# 7. 构建 APK
echo ""
echo "[7/7] 构建 APK..."
cd "$APP_DIR/android"
if [ -f "./gradlew" ]; then
    chmod +x ./gradlew
    # 构建 debug APK
    ./gradlew assembleDebug 2>&1 | tail -10
    
    APK_PATH="$APP_DIR/android/app/build/outputs/apk/debug/app-debug.apk"
    if [ -f "$APK_PATH" ]; then
        echo ""
        echo "=============================="
        echo "✅ 构建成功!"
        echo "APK 位置: $APK_PATH"
        echo "大小: $(ls -lh $APK_PATH | awk '{print $5}')"
        echo "=============================="
        # 复制到方便取的位置
        cp "$APK_PATH" "/opt/FurryChat.apk"
        echo "已复制到: /opt/FurryChat.apk"
    else
        echo "❌ APK 未生成，检查错误"
        exit 1
    fi
else
    echo "❌ gradlew 未找到"
    exit 1
fi
