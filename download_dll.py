import urllib.request
import hashlib
import os
import sys
import ssl

# 下载配置：从最新版本开始尝试
dlls = [
    {
        "name": "wx_key-4.1.4.11.dll",
        "url": "https://github.com/ycccccccy/wx_key/releases/download/dlls/wx_key-4.1.4.11.dll",
        "sha256": "7ff5502f267214ea35bbff3e5b5b463be2abc79c9c4f9b00cd55be03c9bbfa43",
        "size": 41472,
    },
    {
        "name": "wx_key-4.1.4.10.dll",
        "url": "https://github.com/ycccccccy/wx_key/releases/download/dlls/wx_key-4.1.4.10.dll",
        "sha256": "467529f58d9855a15f54f56af61875f4d30c4efa8e808aeb61241432773fcc5c",
        "size": 41472,
    },
    {
        "name": "wx_key-4.1.2.18.dll",
        "url": "https://github.com/ycccccccy/wx_key/releases/download/dlls/wx_key-4.1.2.18.dll",
        "sha256": "d8d5f2c7d5c1aff5cbfc50dd6fde3e36842cb467d30a7f93b50253ce9560fce8",
        "size": 41472,
    },
]

mirrors = [
    "",
    "https://ghproxy.net/",
    "https://gh-proxy.com/",
    "https://github.moeyy.xyz/",
    "https://hub.gitmirror.com/",
]

# 创建 SSL 上下文，忽略证书验证
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gopath", "bin", "wx_key.dll")
print(f"目标路径: {dest}")

last_err = None
for dll in dlls:
    print(f"\n=== 尝试下载 {dll['name']} (期望 {dll['size']} bytes) ===")
    for j, mirror in enumerate(mirrors):
        url = dll["url"] if mirror == "" else mirror + dll["url"]
        mirror_name = "直连" if mirror == "" else mirror
        print(f"[{dll['name']}] 镜像 {j+1}: {mirror_name}")

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
                if resp.status != 200:
                    print(f"  HTTP {resp.status}")
                    last_err = f"HTTP {resp.status}"
                    continue

                data = resp.read()
                if len(data) < 1000:
                    print(f"  文件太小: {len(data)} bytes")
                    last_err = "file too small"
                    continue

                # 保存文件
                with open(dest, "wb") as f:
                    f.write(data)

                # 计算 SHA256
                hash_str = hashlib.sha256(data).hexdigest()
                print(f"  下载成功: {len(data)} bytes")
                print(f"  实际 SHA256: {hash_str}")
                print(f"  期望 SHA256: {dll['sha256']}")
                if hash_str == dll["sha256"]:
                    print("  SHA256 验证通过!")
                else:
                    print("  SHA256 不匹配，但文件已保存")
                print(f"\n成功下载 {dll['name']}，保存为 wx_key.dll")
                sys.exit(0)

        except Exception as e:
            print(f"  失败: {e}")
            last_err = str(e)
            continue

print(f"\n所有下载尝试失败，最后错误: {last_err}")
sys.exit(1)
