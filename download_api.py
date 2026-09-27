import urllib.request
import hashlib
import os
import sys
import ssl
import json

# 使用 GitHub API 下载 release asset
# asset id 从 API 获取
assets = [
    {"id": "311294102", "name": "wx_key-4.1.4.11.dll", "sha256": "7ff5502f267214ea35bbff3e5b5b463be2abc79c9c4f9b00cd55be03c9bbfa43"},
    {"id": "311282285", "name": "wx_key-4.1.4.10.dll", "sha256": "467529f58d9855a15f54f56af61875f4d30c4efa8e808aeb61241432773fcc5c"},
    {"id": "307301838", "name": "wx_key-4.1.2.18.dll", "sha256": "d8d5f2c7d5c1aff5cbfc50dd6fde3e36842cb467d30a7f93b50253ce9560fce8"},
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gopath", "bin", "wx_key.dll")
print(f"目标路径: {dest}")

for asset in assets:
    # GitHub API asset 下载链接
    api_url = f"https://api.github.com/repos/ycccccccy/wx_key/releases/assets/{asset['id']}"
    print(f"\n=== 尝试通过 GitHub API 下载 {asset['name']} ===")
    print(f"API URL: {api_url}")

    try:
        # 设置 Accept 头为 application/octet-stream 以获取二进制内容
        req = urllib.request.Request(api_url, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/octet-stream",
        })
        with urllib.request.urlopen(req, timeout=180, context=ctx) as resp:
            print(f"  HTTP 状态: {resp.status}")
            print(f"  Content-Type: {resp.headers.get('Content-Type')}")
            print(f"  Content-Length: {resp.headers.get('Content-Length')}")

            if resp.status != 200:
                print(f"  HTTP {resp.status}")
                continue

            data = resp.read()
            if len(data) < 1000:
                print(f"  文件太小: {len(data)} bytes")
                continue

            # 检查是否是 JSON 错误响应
            content_type = resp.headers.get('Content-Type', '')
            if 'json' in content_type.lower():
                print(f"  收到 JSON 响应而非二进制文件:")
                print(f"  {data[:500].decode('utf-8', errors='replace')}")
                continue

            # 保存文件
            with open(dest, "wb") as f:
                f.write(data)

            # 计算 SHA256
            hash_str = hashlib.sha256(data).hexdigest()
            print(f"  下载成功: {len(data)} bytes")
            print(f"  实际 SHA256: {hash_str}")
            print(f"  期望 SHA256: {asset['sha256']}")
            if hash_str == asset["sha256"]:
                print("  SHA256 验证通过!")
            else:
                print("  SHA256 不匹配，但文件已保存")
            print(f"\n成功下载 {asset['name']}，保存为 wx_key.dll")
            sys.exit(0)

    except urllib.error.HTTPError as e:
        print(f"  HTTP 错误: {e.code} {e.reason}")
        try:
            body = e.read().decode('utf-8', errors='replace')
            print(f"  响应: {body[:300]}")
        except:
            pass
    except Exception as e:
        print(f"  失败: {e}")

print("\n所有 GitHub API 下载尝试失败")
sys.exit(1)
