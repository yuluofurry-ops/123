#!/usr/bin/env python
"""Push FurryChatApp project to GitHub repo using GitHub API."""

import os
import json
import base64
import mimetypes

# Try to install PyGithub
import subprocess
import sys

try:
    from github import Github, GithubException
except ImportError:
    print("正在安装 PyGithub...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyGithub", "-q"])
    from github import Github, GithubException

REPO_NAME = "yuluofurry-ops/123"
LOCAL_DIR = r"C:\Users\Administrator\WorkBuddy\2026-05-22-21-43-05\FurryChatApp"
SKIP_DIRS = {"node_modules", ".git", "__pycache__", "android", "ios"}
SKIP_EXTS = {".apk", ".ipa", ".pyc", ".pyo"}

# We need a GitHub token. Let's try to use the GitHub CLI token or ask
# Actually, let's try the environment variable
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

# The user needs to provide a GitHub token
# For now, let's create a script that collects everything and pushes via API

def get_all_files(base_dir):
    """Get all files to upload with their relative paths."""
    files = []
    for root, dirs, filenames in os.walk(base_dir):
        # Skip dirs
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for filename in filenames:
            filepath = os.path.join(root, filename)
            relpath = os.path.relpath(filepath, base_dir).replace("\\", "/")
            
            ext = os.path.splitext(filename)[1].lower()
            if ext in SKIP_EXTS:
                continue
            
            files.append((relpath, filepath))
    
    return files

# First, show what will be uploaded without a token
print("=" * 60)
print("福瑞酒馆 App → GitHub 上传准备")
print("=" * 60)

files = get_all_files(LOCAL_DIR)
print(f"\n📦 共 {len(files)} 个文件待上传：")

total_size = 0
for relpath, filepath in files:
    size = os.path.getsize(filepath)
    total_size += size
    print(f"   {relpath} ({size/1024:.1f} KB)")

print(f"\n📊 总大小: {total_size/1024/1024:.1f} MB")

if TOKEN:
    print("\n🔑 GitHub Token 已找到，开始上传...")
    g = Github(TOKEN)
    try:
        repo = g.get_repo(REPO_NAME)
        print(f"✅ 已连接到仓库: {repo.full_name}")
        
        # Upload files one by one
        for i, (relpath, filepath) in enumerate(files):
            with open(filepath, 'rb') as f:
                content = f.read()
            
            # Try to create file
            try:
                # Check if file exists
                try:
                    existing = repo.get_contents(relpath)
                    # Update existing file
                    repo.update_file(relpath, f"更新 {relpath}", content, existing.sha)
                    print(f"   [{i+1}/{len(files)}] ✅ 更新: {relpath}")
                except GithubException as e:
                    if e.status == 404:
                        # Create new file
                        repo.create_file(relpath, f"添加 {relpath}", content)
                        print(f"   [{i+1}/{len(files)}] ✅ 添加: {relpath}")
                    else:
                        raise
            except Exception as e:
                print(f"   [{i+1}/{len(files)}] ❌ 失败: {relpath} - {e}")
        
        print(f"\n🎉 全部上传完成!")
        print(f"   仓库: https://github.com/{REPO_NAME}")
        print(f"   去 Actions 触发构建: https://github.com/{REPO_NAME}/actions")
        
    except Exception as e:
        print(f"\n❌ 上传失败: {e}")
        print("\n你可能需要:")
        print("1. 确认仓库名是否正确")
        print("2. 确认 Token 有 repo 权限")
        print("3. 或者设置 GITHUB_TOKEN 环境变量")
else:
    print("\n⚠️ 未找到 GitHub Token (GITHUB_TOKEN)")
    print("\n需要你先生成一个 Token 才能推送:")
    print("1. 打开 https://github.com/settings/tokens")
    print("2. 点 Generate new token → Generate new token (classic)")
    print("3. 勾选 repo 权限")
    print("4. 生成后复制 Token")
    print("5. 然后把 Token 告诉我，我帮你推")

# Also save the file list to a JSON for verification
with open(os.path.join(LOCAL_DIR, "file_manifest.json"), "w", encoding='utf-8') as f:
    json.dump([{"path": rp, "size": os.path.getsize(fp)} for rp, fp in files], f, ensure_ascii=False, indent=2)
