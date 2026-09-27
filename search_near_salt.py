"""
Search for the DB salt in WeChat memory, then look for 32-byte keys nearby.
The encryption key is often stored near the salt in WCDB internal structures.
Also tries AES-CBC decryption check (if pycryptodome available) as a faster alternative to PBKDF2.
"""
import ctypes, ctypes.wintypes as wt, struct, os, sys, hashlib, json, time, functools, hmac as hmac_mod
print = functools.partial(print, flush=True)

PAGE_SZ=4096; KEY_SZ=32; SALT_SZ=16; IV_SZ=16; HMAC_SZ=64; RESERVE_SZ=IV_SZ+HMAC_SZ; V4_ITER=256000
kernel32=ctypes.windll.kernel32
PROCESS_VM_READ=0x0010; PROCESS_QUERY_INFORMATION=0x0400
MEM_COMMIT=0x1000; READABLE={0x02,0x04,0x08,0x10,0x20,0x40,0x80}

# Try to import AES
try:
    from Crypto.Cipher import AES
    HAS_AES=True
    print("[+] pycryptodome available - will use AES decryption check")
except ImportError:
    HAS_AES=False
    print("[!] pycryptodome not available - will use HMAC verification only")

class MBI(ctypes.Structure):
    _fields_=[("BaseAddress",ctypes.c_uint64),("AllocationBase",ctypes.c_uint64),
        ("AllocationProtect",wt.DWORD),("_pad1",wt.DWORD),("RegionSize",ctypes.c_uint64),
        ("State",wt.DWORD),("Protect",wt.DWORD),("Type",wt.DWORD),("_pad2",wt.DWORD)]

def read_mem(h,addr,sz):
    buf=ctypes.create_string_buffer(sz); n=ctypes.c_size_t(0)
    if kernel32.ReadProcessMemory(h,ctypes.c_uint64(addr),buf,sz,ctypes.byref(n)):
        return buf.raw[:n.value]
    return None

def get_regions(h):
    regs=[]; addr=0; mbi=MBI()
    while addr<0x7FFFFFFFFFFF:
        if kernel32.VirtualQueryEx(h,ctypes.c_uint64(addr),ctypes.byref(mbi),ctypes.sizeof(mbi))==0: break
        if mbi.State==MEM_COMMIT and mbi.Protect in READABLE and 0<mbi.RegionSize<500*1024*1024:
            regs.append((mbi.BaseAddress,mbi.RegionSize))
        nxt=mbi.BaseAddress+mbi.RegionSize
        if nxt<=addr: break
        addr=nxt
    return regs

def verify_hmac(key_bytes, page1, use_256k):
    salt=page1[:SALT_SZ]
    enc_key=hashlib.pbkdf2_hmac("sha512",key_bytes,salt,V4_ITER,dklen=KEY_SZ) if use_256k else key_bytes
    mac_salt=bytes(b^0x3a for b in salt)
    mac_key=hashlib.pbkdf2_hmac("sha512",enc_key,mac_salt,2,dklen=KEY_SZ)
    de=PAGE_SZ-RESERVE_SZ+IV_SZ
    h=hmac_mod.new(mac_key,page1[SALT_SZ:de],hashlib.sha512)
    h.update(struct.pack('<I',1))
    return h.digest()==page1[de:de+HMAC_SZ], enc_key

def check_aes_decrypt(enc_key, page1):
    """Fast check: decrypt page 1 and see if it starts with SQLite header."""
    if not HAS_AES:
        return False
    iv=page1[PAGE_SZ-RESERVE_SZ:PAGE_SZ-RESERVE_SZ+IV_SZ]
    encrypted=page1[SALT_SZ:PAGE_SZ-RESERVE_SZ]
    try:
        cipher=AES.new(enc_key, AES.MODE_CBC, iv)
        decrypted=cipher.decrypt(encrypted)
        return decrypted[:16]==b'SQLite format 3\x00'
    except:
        return False

