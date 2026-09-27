import urllib.request
import urllib.error
import hashlib
import os
import sys
import ssl
import socket

# 设置超时
socket.setdefaulttimeout(30)  # 30秒超时

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gopath", "bin", "wx_key.dll")
print(f"目标路径: {dest}")

# GitHub API asset URL
api_url = "https://api.github.com/repos/ycccccccy/wx_key/releases/assets/311294102"
print(f"API URL: {api_url}")

try:
    # 创建请求，设置 Accept 头为 application/octet-stream
    req = urllib.request.Request(api_url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/octet-stream",
    })
    print("发送请求到 GitHub API...")
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        print(f"HTTP 状态: {resp.status}")
        print(f"Content-Type: {resp.headers.get('Content-Type')}")
        print(f"Content-Length: {resp.headers.get('Content-Length')}")
        print(f"最终 URL: {resp.url[:100]}...")

        data = resp.read()
        print(f"读取到 {len(data)} bytes")

        if len(data) < 1000:
            print(f"文件太小")
            print(f"内容: {data[:500]}")
            sys.exit(1)

        # 检查是否是 JSON 错误响应
        content_type = resp.headers.get('Content-Type', '')
        if 'json' in content_type.lower() or 'text' in content_type.lower():
            print(f"收到文本响应而非二进制文件:")
            print(f"{data[:500].decode('utf-8', errors='replace')}")
            sys.exit(1)

        # 保存文件
        with open(dest, "wb") as f:
            f.write(data)

        # 计算 SHA256
        hash_str = hashlib.sha256(data).hexdigest()
        print(f"下载成功: {len(data)} bytes")
        print(f"实际 SHA256: {hash_str}")
        print(f"期望 SHA256: 7ff5502f267214ea35bbff3e5b5b463be2abc79c9c4f9b00cd55be03c9bbfa43")
        if hash_str == "7ff5502f267214ea35bbff3e5b5b463be2abc79c9c4f9b00cd55be03c9bbfa43":
            print("SHA256 验证通过!")
        else:
            print("SHA256 不匹配，但文件已保存")
        print(f"\n成功下载 wx_key-4.1.4.11.dll，保存为 wx_key.dll")

except urllib.error.HTTPError as e:
    print(f"HTTP 错误: {e.code} {e.reason}")
    print(f"Headers: {dict(e.headers)}")
    try:
        body = e.read().decode('utf-8', errors='replace')
        print(f"响应: {body[:500]}")
    except:
        pass
except urllib.error.URLError as e:
    print(f"URL 错误: {e}")
    if hasattr(e, 'reason'):
        print(f"原因: {e.reason}")
except socket.timeout:
    print("连接超时！可能 release-assets.githubusercontent.com 被阻止")
except Exception as e:
    print(f"失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
