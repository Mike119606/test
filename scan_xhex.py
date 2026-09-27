"""Quick scan for x'hex' key patterns in WeChat memory."""
import ctypes, ctypes.wintypes as wt, struct, os, sys, re, json, time, functools
print = functools.partial(print, flush=True)

PAGE_SZ = 4096; SALT_SZ = 16; KEY_SZ = 32
kernel32 = ctypes.windll.kernel32
PROCESS_VM_READ = 0x0010; PROCESS_QUERY_INFORMATION = 0x0400
MEM_COMMIT = 0x1000; READABLE = {0x02,0x04,0x08,0x10,0x20,0x40,0x80}

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

def main():
    import subprocess
    r = subprocess.run(["tasklist","/FI","IMAGENAME eq Weixin.exe","/FO","CSV","/NH"],
                       capture_output=True, text=True)
    best = (0,0)
    for line in r.stdout.strip().split('\n'):
        if not line.strip(): continue
        p = line.strip('"').split('","')
        if len(p)>=5:
            pid=int(p[1]); mem=int(p[4].replace(',','').replace(' K','').strip() or '0')
            if mem>best[1]: best=(pid,mem)
    if not best[0]: print("[ERROR] Weixin.exe 未运行"); sys.exit(1)
    print(f"[+] Weixin.exe PID={best[0]} ({best[1]//1024}MB)")

    h = kernel32.OpenProcess(PROCESS_VM_READ|PROCESS_QUERY_INFORMATION, False, best[0])
    if not h: print("[ERROR] 无法打开进程"); sys.exit(1)

    # Enumerate all readable regions
    regs = []
    addr = 0; mbi = MBI()
    while addr < 0x7FFFFFFFFFFF:
        if kernel32.VirtualQueryEx(h, ctypes.c_uint64(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))==0: break
        if mbi.State==MEM_COMMIT and mbi.Protect in READABLE and 0<mbi.RegionSize<500*1024*1024:
            regs.append((mbi.BaseAddress, mbi.RegionSize))
        nxt = mbi.BaseAddress + mbi.RegionSize
        if nxt<=addr: break
        addr = nxt

    total_mb = sum(s for _,s in regs)/1024/1024
    print(f"[+] 可读内存: {len(regs)} 区域, {total_mb:.0f}MB")

    # Search for x'hex' pattern
    hex_re = re.compile(b"x'([0-9a-fA-F]{64,192})'")
    all_matches = []
    t0 = time.time()

    for reg_idx, (base, size) in enumerate(regs):
        data = read_mem(h, base, size)
        if not data: continue
        for m in hex_re.finditer(data):
            hex_str = m.group(1).decode()
            addr_found = base + m.start()
            all_matches.append((addr_found, hex_str, len(hex_str)))

        if (reg_idx+1) % 200 == 0:
            elapsed = time.time()-t0
            print(f"  [{reg_idx+1}/{len(regs)}] {len(all_matches)} matches, {elapsed:.0f}s")

    elapsed = time.time()-t0
    print(f"\n扫描完成: {elapsed:.0f}s, {len(all_matches)} 个 x'hex' 匹配")

    for addr, hex_str, hex_len in all_matches[:20]:
        print(f"  0x{addr:016X} len={hex_len} hex={hex_str[:80]}{'...' if len(hex_str)>80 else ''}")

    if not all_matches:
        print("\n[!] 内存中未找到 x'hex' 模式 - 密钥可能已被清空")
        print("[!] 需要重启微信以重新加载密钥")

    kernel32.CloseHandle(h)

if __name__ == '__main__':
    main()
