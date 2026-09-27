"""
Restart WeChat and immediately scan memory for the encryption key.
The key is briefly available during WeChat startup when databases are opened.

Approach:
1. Gracefully close WeChat
2. Start WeChat
3. Repeatedly scan memory for x'hex' patterns and V4 pattern candidates
4. Validate found keys with both 2-iter (encKey) and 256000-iter (passphrase) methods
"""
import ctypes, ctypes.wintypes as wt, struct, os, sys, re, json, time, functools, subprocess
import hashlib, hmac as hmac_mod
print = functools.partial(print, flush=True)

PAGE_SZ = 4096; KEY_SZ = 32; SALT_SZ = 16; IV_SZ = 16; HMAC_SZ = 64
RESERVE_SZ = IV_SZ + HMAC_SZ; V4_ITER_COUNT = 256000

kernel32 = ctypes.windll.kernel32
PROCESS_VM_READ = 0x0010; PROCESS_QUERY_INFORMATION = 0x0400
MEM_COMMIT = 0x1000; MEM_PRIVATE = 0x20000; PAGE_READWRITE = 0x04
READABLE = {0x02,0x04,0x08,0x10,0x20,0x40,0x80}

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_DIR = os.path.join(_SCRIPT_DIR, "wechat-decrypt-main")
with open(os.path.join(_CONFIG_DIR, "config.json"), encoding="utf-8") as f:
    _cfg = json.load(f)
DB_DIR = _cfg["db_dir"]
OUT_FILE = os.path.join(_CONFIG_DIR, _cfg["keys_file"])
WECHAT_EXE = r"E:\微信\微信\Weixin\Weixin.exe"

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress",ctypes.c_uint64),("AllocationBase",ctypes.c_uint64),
        ("AllocationProtect",wt.DWORD),("_pad1",wt.DWORD),("RegionSize",ctypes.c_uint64),
        ("State",wt.DWORD),("Protect",wt.DWORD),("Type",wt.DWORD),("_pad2",wt.DWORD)]

def read_mem(h, addr, sz):
    buf = ctypes.create_string_buffer(sz)
    n = ctypes.c_size_t(0)
    if kernel32.ReadProcessMemory(h, ctypes.c_uint64(addr), buf, sz, ctypes.byref(n)):
        return buf.raw[:n.value]
    return None

def find_wechat_pid():
    r = subprocess.run(["tasklist","/FI","IMAGENAME eq Weixin.exe","/FO","CSV","/NH"],
                       capture_output=True, text=True)
    best = (0,0)
    for line in r.stdout.strip().split('\n'):
        if not line.strip(): continue
        p = line.strip('"').split('","')
        if len(p)>=5:
            pid=int(p[1]); mem=int(p[4].replace(',','').replace(' K','').strip() or '0')
            if mem>best[1]: best=(pid,mem)
    return best[0]

def get_all_regions(h):
    regs = []
    addr = 0; mbi = MBI()
    while addr < 0x7FFFFFFFFFFF:
        if kernel32.VirtualQueryEx(h, ctypes.c_uint64(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))==0: break
        if mbi.State==MEM_COMMIT and mbi.Protect in READABLE and 0<mbi.RegionSize<500*1024*1024:
            regs.append((mbi.BaseAddress, mbi.RegionSize))
        nxt = mbi.BaseAddress + mbi.RegionSize
        if nxt<=addr: break
        addr = nxt
    return regs

def verify_key(raw_key, page1, use_256k=True):
    """Verify key with either 256000 iterations (passphrase) or 2 iterations (encKey)."""
    salt = page1[:SALT_SZ]
    if use_256k:
        enc_key = hashlib.pbkdf2_hmac("sha512", raw_key, salt, V4_ITER_COUNT, dklen=KEY_SZ)
    else:
        enc_key = raw_key
    mac_salt = bytes(b ^ 0x3a for b in salt)
    mac_key = hashlib.pbkdf2_hmac("sha512", enc_key, mac_salt, 2, dklen=KEY_SZ)
    data_end = PAGE_SZ - RESERVE_SZ + IV_SZ
    hmac_data = page1[SALT_SZ:data_end]
    stored = page1[data_end:data_end+HMAC_SZ]
    h = hmac_mod.new(mac_key, hmac_data, hashlib.sha512)
    h.update(struct.pack('<I', 1))
    return h.digest() == stored, enc_key

def scan_memory_for_keys(h, val_page1):
    """Scan all readable memory for x'hex' patterns and validate them."""
    regs = get_all_regions(h)
    hex_re = re.compile(b"x'([0-9a-fA-F]{64,192})'")

    found_key = None
    for base, size in regs:
        data = read_mem(h, base, size)
        if not data: continue

        # Search for x'hex' patterns
        for m in hex_re.finditer(data):
            hex_str = m.group(1).decode()
            hex_len = len(hex_str)

            # Try different key interpretations
            if hex_len >= 64:
                key_hex = hex_str[:64]  # First 64 hex chars = 32 bytes
                key_bytes = bytes.fromhex(key_hex)
                # Try as encKey (2 iterations, fast)
                valid, enc_key = verify_key(key_bytes, val_page1, use_256k=False)
                if valid:
                    print(f"  [FOUND via x'hex' as encKey] key={key_hex}")
                    return enc_key.hex(), "encKey"
                # Try as passphrase (256000 iterations, slow)
                valid, enc_key = verify_key(key_bytes, val_page1, use_256k=True)
                if valid:
                    print(f"  [FOUND via x'hex' as passphrase] key={key_hex}")
                    return key_hex, "passphrase"

    return None, None

