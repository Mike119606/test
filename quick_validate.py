"""Quick validation: try Method B (2-iter, fast) on all candidates from candidates.json.
If no match, try Method A (256000-iter) in batches of 30."""
import struct, os, sys, hashlib, json, time, functools, hmac as hmac_mod
print = functools.partial(print, flush=True)

PAGE_SZ=4096; KEY_SZ=32; SALT_SZ=16; IV_SZ=16; HMAC_SZ=64; RESERVE_SZ=IV_SZ+HMAC_SZ; V4_ITER=256000

_SCRIPT_DIR=os.path.dirname(os.path.abspath(__file__))
_CONFIG_DIR=os.path.join(_SCRIPT_DIR,"wechat-decrypt-main")
OUT_FILE=os.path.join(_CONFIG_DIR,"all_keys.json")

def verify(key_bytes, page1, use_256k):
    salt=page1[:SALT_SZ]
    enc_key=hashlib.pbkdf2_hmac("sha512",key_bytes,salt,V4_ITER,dklen=KEY_SZ) if use_256k else key_bytes
    mac_salt=bytes(b^0x3a for b in salt)
    mac_key=hashlib.pbkdf2_hmac("sha512",enc_key,mac_salt,2,dklen=KEY_SZ)
    de=PAGE_SZ-RESERVE_SZ+IV_SZ
    h=hmac_mod.new(mac_key,page1[SALT_SZ:de],hashlib.sha512)
    h.update(struct.pack('<I',1))
    return h.digest()==page1[de:de+HMAC_SZ], enc_key

def main():
    with open(os.path.join(_CONFIG_DIR,"candidates.json")) as f:
        data=json.load(f)
    candidates=data["candidates"]
    db_files_info=data["db_files"]

    # Load validation DB
    with open(os.path.join(_CONFIG_DIR,"config.json"),encoding="utf-8") as f:
        _cfg=json.load(f)
    db_dir=_cfg["db_dir"]

    val_page1=None; val_rel=None
    for db_info in db_files_info:
        if "message_0.db" in db_info["rel"] and "fts" not in db_info["rel"]:
            with open(os.path.join(db_dir,db_info["rel"]),'rb') as f:
                val_page1=f.read(PAGE_SZ)
            val_rel=db_info["rel"]; break
    if not val_page1:
        for db_info in db_files_info:
            with open(os.path.join(db_dir,db_info["rel"]),'rb') as f:
                val_page1=f.read(PAGE_SZ)
            val_rel=db_info["rel"]; break

    print(f"验证数据库: {val_rel}")
    print(f"候选数: {len(candidates)}")

    # Method B: 2 iterations (fast)
    print(f"\n[*] Method B (encKey, 2-iter) - {len(candidates)} candidates...")
    t0=time.time()
    raw_key_hex=None; key_type=None
    for i,cand in enumerate(candidates):
        key_bytes=bytes.fromhex(cand["key_hex"])
        valid,enc=verify(key_bytes,val_page1,False)
        if valid:
            print(f"\n  [FOUND via Method B] enc_key={cand['key_hex']}")
            raw_key_hex=cand["key_hex"]; key_type="encKey"; break
    print(f"  Method B: {time.time()-t0:.1f}s, {'FOUND' if raw_key_hex else 'no match'}")

    # Method A: 256000 iterations (slow) - batch of 30
    if not raw_key_hex:
        print(f"\n[*] Method A (passphrase, 256000-iter) - batch of 30...")
        t0=time.time()
        batch_size=30
        for batch_start in range(0,len(candidates),batch_size):
            batch_end=min(batch_start+batch_size,len(candidates))
            for i in range(batch_start,batch_end):
                cand=candidates[i]
                key_bytes=bytes.fromhex(cand["key_hex"])
                valid,enc=verify(key_bytes,val_page1,True)
                if valid:
                    print(f"\n  [FOUND via Method A] passphrase={cand['key_hex']}")
                    raw_key_hex=cand["key_hex"]; key_type="passphrase"; break
            elapsed=time.time()-t0
            print(f"  [{batch_end}/{len(candidates)}] {elapsed:.0f}s",end="\r")
            if raw_key_hex: break
            if elapsed>10:
                print(f"\n  [TIMEOUT at {batch_end}/{len(candidates)}] saving partial...")
                break

    # Save results
    result={}
    if raw_key_hex:
        if key_type=="passphrase":
            raw=bytes.fromhex(raw_key_hex)
            print(f"\n[*] 派生 encKey for each DB...")
            for db_info in db_files_info:
                salt=bytes.fromhex(db_info["salt"])
                enc=hashlib.pbkdf2_hmac("sha512",raw,salt,V4_ITER,dklen=KEY_SZ)
                result[db_info["rel"]]={"enc_key":enc.hex(),"salt":db_info["salt"],"size_mb":db_info["sz"]/1024/1024}
                print(f"  OK: {db_info['rel']}")
        else:
            for db_info in db_files_info:
                if db_info["salt"]==val_page1[:SALT_SZ].hex():
                    result[db_info["rel"]]={"enc_key":raw_key_hex,"salt":db_info["salt"],"size_mb":db_info["sz"]/1024/1024}
                    print(f"  OK: {db_info['rel']}")
                else:
                    result[db_info["rel"]]={"enc_key":"","salt":db_info["salt"],"size_mb":db_info["sz"]/1024/1024}
    else:
        print("[!] 未找到密钥")
        for db_info in db_files_info:
            result[db_info["rel"]]={"enc_key":"","salt":db_info["salt"],"size_mb":db_info["sz"]/1024/1024}

    with open(OUT_FILE,'w') as f: json.dump(result,f,indent=2)
    print(f"\n密钥保存到: {OUT_FILE}")

if __name__=='__main__':
    main()
