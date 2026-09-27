"""
Phase 2b: Validate candidates with BOTH methods:
  Method A: key is raw passphrase -> PBKDF2 256000 iterations
  Method B: key is already derived encKey -> PBKDF2 2 iterations (for macKey only)
Also relaxes entropy filter (loads all 658 candidates from raw scan).
"""
import struct, os, sys, hashlib, json, time, functools
import hmac as hmac_mod
import ctypes
import ctypes.wintypes as wt

print = functools.partial(print, flush=True)

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_DIR = os.path.join(_SCRIPT_DIR, "wechat-decrypt-main")

PAGE_SZ = 4096
KEY_SZ = 32
SALT_SZ = 16
IV_SZ = 16
HMAC_SZ = 64
RESERVE_SZ = IV_SZ + HMAC_SZ
V4_ITER_COUNT = 256000

OUT_FILE = os.path.join(_CONFIG_DIR, "all_keys.json")

kernel32 = ctypes.windll.kernel32
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
MEM_COMMIT = 0x1000
MEM_PRIVATE = 0x20000
PAGE_READWRITE = 0x04


class MBI(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_uint64), ("AllocationBase", ctypes.c_uint64),
        ("AllocationProtect", wt.DWORD), ("_pad1", wt.DWORD),
        ("RegionSize", ctypes.c_uint64), ("State", wt.DWORD),
        ("Protect", wt.DWORD), ("Type", wt.DWORD), ("_pad2", wt.DWORD),
    ]


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


def compute_hmac(mac_key, page1, pgno=1):
    data_end = PAGE_SZ - RESERVE_SZ + IV_SZ
    hmac_data = page1[SALT_SZ:data_end]
    stored = page1[data_end:data_end + HMAC_SZ]
    h = hmac_mod.new(mac_key, hmac_data, hashlib.sha512)
    h.update(struct.pack('<I', pgno))
    return h.digest() == stored


def verify_method_a(raw_passphrase, page1):
    """Method A: key is raw passphrase -> 256000 iterations"""
    salt = page1[:SALT_SZ]
    enc_key = hashlib.pbkdf2_hmac("sha512", raw_passphrase, salt, V4_ITER_COUNT, dklen=KEY_SZ)
    mac_salt = bytes(b ^ 0x3a for b in salt)
    mac_key = hashlib.pbkdf2_hmac("sha512", enc_key, mac_salt, 2, dklen=KEY_SZ)
    return compute_hmac(mac_key, page1), enc_key


def verify_method_b(enc_key, page1):
    """Method B: key is already derived encKey -> 2 iterations only"""
    salt = page1[:SALT_SZ]
    mac_salt = bytes(b ^ 0x3a for b in salt)
    mac_key = hashlib.pbkdf2_hmac("sha512", enc_key, mac_salt, 2, dklen=KEY_SZ)
    return compute_hmac(mac_key, page1), enc_key


