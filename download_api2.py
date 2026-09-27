import urllib.request
import urllib.error
import http.client
import hashlib
import os
import sys
import ssl
import json

# 使用 GitHub API 下载 release asset
# 需要设置 Accept: application/octet-stream 头
assets = [
    {"id": "311294102", "name": "wx_key-4.1.4.11.dll", "sha256": "7ff5502f267214ea35bbff3e5b5b463be2abc79c9c4f9b00cd55be03c9bbfa43"},
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gopath", "bin", "wx_key.dll")
print(f"目标路径: {dest}")

for asset in assets:
    api_url = f"https://api.github.com/repos/ycccccccy/wx_key/releases/assets/{asset['id']}"
    print(f"\n=== 尝试通过 GitHub API 下载 {asset['name']} ===")
    print(f"API URL: {api_url}")

    # 创建不自动跟随重定向的 opener
    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            print(f"  重定向到: {newurl}")
            print(f"  状态码: {code}")
            # 手动跟随重定向
            new_req = urllib.request.Request(newurl, headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/octet-stream",
            })
            return new_req

    opener = urllib.request.build_opener(NoRedirectHandler, urllib.request.HTTPSHandler(context=ctx))

    try:
        req = urllib.request.Request(api_url, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/octet-stream",  # 重要：请求二进制内容
        })
        print("  发送请求...")
        with opener.open(req, timeout=60) as resp:
            print(f"  HTTP 状态: {resp.status}")
            print(f"  Content-Type: {resp.headers.get('Content-Type')}")
            print(f"  Content-Length: {resp.headers.get('Content-Length')}")
            print(f"  最终 URL: {resp.url}")

            data = resp.read()
            print(f"  读取到 {len(data)} bytes")

            if len(data) < 1000:
                print(f"  文件太小")
                # 打印内容看看是什么
                print(f"  内容: {data[:500]}")
                continue

            # 检查是否是 JSON 错误响应
            content_type = resp.headers.get('Content-Type', '')
            if 'json' in content_type.lower() or 'text' in content_type.lower():
                print(f"  收到文本响应而非二进制文件:")
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
        print(f"  Headers: {dict(e.headers)}")
        try:
            body = e.read().decode('utf-8', errors='replace')
            print(f"  响应: {body[:500]}")
        except:
            pass
    except urllib.error.URLError as e:
        print(f"  URL 错误: {e}")
        if hasattr(e, 'reason'):
            print(f"  原因: {e.reason}")
    except Exception as e:
        print(f"  失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

print("\n所有 GitHub API 下载尝试失败")
sys.exit(1)