def main():
    print("=" * 60)
    print("  Restart WeChat & Extract Key")
    print("=" * 60)

    # Load validation DB
    val_page1 = None
    for root, dirs, files in os.walk(DB_DIR):
        for f in files:
            if f == "message_0.db":
                with open(os.path.join(root, f), 'rb') as fh:
                    val_page1 = fh.read(PAGE_SZ)
                print(f"验证数据库: {os.path.relpath(os.path.join(root, f), DB_DIR)}")
                break
    if not val_page1:
        print("[ERROR] message_0.db not found"); sys.exit(1)

    # Step 1: Close WeChat
    print("\n[1] 关闭微信...")
    subprocess.run(["taskkill", "/IM", "Weixin.exe"], capture_output=True)
    time.sleep(3)
    # Force kill if still running
    pid = find_wechat_pid()
    if pid:
        print("  微信未关闭，强制结束...")
        subprocess.run(["taskkill", "/F", "/IM", "Weixin.exe"], capture_output=True)
        time.sleep(2)

    # Step 2: Start WeChat
    print("\n[2] 启动微信...")
    subprocess.Popen([WECHAT_EXE])
    print(f"  已启动: {WECHAT_EXE}")

    # Step 3: Wait for WeChat process and scan repeatedly
    print("\n[3] 等待微信进程并扫描内存...")
    max_wait = 120  # seconds
    scan_interval = 3  # seconds
    t_start = time.time()

    while time.time() - t_start < max_wait:
        pid = find_wechat_pid()
        if not pid:
            time.sleep(1)
            continue

        # Open process
        h = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
        if not h:
            time.sleep(1)
            continue

        elapsed = time.time() - t_start
        print(f"\n  [{elapsed:.0f}s] PID={pid} - 扫描内存...")

        # Scan for x'hex' patterns (fast)
        key_hex, key_type = scan_memory_for_keys(h, val_page1)

        if key_hex:
            print(f"\n  [SUCCESS] 找到密钥! type={key_type}")
            kernel32.CloseHandle(h)
            save_keys(key_hex, key_type, val_page1)
            return

        kernel32.CloseHandle(h)
        time.sleep(scan_interval)

    print("\n[!] 超时未找到密钥")
    print("[!] 可能原因: 微信登录窗口未关闭，或需要手动登录")

def save_keys(key_hex, key_type, val_page1):
    """Save derived encKeys for all databases."""
    # Collect all DB files
    db_files = []
    for root, dirs, files in os.walk(DB_DIR):
        for f in files:
            if f.endswith('.db') and not f.endswith('-wal') and not f.endswith('-shm'):
                path = os.path.join(root, f)
                rel = os.path.relpath(path, DB_DIR)
                sz = os.path.getsize(path)
                if sz < PAGE_SZ: continue
                with open(path, 'rb') as fh:
                    page1 = fh.read(PAGE_SZ)
                db_files.append((rel, path, sz, page1))

    result = {}
    if key_type == "passphrase":
        raw_bytes = bytes.fromhex(key_hex)
        print(f"\n[*] 为每个数据库派生 encKey (256000 iterations)...")
        for rel, path, sz, page1 in db_files:
            salt = page1[:SALT_SZ]
            enc_key = hashlib.pbkdf2_hmac("sha512", raw_bytes, salt, V4_ITER_COUNT, dklen=KEY_SZ)
            result[rel] = {"enc_key": enc_key.hex(), "salt": salt.hex(), "size_mb": round(sz/1024/1024,1)}
            print(f"  OK: {rel}")
    else:
        # key is already encKey - only valid for validation DB's salt
        # Each DB has different salt, so we need to find the passphrase
        # But if the key IS the encKey, we can only decrypt the validation DB
        for rel, path, sz, page1 in db_files:
            salt_hex = page1[:SALT_SZ].hex()
            if page1[:SALT_SZ] == val_page1[:SALT_SZ]:
                result[rel] = {"enc_key": key_hex, "salt": salt_hex, "size_mb": round(sz/1024/1024,1)}
                print(f"  OK: {rel}")
            else:
                result[rel] = {"enc_key": "", "salt": salt_hex, "size_mb": round(sz/1024/1024,1)}
                print(f"  MISSING: {rel} (需要单独的encKey)")

    with open(OUT_FILE, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n密钥保存到: {OUT_FILE}")

if __name__ == '__main__':
    main()