def main():
    print("=" * 60)
    print("  Phase 2b: Validate with BOTH methods (raw scan, no entropy filter)")
    print("=" * 60)

    # Load config
    with open(os.path.join(_CONFIG_DIR, "config.json"), encoding="utf-8") as f:
        _cfg = json.load(f)
    db_dir = _cfg["db_dir"]

    # Load candidates
    with open(os.path.join(_CONFIG_DIR, "candidates.json")) as f:
        data = json.load(f)
    db_files_info = data["db_files"]

    # Find message_0.db for validation
    val_page1 = None
    val_rel = None
    for db_info in db_files_info:
        if "message_0.db" in db_info["rel"] and "fts" not in db_info["rel"]:
            val_path = os.path.join(db_dir, db_info["rel"])
            with open(val_path, 'rb') as f:
                val_page1 = f.read(PAGE_SZ)
            val_rel = db_info["rel"]
            break

    if val_page1 is None:
        # Use first DB
        for db_info in db_files_info:
            val_path = os.path.join(db_dir, db_info["rel"])
            with open(val_path, 'rb') as f:
                val_page1 = f.read(PAGE_SZ)
            val_rel = db_info["rel"]
            break

    print(f"验证数据库: {val_rel}")

    # Re-scan memory to get ALL candidates (no entropy filter)
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
    print(f"[+] Weixin.exe PID={best[0]}")

    h = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, best[0])
    if not h:
        print("[ERROR] 无法打开进程")
        sys.exit(1)

    regions = enum_v4_regions(h)
    print(f"[+] V4 内存区域: {len(regions)} 个")

    key_pattern = bytes([
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x2F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ])
    ptr_size = 8

    # Collect ALL candidates (no entropy filter)
    all_candidates = []
    seen_addrs = set()
    t0 = time.time()

    for base, size in regions:
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
                ptr_val = struct.unpack_from('<Q', data, idx - ptr_size)[0]
                search_end = idx
                if ptr_val <= 0x10000 or ptr_val >= 0x7FFFFFFFFFFF:
                    continue
                if ptr_val in seen_addrs:
                    continue
                seen_addrs.add(ptr_val)
                key_data = read_mem(h, ptr_val, 0x20)
                if key_data and len(key_data) >= 0x20:
                    all_candidates.append((ptr_val, key_data))
            offset += read_size

    print(f"[+] 扫描完成: {len(all_candidates)} candidates in {time.time()-t0:.0f}s")
    kernel32.CloseHandle(h)

    # First try Method B (fast, 2 iterations) on ALL candidates
    print(f"\n[*] Method B (encKey, 2 iterations) - testing {len(all_candidates)} candidates...")
    t0 = time.time()
    for i, (ptr, key_data) in enumerate(all_candidates):
        valid, enc_key = verify_method_b(key_data, val_page1)
        if valid:
            print(f"\n  [FOUND via Method B] enc_key={enc_key.hex()}")
            print(f"  ptr=0x{ptr:016X}")
            raw_key_hex = enc_key.hex()
            break
        if (i + 1) % 100 == 0:
            print(f"  [{i+1}/{len(all_candidates)}] {time.time()-t0:.0f}s")
    else:
        print(f"  Method B: no match in {time.time()-t0:.0f}s")
        raw_key_hex = None

    # If Method B failed, try Method A (slow, 256000 iterations) on all candidates
    if not raw_key_hex:
        print(f"\n[*] Method A (passphrase, 256000 iterations) - testing {len(all_candidates)} candidates...")
        t0 = time.time()
        for i, (ptr, key_data) in enumerate(all_candidates):
            valid, enc_key = verify_method_a(key_data, val_page1)
            if valid:
                print(f"\n  [FOUND via Method A] raw_key={key_data.hex()}")
                print(f"  enc_key={enc_key.hex()}")
                print(f"  ptr=0x{ptr:016X}")
                raw_key_hex = key_data.hex()
                is_passphrase = True
                break
            if (i + 1) % 20 == 0:
                print(f"  [{i+1}/{len(all_candidates)}] {time.time()-t0:.0f}s")
        else:
            print(f"  Method A: no match in {time.time()-t0:.0f}s")
            raw_key_hex = None
            is_passphrase = False

    # Save results
    result = {}
    if raw_key_hex:
        if is_passphrase:
            print(f"\n[*] 为每个数据库派生 encKey...")
            raw_bytes = bytes.fromhex(raw_key_hex)
            for db_info in db_files_info:
                salt = bytes.fromhex(db_info["salt"])
                enc_key = hashlib.pbkdf2_hmac("sha512", raw_bytes, salt, V4_ITER_COUNT, dklen=KEY_SZ)
                result[db_info["rel"]] = {
                    "enc_key": enc_key.hex(),
                    "salt": db_info["salt"],
                    "size_mb": db_info["sz"] / 1024 / 1024
                }
                print(f"  OK: {db_info['rel']}")
        else:
            # Key is already encKey - but each DB has different salt, so encKey differs per DB
            # This means we can only decrypt the validation DB. Need to find per-DB encKeys.
            # For now, save what we have
            for db_info in db_files_info:
                if db_info["rel"] == val_rel:
                    result[db_info["rel"]] = {
                        "enc_key": raw_key_hex,
                        "salt": db_info["salt"],
                        "size_mb": db_info["sz"] / 1024 / 1024
                    }
                    print(f"  OK: {db_info['rel']} (only validation DB - need per-DB keys)")
                else:
                    result[db_info["rel"]] = {
                        "enc_key": "",
                        "salt": db_info["salt"],
                        "size_mb": db_info["sz"] / 1024 / 1024
                    }
    else:
        print("[!] 两种方法都未找到密钥!")
        for db_info in db_files_info:
            result[db_info["rel"]] = {
                "enc_key": "",
                "salt": db_info["salt"],
                "size_mb": db_info["sz"] / 1024 / 1024
            }

    with open(OUT_FILE, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n密钥保存到: {OUT_FILE}")


if __name__ == '__main__':
    main()
