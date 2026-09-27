"""Parse PE export table to list exported function names."""
import struct, sys

def parse_exports(path):
    with open(path, 'rb') as f:
        data = f.read()

    pe_off = struct.unpack_from('<I', data, 0x3C)[0]
    assert data[pe_off:pe_off+4] == b'PE\x00\x00', "Not a valid PE file"

    # Optional header starts at pe_off + 24
    opt_off = pe_off + 24
    magic = struct.unpack_from('<H', data, opt_off)[0]
    is64 = magic == 0x20B

    # Export directory is at OptionalHeader + 96 (32-bit) or + 112 (64-bit)
    # Data directories start at opt_off + 96 (PE32) or opt_off + 112 (PE32+)
    if is64:
        export_rva = struct.unpack_from('<I', data, opt_off + 112)[0]
        export_size = struct.unpack_from('<I', data, opt_off + 116)[0]
    else:
        export_rva = struct.unpack_from('<I', data, opt_off + 96)[0]
        export_size = struct.unpack_from('<I', data, opt_off + 100)[0]

    print(f"PE32+ (64-bit): {is64}")
    print(f"Export RVA: 0x{export_rva:X}, Size: {export_size}")

    if export_rva == 0:
        print("No exports!")
        return []

    # Find section containing export RVA
    num_sections = struct.unpack_from('<H', data, pe_off + 6)[0]
    opt_hdr_size = struct.unpack_from('<H', data, pe_off + 20)[0]
    sec_off = pe_off + 24 + opt_hdr_size

    def rva_to_offset(rva):
        for i in range(num_sections):
            so = sec_off + i * 40
            v_size = struct.unpack_from('<I', data, so + 8)[0]
            v_addr = struct.unpack_from('<I', data, so + 12)[0]
            raw_size = struct.unpack_from('<I', data, so + 16)[0]
            raw_ptr = struct.unpack_from('<I', data, so + 20)[0]
            if v_addr <= rva < v_addr + max(v_size, raw_size):
                return raw_ptr + (rva - v_addr)
        return None

    exp_off = rva_to_offset(export_rva)
    if exp_off is None:
        print(f"Cannot map export RVA 0x{export_rva:X} to file offset")
        return []

    # IMAGE_EXPORT_DIRECTORY
    num_funcs = struct.unpack_from('<I', data, exp_off + 20)[0]
    num_names = struct.unpack_from('<I', data, exp_off + 24)[0]
    addr_funcs_rva = struct.unpack_from('<I', data, exp_off + 28)[0]
    addr_names_rva = struct.unpack_from('<I', data, exp_off + 32)[0]
    addr_ordinals_rva = struct.unpack_from('<I', data, exp_off + 36)[0]

    print(f"Functions: {num_funcs}, Named: {num_names}")

    names_off = rva_to_offset(addr_names_rva)
    if names_off is None:
        print("Cannot map name pointer table")
        return []

    exports = []
    for i in range(num_names):
        name_rva = struct.unpack_from('<I', data, names_off + i * 4)[0]
        name_off = rva_to_offset(name_rva)
        if name_off is None:
            continue
        end = data.index(b'\x00', name_off)
        name = data[name_off:end].decode('ascii', errors='replace')
        exports.append(name)

    return exports

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\应轩旸\Documents\trae_projects\001\gopath\bin\wx_key.dll"
    exports = parse_exports(path)
    print(f"\nExported functions ({len(exports)}):")
    for e in exports:
        print(f"  - {e}")