def main():
    _SCRIPT_DIR=os.path.dirname(os.path.abspath(__file__))
    _CONFIG_DIR=os.path.join(_SCRIPT_DIR,"wechat-decrypt-main")
    with open(os.path.join(_CONFIG_DIR,"config.json"),encoding="utf-8") as f:
        _cfg=json.load(f)
    db_dir=_cfg["db_dir"]
    OUT_FILE=os.path.join(_CONFIG_DIR,_cfg["keys_file"])

    # Load message_0.db
    val_page1=None; val_salt=None; val_path=None
    for root,dirs,files in os.walk(db_dir):
        for f in files:
            if f=="message_0.db":
                val_path=os.path.join(root,f)
                with open(val_path,'rb') as fh: val_page1=fh.read(PAGE_SZ)
                val_salt=val_page1[:SALT_SZ]
                break
    if not val_page1: print("[ERROR] message_0.db not found"); sys.exit(1)
    print(f"验证数据库: {os.path.relpath(val_path,db_dir)}")
    print(f"Salt (hex): {val_salt.hex()}")

    # Also collect all DB salts
    all_salts={}
    for root,dirs,files in os.walk(db_dir):
        for f in files:
            if f.endswith('.db') and not f.endswith('-wal') and not f.endswith('-shm'):
                path=os.path.join(root,f)
                sz=os.path.getsize(path)
                if sz<PAGE_SZ: continue
                with open(path,'rb') as fh: page1=fh.read(PAGE_SZ)
                salt=page1[:SALT_SZ]
                all_salts[salt]=page1

    print(f"共 {len(all_salts)} 个不同的salt")

    # Find WeChat PID
    import subprocess
    r=subprocess.run(["tasklist","/FI","IMAGENAME eq Weixin.exe","/FO","CSV","/NH"],
                     capture_output=True,text=True)
    best=(0,0)
    for line in r.stdout.strip().split('\n'):
        if not line.strip(): continue
        p=line.strip('"').split('","')
        if len(p)>=5:
            pid=int(p[1]); mem=int(p[4].replace(',','').replace(' K','').strip() or '0')
            if mem>best[1]: best=(pid,mem)
    if not best[0]: print("[ERROR] Weixin.exe 未运行"); sys.exit(1)
    print(f"[+] Weixin.exe PID={best[0]} ({best[1]//1024}MB)")

    h=kernel32.OpenProcess(PROCESS_VM_READ|PROCESS_QUERY_INFORMATION,False,best[0])
    if not h: print("[ERROR] 无法打开进程"); sys.exit(1)

    regs=get_regions(h)
    total_mb=sum(s for _,s in regs)/1024/1024
    print(f"[+] 可读内存: {len(regs)} 区域, {total_mb:.0f}MB")

    # Search for each salt in memory
    t0=time.time()
    salt_locations=[]  # (salt_bytes, address)

    for reg_idx,(base,size) in enumerate(regs):
        data=read_mem(h,base,size)
        if not data: continue
        for salt_bytes,page1 in all_salts.items():
            search_start=0
            while True:
                idx=data.find(salt_bytes,search_start)
                if idx==-1: break
                addr=base+idx
                salt_locations.append((salt_bytes,addr,data,idx))
                search_start=idx+1
        if (reg_idx+1)%500==0:
            print(f"  [{reg_idx+1}/{len(regs)}] {len(salt_locations)} salt locations, {time.time()-t0:.0f}s")

    print(f"\n找到 {len(salt_locations)} 个salt位置 ({time.time()-t0:.0f}s)")

    # For each salt location, look for 32-byte keys nearby
    # Check positions: -256 to +256 bytes from salt, at 8-byte alignment
    found_key=None; found_type=None
    checked=0

    for salt_bytes, addr, data, salt_idx in salt_locations:
        page1=all_salts[salt_bytes]
        # Check nearby positions
        for offset in range(-512, 512, 8):
            pos=salt_idx+offset
            if pos<0 or pos+32>len(data): continue
            key_data=data[pos:pos+32]
            # Skip low entropy
            if len(set(key_data))<16: continue
            if key_data.count(0)>8: continue
            checked+=1

            # Fast AES check (if available)
            if HAS_AES and check_aes_decrypt(key_data, page1):
                print(f"\n  [FOUND via AES] key={key_data.hex()} at offset {offset} from salt")
                found_key=key_data.hex(); found_type="encKey"; break

            # Method B HMAC check (fast)
            valid,enc=verify_hmac(key_data,page1,False)
            if valid:
                print(f"\n  [FOUND via Method B] key={key_data.hex()} at offset {offset} from salt")
                found_key=key_data.hex(); found_type="encKey"; break

        if found_key: break

        # Also try as passphrase (slow, only for first few salt locations)
        if salt_locations.index((salt_bytes,addr,data,salt_idx))<5:
            for offset in range(-256,257,8):
                pos=salt_idx+offset
                if pos<0 or pos+32>len(data): continue
                key_data=data[pos:pos+32]
                if len(set(key_data))<16: continue
                valid,enc=verify_hmac(key_data,page1,True)
                if valid:
                    print(f"\n  [FOUND via Method A] key={key_data.hex()} at offset {offset} from salt")
                    found_key=key_data.hex(); found_type="passphrase"; break
            if found_key: break

    print(f"\n检查了 {checked} 个候选 ({time.time()-t0:.0f}s)")

    # Save results
    result={}
    if found_key:
        if found_type=="passphrase":
            raw=bytes.fromhex(found_key)
            for root,dirs,files in os.walk(db_dir):
                for f in files:
                    if f.endswith('.db') and not f.endswith('-wal') and not f.endswith('-shm'):
                        path=os.path.join(root,f); rel=os.path.relpath(path,db_dir)
                        sz=os.path.getsize(path)
                        if sz<PAGE_SZ: continue
                        with open(path,'rb') as fh: page1=fh.read(PAGE_SZ)
                        salt=page1[:SALT_SZ]
                        enc=hashlib.pbkdf2_hmac("sha512",raw,salt,V4_ITER,dklen=KEY_SZ)
                        result[rel]={"enc_key":enc.hex(),"salt":salt.hex(),"size_mb":round(sz/1024/1024,1)}
                        print(f"  OK: {rel}")
        else:
            for root,dirs,files in os.walk(db_dir):
                for f in files:
                    if f.endswith('.db') and not f.endswith('-wal') and not f.endswith('-shm'):
                        path=os.path.join(root,f); rel=os.path.relpath(path,db_dir)
                        sz=os.path.getsize(path)
                        if sz<PAGE_SZ: continue
                        with open(path,'rb') as fh: page1=fh.read(PAGE_SZ)
                        salt_hex=page1[:SALT_SZ].hex()
                        if page1[:SALT_SZ]==val_salt:
                            result[rel]={"enc_key":found_key,"salt":salt_hex,"size_mb":round(sz/1024/1024,1)}
                            print(f"  OK: {rel}")
                        else:
                            result[rel]={"enc_key":"","salt":salt_hex,"size_mb":round(sz/1024/1024,1)}
    else:
        print("[!] 未找到密钥")
        for root,dirs,files in os.walk(db_dir):
            for f in files:
                if f.endswith('.db') and not f.endswith('-wal') and not f.endswith('-shm'):
                    path=os.path.join(root,f); rel=os.path.relpath(path,db_dir)
                    sz=os.path.getsize(path)
                    if sz<PAGE_SZ: continue
                    with open(path,'rb') as fh: page1=fh.read(PAGE_SZ)
                    result[rel]={"enc_key":"","salt":page1[:SALT_SZ].hex(),"size_mb":round(sz/1024/1024,1)}

    with open(OUT_FILE,'w') as f: json.dump(result,f,indent=2)
    print(f"\n密钥保存到: {OUT_FILE}")
    kernel32.CloseHandle(h)

if __name__=='__main__':
    main()
