# -*- coding: utf-8 -*-
"""Download numpy & zstandard wheels via urllib then report paths."""
import urllib.request, re, sys, os

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
OUT = os.path.dirname(os.path.abspath(__file__))

def get_index(pkg):
    url = 'https://repo.huaweicloud.com/repository/pypi/simple/%s/' % pkg
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode('utf-8', errors='ignore')

def pick_wheel(html, tag):
    links = re.findall(r'href="([^"]+)"', html)
    cands = [l for l in links if l.endswith('.whl') or '#sha256=' in l]
    matches = [l for l in cands if tag in l]
    return matches[-1] if matches else None

def download(url, name):
    dst = os.path.join(OUT, name)
    if os.path.exists(dst) and os.path.getsize(dst) > 1000000:
        print('already have', name)
        return dst
    req = urllib.request.Request(url, headers=UA)
    print('downloading', name, '...')
    with urllib.request.urlopen(req, timeout=300) as r, open(dst + '.part', 'wb') as f:
        total = 0
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
            total += len(chunk)
            print('  %d bytes' % total, flush=True)
    os.replace(dst + '.part', dst)
    print('saved', dst)
    return dst

def main():
    tag = 'cp313-cp313-win_amd64'
    for pkg in ['numpy', 'zstandard']:
        print('=== %s ===' % pkg)
        html = get_index(pkg)
        link = pick_wheel(html, tag)
        if not link:
            print('NO WHEEL for', pkg)
            sys.exit(1)
        if not link.startswith('http'):
            from urllib.parse import urljoin
            link = urljoin('https://repo.huaweicloud.com/repository/pypi/simple/%s/' % pkg, link)
        name = re.search(r'([^/]+\.whl)', link).group(1)
        download(link, name)

if __name__ == '__main__':
    main()
