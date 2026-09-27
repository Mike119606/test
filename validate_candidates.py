"""
Phase 2: Validate V4 key candidates using PBKDF2-HMAC-SHA512 (256000 iterations).
Loads candidates from Phase 1, validates against message_0.db, saves derived encKeys.
"""
import struct, os, sys, hashlib, json, time, functools
import hmac as hmac_mod

print = functools.partial(print, flush=True)

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

CANDIDATES_FILE = os.path.join(_CONFIG_DIR, "candidates.json")
OUT_FILE = os.path.join(_CONFIG_DIR, "all_keys.json")
DB_DIR = None  # loaded from config


def verify_key(raw_passphrase, db_page1):
    """Verify raw passphrase (32 bytes) against a DB's first page."""
    salt = db_page1[:SALT_SZ]
    enc_key = hashlib.pbkdf2_hmac("sha512", raw_passphrase, salt, V4_ITER_COUNT, dklen=KEY_SZ)
    mac_salt = bytes(b ^ 0x3a for b in salt)
    mac_key = hashlib.pbkdf2_hmac("sha512", enc_key, mac_salt, 2, dklen=KEY_SZ)
    data_end = PAGE_SZ - RESERVE_SZ + IV_SZ  # 4032
    hmac_data = db_page1[SALT_SZ:data_end]
    stored_hmac = db_page1[data_end:data_end + HMAC_SZ]
    h = hmac_mod.new(mac_key, hmac_data, hashlib.sha512)
    h.update(struct.pack('<I', 1))
    return h.digest() == stored_hmac, enc_key


def main():
    print("=" * 60)
    print("  Phase 2: Validate candidates (PBKDF2 256000 iterations)")
    print("=" * 60)

    with open(CANDIDATES_FILE) as f:
        data = json.load(f)

    candidates = data["candidates"]
    db_files_info = data["db_files"]

    # Load validation DB (message_0.db)
    _cfg = {}
    with open(os.path.join(_CONFIG_DIR, "config.json"), encoding="utf-8") as f:
        _cfg = json.load(f)
    db_dir = _cfg["db_dir"]

    val_page1 = None
    for db_info in db_files_info:
        if "message_0.db" in db_info["rel"]:
            val_path = os.path.join(db_dir, db_info["rel"])
            with open(val_path, 'rb') as f:
                val_page1 = f.read(PAGE_SZ)
            print(f"验证数据库: {db_info['rel']}")
            break

    if val_page1 is None:
        print("[ERROR] 未找到 message_0.db")
        sys.exit(1)

    print(f"候选数: {len(candidates)}")

    # Test speed
    t_test = time.time()
    hashlib.pbkdf2_hmac("sha512", b"\x00" * 32, b"\x00" * 16, V4_ITER_COUNT, dklen=32)
    print(f"PBKDF2 速度: {time.time() - t_test:.2f}s per validation")
    print(f"预计总时间: {len(candidates) * 0.1:.0f}s")

    raw_key_hex = None
    t0 = time.time()

    for i, cand in enumerate(candidates):
        key_bytes = bytes.fromhex(cand["key_hex"])
        valid, enc_key = verify_key(key_bytes, val_page1)
        if valid:
            raw_key_hex = cand["key_hex"]
            print(f"\n  [FOUND] raw_key={raw_key_hex}")
            print(f"  ptr=0x{cand['ptr']:016X}")
            print(f"  candidate {i+1}/{len(candidates)} in {time.time()-t0:.0f}s")
            break
        if (i + 1) % 20 == 0:
            elapsed = time.time() - t0
            print(f"  [{i+1}/{len(candidates)}] {elapsed:.0f}s, no match yet")

    elapsed = time.time() - t0
    print(f"\n验证完成: {elapsed:.0f}s, {len(candidates)} candidates")

    # Save results
    result = {}
    if raw_key_hex:
        raw_key_bytes = bytes.fromhex(raw_key_hex)
        print(f"\n[*] 为每个数据库派生 encKey...")
        for db_info in db_files_info:
            salt = bytes.fromhex(db_info["salt"])
            enc_key = hashlib.pbkdf2_hmac("sha512", raw_key_bytes, salt, V4_ITER_COUNT, dklen=KEY_SZ)
            result[db_info["rel"]] = {
                "enc_key": enc_key.hex(),
                "salt": db_info["salt"],
                "size_mb": db_info["sz"] / 1024 / 1024
            }
            print(f"  OK: {db_info['rel']} enc_key={enc_key.hex()[:16]}...")
    else:
        print("[!] 未找到密钥!")
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
