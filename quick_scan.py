"""Lightweight rapid scanner: scans for x'hex' patterns in a tight loop.
Designed to catch the key during WeChat startup/login.
"""
import ctypes, ctypes.wintypes as wt, struct, os, sys, re, json, time, functools, hashlib, hmac as hmac_mod
print = functools.partial(print, flush=True)

PAGE_SZ=4096; KEY_SZ=32; SALT_SZ=16; IV_SZ=16; HMAC_SZ=64; RESERVE_SZ=IV_SZ+HMAC_SZ; V4_ITER=256000
kernel32 = ctypes.windll.kernel32
PROCESS_VM_READ=0x0010; PROCESS_QUERY_INFORMATION=0x0400
MEM_COMMIT=0x1000; READABLE={0x02,0x04,0x08,0x10,0x20,0x40,0x80}

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

def verify(key_bytes, page1, use_256k):
    salt=page1[:SALT_SZ]
    enc_key = hashlib.pbkdf2_hmac("sha512",key_bytes,salt,V4_ITER,dklen=KEY_SZ) if use_256k else key_bytes
    mac_salt=bytes(b^0x3a for b in salt)
    mac_key=hashlib.pbkdf2_hmac("sha512",enc_key,mac_salt,2,dklen=KEY_SZ)
    de=PAGE_SZ-RESERVE_SZ+IV_SZ
    h=hmac_mod.new(mac_key,page1[SALT_SZ:de],hashlib.sha512)
    h.update(struct.pack('<I',1))
    return h.digest()==page1[de:de+HMAC_SZ], enc_key

_SCRIPT_DIR=os.path.dirname(os.path.abspath(__file__))
_CONFIG_DIR=os.path.join(_SCRIPT_DIR,"wechat-decrypt-main")
with open(os.path.join(_CONFIG_DIR,"config.json"),encoding="utf-8") as f: _cfg=json.load(f)
DB_DIR=_cfg["db_dir"]
OUT_FILE=os.path.join(_CONFIG_DIR,_cfg["keys_file"])

def main():
    # Load validation DB
    val_page1=None
    for root,dirs,files in os.walk(DB_DIR):
        for f in files:
            if f=="message_0.db":
                with open(os.path.join(root,f),'rb') as fh: val_page1=fh.read(PAGE_SZ)
                break
    if not val_page1: print("[ERROR] message_0.db not found"); sys.exit(1)

    hex_re=re.compile(b"x'([0-9a-fA-F]{64,192})'")
    v4_pattern=struct.pack('<QQQ', 0, 0x20, 0x2F)

    import subprocess
    t_start=time.time()
    max_time=180  # 3 minutes

    while time.time()-t_start < max_time:
        r=subprocess.run(["tasklist","/FI","IMAGENAME eq Weixin.exe","/FO","CSV","/NH"],
                         capture_output=True,text=True)
        best=(0,0)
        for line in r.stdout.strip().split('\n'):
            if not line.strip(): continue
            p=line.strip('"').split('","')
            if len(p)>=5:
                pid=int(p[1]); mem=int(p[4].replace(',','').replace(' K','').strip() or '0')
                if mem>best[1]: best=(pid,mem)
        pid=best[0]

        if not pid:
            time.sleep(1)
            continue

        h=kernel32.OpenProcess(PROCESS_VM_READ|PROCESS_QUERY_INFORMATION,False,pid)
        if not h:
            time.sleep(1)
            continue

        elapsed=time.time()-t_start
        regs=get_regions(h)
        total_mb=sum(s for _,s in regs)/1024/1024
        xhex_found=0
        v4_found=0

        for base,size in regs:
            data=read_mem(h,base,size)
            if not data: continue

            # Search x'hex' patterns
            for m in hex_re.finditer(data):
                xhex_found+=1
                hex_str=m.group(1).decode()
                if len(hex_str)>=64:
                    key_bytes=bytes.fromhex(hex_str[:64])
                    # Try as encKey (fast)
                    valid,enc=verify(key_bytes,val_page1,False)
                    if valid:
                        print(f"\n[FOUND x'hex' as encKey] key={hex_str[:64]}")
                        save_and_exit(hex_str[:64],"encKey",val_page1)
                    # Try as passphrase (slow)
                    valid,enc=verify(key_bytes,val_page1,True)
                    if valid:
                        print(f"\n[FOUND x'hex' as passphrase] key={hex_str[:64]}")
                        save_and_exit(hex_str[:64],"passphrase",val_page1)

            # Search V4 pattern
            search_end=len(data)
            while True:
                idx=data.rfind(v4_pattern,0,search_end)
                if idx==-1 or idx<8: break
                v4_found+=1
                ptr=struct.unpack_from('<Q',data,idx-8)[0]
                search_end=idx
                if 0x10000<ptr<0x7FFFFFFFFFFF:
                    key_data=read_mem(h,ptr,0x20)
                    if key_data and len(key_data)>=0x20:
                        # Skip low-entropy
                        if len(set(key_data[:32]))<16: continue
                        valid,enc=verify(key_data,val_page1,False)
                        if valid:
                            print(f"\n[FOUND V4 as encKey] key={key_data.hex()}")
                            save_and_exit(key_data.hex(),"encKey",val_page1)
                        valid,enc=verify(key_data,val_page1,True)
                        if valid:
                            print(f"\n[FOUND V4 as passphrase] key={key_data.hex()}")
                            save_and_exit(key_data.hex(),"passphrase",val_page1)

        kernel32.CloseHandle(h)
        print(f"  [{elapsed:.0f}s] PID={pid} {total_mb:.0f}MB xhex={xhex_found} v4={v4_found}")
        time.sleep(2)

    print("\n[!] 超时，未找到密钥")

def save_and_exit(key_hex, key_type, val_page1):
    db_files=[]
    for root,dirs,files in os.walk(DB_DIR):
        for f in files:
            if f.endswith('.db') and not f.endswith('-wal') and not f.endswith('-shm'):
                path=os.path.join(root,f); rel=os.path.relpath(path,DB_DIR)
                sz=os.path.getsize(path)
                if sz<PAGE_SZ: continue
                with open(path,'rb') as fh: page1=fh.read(PAGE_SZ)
                db_files.append((rel,path,sz,page1))

    result={}
    if key_type=="passphrase":
        raw=bytes.fromhex(key_hex)
        for rel,path,sz,page1 in db_files:
            salt=page1[:SALT_SZ]
            enc=hashlib.pbkdf2_hmac("sha512",raw,salt,V4_ITER,dklen=KEY_SZ)
            result[rel]={"enc_key":enc.hex(),"salt":salt.hex(),"size_mb":round(sz/1024/1024,1)}
            print(f"  OK: {rel}")
    else:
        for rel,path,sz,page1 in db_files:
            salt_hex=page1[:SALT_SZ].hex()
            if page1[:SALT_SZ]==val_page1[:SALT_SZ]:
                result[rel]={"enc_key":key_hex,"salt":salt_hex,"size_mb":round(sz/1024/1024,1)}
                print(f"  OK: {rel}")
            else:
                result[rel]={"enc_key":"","salt":salt_hex,"size_mb":round(sz/1024/1024,1)}

    with open(OUT_FILE,'w') as f: json.dump(result,f,indent=2)
    print(f"\n密钥保存到: {OUT_FILE}")
    sys.exit(0)

if __name__=='__main__':
    main()
