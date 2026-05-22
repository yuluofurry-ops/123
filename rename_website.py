#!/usr/bin/env python
"""Search and replace '冒险酒馆' with '福瑞酒馆' on the website."""

import paramiko

HOST = "38.92.8.234"
PORT = 2222
USER = "root"
PASSWORD = "Luotianyu6.."

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=15)

# Search for matches
cmd_search = "grep -rn '冒险酒馆' /www/wwwroot/ai.furrychat.online/ 2>/dev/null | head -30"
stdin, stdout, _ = client.exec_command(cmd_search, timeout=15)
result = stdout.read().decode().strip()

if result:
    print("找到以下包含「冒险酒馆」的行：\n")
    print(result)
    
    # Replace in all files
    cmd_replace = "sed -i 's/冒险酒馆/福瑞酒馆/g' /www/wwwroot/ai.furrychat.online/*.html /www/wwwroot/ai.furrychat.online/*.php /www/wwwroot/ai.furrychat.online/*.js 2>/dev/null"
    stdin, stdout, _ = client.exec_command(cmd_replace, timeout=15)
    
    # Also search in subdirectories
    cmd_replace_recursive = "grep -rl '冒险酒馆' /www/wwwroot/ai.furrychat.online/ 2>/dev/null | while read f; do sed -i 's/冒险酒馆/福瑞酒馆/g' \"$f\"; done"
    stdin, stdout, _ = client.exec_command(cmd_replace_recursive, timeout=15)
    print(stdout.read().decode())
    
    # Verify no remaining matches
    cmd_verify = "grep -rn '冒险酒馆' /www/wwwroot/ai.furrychat.online/ 2>/dev/null"
    stdin, stdout, _ = client.exec_command(cmd_verify, timeout=15)
    remaining = stdout.read().decode().strip()
    
    # Verify new text
    cmd_verify_new = "grep -rn '福瑞酒馆' /www/wwwroot/ai.furrychat.online/ 2>/dev/null | head -10"
    stdin, stdout, _ = client.exec_command(cmd_verify_new, timeout=15)
    new_matches = stdout.read().decode().strip()
    
    print("\n" + "=" * 60)
    if remaining:
        print(f"⚠️ 仍有 {remaining.count(chr(10))+1} 处未替换：")
        print(remaining)
    else:
        print("✅ 全部替换完成，没有残留的「冒险酒馆」")
    
    print("\n已替换为「福瑞酒馆」的位置：")
    print(new_matches if new_matches else "（未找到新匹配，可能文件名不在列表中）")

else:
    print("在 /www/wwwroot/ai.furrychat.online/ 下未找到「冒险酒馆」")
    
    # Also check the main index
    for path in ["/www/wwwroot/ai.furrychat.online/index.html", "/www/wwwroot/default/index.html"]:
        cmd_check = f"cat {path} 2>/dev/null | head -20"
        stdin, stdout, _ = client.exec_command(cmd_check, timeout=10)
        content = stdout.read().decode()[:200]
        if content:
            print(f"\n{path} 前200字符:")
            print(content)

client.close()
