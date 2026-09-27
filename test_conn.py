import socket
import sys

# 测试连接到 GitHub CDN IP 地址
ips = ['185.199.111.133', '185.199.109.133', '185.199.110.133']
for ip in ips:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    try:
        s.connect((ip, 443))
        print(f"连接成功 {ip}:443")
        s.close()
    except Exception as e:
        print(f"连接失败 {ip}:443 - {e}")
        s.close()

# 测试连接到 api.github.com
print("\n测试 api.github.com:")
try:
    ip = socket.gethostbyname('api.github.com')
    print(f"  IP: {ip}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect((ip, 443))
    print(f"  连接成功")
    s.close()
except Exception as e:
    print(f"  连接失败: {e}")
