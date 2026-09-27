"""
Extract WeChat 4.x database encryption key using chatlog's V4 pattern-based approach.

Scans WeChat process memory for the pattern:
  [0x00*8][0x20,0x00*7][0x2F,0x00*7]  (three uint64: 0, 32, 47)

The 8 bytes immediately before this pattern are a pointer to the 32-byte raw passphrase.
Key derivation (SQLCipher 4 / WeChat V4):
  encKey = PBKDF2-HMAC-SHA512(passphrase, salt, 256000, 32)
  macKey = PBKDF2-HMAC-SHA512(encKey, salt^0x3a, 2, 32)
  HMAC  = HMAC-SHA512(macKey, page[16:4032] + pageNum_LE)
"""
import ctypes
import ctypes.wintypes as wt
import struct, os, sys, hashlib, json, time, functools
import hmac as hmac_mod

print = functools.partial(print, flush=True)

# Load config
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_DIR = os.path.join(_SCRIPT_DIR, "wechat-decrypt-main")
if not os.path.exists(os.path.join(_CONFIG_DIR, "config.json")):
    _CONFIG_DIR = _SCRIPT_DIR

PAGE_SZ = 4096
KEY_SZ = 32
SALT_SZ = 16
IV_SZ = 16
HMAC_SZ = 64
RESERVE_SZ = IV_SZ + HMAC_SZ  # 80
V4_ITER_COUNT = 256000

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
OUT_FILE = os.path.join(_CONFIG_DIR, _cfg["keys_file"]) if not os.path.isabs(_cfg["keys_file"]) else _cfg["keys_file"]


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


def verify_key(raw_passphrase, db_page1):
    """Verify raw passphrase (32 bytes) against a DB's first page.
    Uses SQLCipher 4 key derivation: PBKDF2 256000 iterations."""
    salt = db_page1[:SALT_SZ]
    # Step 1: derive encKey
    enc_key = hashlib.pbkdf2_hmac("sha512", raw_passphrase, salt, V4_ITER_COUNT, dklen=KEY_SZ)
    # Step 2: derive macKey
    mac_salt = bytes(b ^ 0x3a for b in salt)
    mac_key = hashlib.pbkdf2_hmac("sha512", enc_key, mac_salt, 2, dklen=KEY_SZ)
    # Step 3: verify HMAC
    data_end = PAGE_SZ - RESERVE_SZ + IV_SZ  # 4032
    hmac_data = db_page1[SALT_SZ:data_end]  # [16:4032]
    stored_hmac = db_page1[data_end:data_end + HMAC_SZ]  # [4032:4096]
    h = hmac_mod.new(mac_key, hmac_data, hashlib.sha512)
    h.update(struct.pack('<I', 1))  # page number = 1
    return h.digest() == stored_hmac


def main():
    print("=" * 60)
    print("  V4 Key Extraction (chatlog pattern + SQLCipher4 derivation)")
    print("=" * 60)

    # 1. Collect DB files - use message_0.db for validation
    db_files = []
    validation_db = None
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
                db_files.append((rel, path, sz, page1))
                if validation_db is None or 'message_0.db' in f:
                    validation_db = (rel, path, sz, page1)

    print(f"找到 {len(db_files)} 个数据库文件")
    val_rel, val_path, val_sz, val_page1 = validation_db
    print(f"验证数据库: {val_rel}")

    # 2. Open process
    pid = get_pid()
    h = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
    if not h:
        print("[ERROR] 无法打开进程 (需要管理员权限?)")
        sys.exit(1)

    # 3. Enumerate V4 regions
    regions = enum_v4_regions(h)
    total_mb = sum(s for _, s in regions) / 1024 / 1024
    print(f"[+] V4 内存区域: {len(regions)} 个, {total_mb:.0f}MB")

    # Test PBKDF2 speed
    print("[*] 测试 PBKDF2 速度...", end=" ")
    t_test = time.time()
    hashlib.pbkdf2_hmac("sha512", b"\x00" * 32, b"\x00" * 16, V4_ITER_COUNT, dklen=32)
    test_dur = time.time() - t_test
    print(f"{test_dur:.2f}s per validation")

    # 4. Search for pattern
    key_pattern = bytes([
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x2F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ])
    ptr_size = 8

    raw_key_hex = None
    seen_addrs = set()
    total_patterns = 0
    validated = 0
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

                validated += 1
                if verify_key(key_data, val_page1):
                    raw_key_hex = key_data.hex()
                    print(f"\n  [FOUND] raw_key={raw_key_hex}")
                    print(f"    ptr=0x{ptr_val:016X}")
                    print(f"    validated {validated} candidates in {time.time()-t0:.0f}s")
                    break

            if raw_key_hex:
                break
            offset += read_size

        if raw_key_hex:
            break

        elapsed = time.time() - t0
        if (reg_idx + 1) % 5 == 0 or reg_idx == len(regions) - 1:
            progress = sum(s for _, s in regions[:reg_idx + 1]) / sum(s for _, s in regions) * 100
            print(f"  [{progress:.0f}%] {total_patterns} patterns, {validated} validated, {elapsed:.0f}s")

    elapsed = time.time() - t0
    print(f"\n扫描完成: {elapsed:.0f}s, {total_patterns} patterns, {validated} validated")

    # 5. Save results - derive encKey per DB (mcp_server.py expects derived encKey)
    result = {}
    if raw_key_hex:
        raw_key_bytes = bytes.fromhex(raw_key_hex)
        print(f"\n[*] 为每个数据库派生 encKey (256000 iterations each)...")
        for rel, path, sz, page1 in db_files:
            salt = page1[:SALT_SZ]
            salt_hex = salt.hex()
            enc_key = hashlib.pbkdf2_hmac("sha512", raw_key_bytes, salt, V4_ITER_COUNT, dklen=KEY_SZ)
            result[rel] = {
                "enc_key": enc_key.hex(),
                "salt": salt_hex,
                "size_mb": round(sz / 1024 / 1024, 1)
            }
            print(f"  OK: {rel} ({sz / 1024 / 1024:.1f}MB) enc_key={enc_key.hex()[:16]}...")
    else:
        print("[!] 未找到密钥!")
        for rel, path, sz, page1 in db_files:
            salt_hex = page1[:SALT_SZ].hex()
            result[rel] = {"enc_key": "", "salt": salt_hex, "size_mb": round(sz / 1024 / 1024, 1)}
            print(f"  MISSING: {rel}")

    with open(OUT_FILE, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n密钥保存到: {OUT_FILE}")

    kernel32.CloseHandle(h)


if __name__ == '__main__':
    main()
