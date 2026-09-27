"""
Phase 1: Scan WeChat process memory for V4 key pattern candidates.
Fast - just collects candidates, saves to candidates.json.
Entropy filtering reduces the number of candidates for Phase 2 validation.
"""
import ctypes
import ctypes.wintypes as wt
import struct, os, sys, json, time, functools
from collections import Counter

print = functools.partial(print, flush=True)

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_DIR = os.path.join(_SCRIPT_DIR, "wechat-decrypt-main")
if not os.path.exists(os.path.join(_CONFIG_DIR, "config.json")):
    _CONFIG_DIR = _SCRIPT_DIR

PAGE_SZ = 4096
SALT_SZ = 16

kernel32 = ctypes.windll.kernel32
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
MEM_COMMIT = 0x1000
MEM_PRIVATE = 0x20000
PAGE_READWRITE = 0x04

_cfg = {}
with open(os.path.join(_CONFIG_DIR, "config.json"), encoding="utf-8") as _f:
    _cfg = json.load(_f)
DB_DIR = _cfg["db_dir"]
CANDIDATES_FILE = os.path.join(_CONFIG_DIR, "candidates.json")


class MBI(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_uint64), ("AllocationBase", ctypes.c_uint64),
        ("AllocationProtect", wt.DWORD), ("_pad1", wt.DWORD),
        ("RegionSize", ctypes.c_uint64), ("State", wt.DWORD),
        ("Protect", wt.DWORD), ("Type", wt.DWORD), ("_pad2", wt.DWORD),
    ]


def get_pid():
    import subprocess
    r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Weixin.exe", "/FO", "CSV", "/NH"],
                       capture_output=True, text=True)
    best = (0, 0)
    for line in r.stdout.strip().split('\n'):
        if not line.strip():
            continue
        p = line.strip('"').split('","')
        if len(p) >= 5:
            pid = int(p[1])
            mem = int(p[4].replace(',', '').replace(' K', '').strip() or '0')
            if mem > best[1]:
                best = (pid, mem)
    if not best[0]:
        print("[ERROR] Weixin.exe 未运行")
        sys.exit(1)
    print(f"[+] Weixin.exe PID={best[0]} ({best[1] // 1024}MB)")
    return best[0]


def read_mem(h, addr, sz):
    buf = ctypes.create_string_buffer(sz)
    n = ctypes.c_size_t(0)
    if kernel32.ReadProcessMemory(h, ctypes.c_uint64(addr), buf, sz, ctypes.byref(n)):
        return buf.raw[:n.value]
    return None


def enum_v4_regions(h):
    regs = []
    addr = 0
    mbi = MBI()
    while addr < 0x7FFFFFFFFFFF:
        if kernel32.VirtualQueryEx(h, ctypes.c_uint64(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0:
            break
        if (mbi.State == MEM_COMMIT and
                (mbi.Protect & PAGE_READWRITE) != 0 and
                mbi.Type == MEM_PRIVATE and
                mbi.RegionSize >= 1024 * 1024):
            regs.append((mbi.BaseAddress, mbi.RegionSize))
        nxt = mbi.BaseAddress + mbi.RegionSize
        if nxt <= addr:
            break
        addr = nxt
    return regs


def has_high_entropy(data):
    """Check if 32-byte candidate looks like a real key (high entropy)."""
    if len(data) < 32:
        return False
    d = data[:32]
    # Skip all zeros or all same byte
    if d == b'\x00' * 32 or len(set(d)) == 1:
        return False
    # Count zero bytes - real key has few
    zero_count = d.count(0)
    if zero_count > 8:
        return False
    # Count unique bytes - real key has many
    unique = len(set(d))
    if unique < 16:
        return False
    # Skip if upper 24 bytes are all zero (looks like a pointer)
    if d[8:] == b'\x00' * 24:
        return False
    if d[16:] == b'\x00' * 16:
        return False
    return True


def main():
    print("=" * 60)
    print("  Phase 1: Scan for V4 key candidates")
    print("=" * 60)

    # Collect DB files
    db_files = []
    for root, dirs, files in os.walk(DB_DIR):
        for f in files:
            if f.endswith('.db') and not f.endswith('-wal') and not f.endswith('-shm'):
                path = os.path.join(root, f)
                rel = os.path.relpath(path, DB_DIR)
                sz = os.path.getsize(path)
                if sz < PAGE_SZ:
                    continue
                with open(path, 'rb') as fh:
                    page1 = fh.read(PAGE_SZ)
                db_files.append({"rel": rel, "path": path, "sz": sz, "salt": page1[:SALT_SZ].hex()})
    print(f"找到 {len(db_files)} 个数据库文件")

    pid = get_pid()
    h = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
    if not h:
        print("[ERROR] 无法打开进程")
        sys.exit(1)

    regions = enum_v4_regions(h)
    total_mb = sum(s for _, s in regions) / 1024 / 1024
    print(f"[+] V4 内存区域: {len(regions)} 个, {total_mb:.0f}MB")

    key_pattern = bytes([
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x2F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ])
    ptr_size = 8

    candidates = []
    seen_addrs = set()
    total_patterns = 0
    t0 = time.time()

    for reg_idx, (base, size) in enumerate(regions):
        chunk_size = min(size, 256 * 1024 * 1024)
        offset = 0
        while offset < size:
            read_size = min(chunk_size, size - offset)
            overlap = len(key_pattern) + ptr_size
            actual_read = min(read_size + overlap, size - offset)

            data = read_mem(h, base + offset, actual_read)
            if not data:
                offset += read_size
                continue

            search_end = len(data)
            while True:
                idx = data.rfind(key_pattern, 0, search_end)
                if idx == -1 or idx < ptr_size:
                    break
                total_patterns += 1

                ptr_val = struct.unpack_from('<Q', data, idx - ptr_size)[0]
                search_end = idx

                if ptr_val <= 0x10000 or ptr_val >= 0x7FFFFFFFFFFF:
                    continue
                if ptr_val in seen_addrs:
                    continue
                seen_addrs.add(ptr_val)

                key_data = read_mem(h, ptr_val, 0x20)
                if not key_data or len(key_data) < 0x20:
                    continue

                # Entropy filter
                if not has_high_entropy(key_data):
                    continue

                candidates.append({
                    "ptr": ptr_val,
                    "key_hex": key_data.hex()
                })

            offset += read_size

        elapsed = time.time() - t0
        if (reg_idx + 1) % 10 == 0 or reg_idx == len(regions) - 1:
            progress = sum(s for _, s in regions[:reg_idx + 1]) / sum(s for _, s in regions) * 100
            print(f"  [{progress:.0f}%] {total_patterns} patterns, {len(candidates)} high-entropy candidates, {elapsed:.0f}s")

    elapsed = time.time() - t0
    print(f"\n扫描完成: {elapsed:.0f}s")
    print(f"  总模式匹配: {total_patterns}")
    print(f"  高熵候选: {len(candidates)}")

    # Save candidates
    with open(CANDIDATES_FILE, 'w') as f:
        json.dump({"candidates": candidates, "db_files": db_files}, f, indent=2)
    print(f"候选保存到: {CANDIDATES_FILE}")

    kernel32.CloseHandle(h)


if __name__ == '__main__':
    main()
