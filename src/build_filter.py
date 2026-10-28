"""Wrap a relocation-free ARM32 object in a minimal executable ELF."""
from pathlib import Path
import struct

root = Path(__file__).resolve().parent
obj = (root / 'dhcp_filter.o').read_bytes()
assert obj[:6] == b'\x7fELF\x01\x01'
assert struct.unpack_from('<H', obj, 18)[0] == 40
shoff = struct.unpack_from('<I', obj, 32)[0]
shentsize, shnum, shstr = struct.unpack_from('<HHH', obj, 46)
sections = [struct.unpack_from('<10I', obj, shoff + i * shentsize) for i in range(shnum)]
strings = sections[shstr]
names = obj[strings[4]:strings[4] + strings[5]]

def section_name(section):
    start = section[0]
    return names[start:names.index(b'\0', start)]

assert not any(section[1] in (4, 9) and section[5] for section in sections), 'relocations not allowed'
text = next(section for section in sections if section_name(section) == b'.text')
code = obj[text[4]:text[4] + text[5]]
assert len(code) < 4096
base = 0x10000
header_size = 52 + 32
ident = b'\x7fELF\x01\x01\x01\x00' + bytes(8)
ehdr = struct.pack('<16sHHIIIIIHHHHHH', ident, 2, 40, 1, base + header_size,
                   52, 0, 0x05000200, 52, 32, 1, 0, 0, 0)
phdr = struct.pack('<8I', 1, 0, base, base, header_size + len(code),
                   header_size + len(code), 5, 4096)
out = root / 'dhcp_filter'
out.write_bytes(ehdr + phdr + code)
out.chmod(0o700)
print('built', out.name, len(code), 'bytes; no relocations')
