#!/usr/bin/env python
"""Upload FurryChatApp project to server via SFTP and run build."""

import paramiko
import os
import stat

HOST = "38.92.8.234"
PORT = 2222
USER = "root"
PASSWORD = "Luotianyu6.."
LOCAL_DIR = r"C:\Users\Administrator\WorkBuddy\2026-05-22-21-43-05\FurryChatApp"
REMOTE_DIR = "/opt/FurryChatApp"

# Files/dirs to skip during upload (node_modules is huge, will be reinstalled on server)
SKIP = {"node_modules", ".git", "__pycache__", "android", "ios"}

def upload_dir(sftp, local, remote):
    """Recursively upload a directory, skipping SKIP entries."""
    for item in os.listdir(local):
        if item in SKIP:
            print(f"   ⏭️  跳过: {item}")
            continue
        local_path = os.path.join(local, item)
        remote_path = f"{remote}/{item}"
        if os.path.isdir(local_path):
            try:
                sftp.stat(remote_path)
            except FileNotFoundError:
                sftp.mkdir(remote_path)
                print(f"   📁 创建目录: {remote_path}")
            upload_dir(sftp, local_path, remote_path)
        else:
            sftp.put(local_path, remote_path)
            print(f"   📄 上传: {item}")

try:
    # Connect
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=15)
    sftp = client.open_sftp()
    
    # Create remote dir
    try:
        sftp.stat(REMOTE_DIR)
    except FileNotFoundError:
        sftp.mkdir(REMOTE_DIR)
        print(f"✅ 创建远程目录: {REMOTE_DIR}")
    
    # Upload project files
    print("\n📤 上传项目文件...")
    upload_dir(sftp, LOCAL_DIR, REMOTE_DIR)
    print("✅ 上传完成")
    
    sftp.close()
    
    # Make build script executable and run it
    print("\n🔧 开始构建...")
    stdin, stdout, stderr = client.exec_command(
        f"chmod +x {REMOTE_DIR}/server_build.sh && cd {REMOTE_DIR} && bash server_build.sh 2>&1",
        timeout=600  # 10 minutes timeout
    )
    
    # Stream output
    import select
    while True:
        if stdout.channel.exit_status_ready():
            break
        if stdout.channel.recv_ready():
            data = stdout.channel.recv(4096).decode('utf-8', errors='replace')
            print(data, end='', flush=True)
    
    # Get remaining output
    remaining = stdout.read().decode('utf-8', errors='replace')
    if remaining:
        print(remaining)
    
    err = stderr.read().decode('utf-8', errors='replace')
    if err:
        print(f"\n⚠️ 错误输出:\n{err}")
    
    print("\n✅ 构建过程完成")
    client.close()

except Exception as e:
    print(f"❌ 错误: {e}")
