"""Structural checks for a stored-LZ4TOS image produced by rcc.

tools/test.py already compares program output through rvm and the C native
backend; this adds the ELF-side checks it used to claim but never performed
(issue #8):

  * LZ4TOS header (magic/version/raw size/block size);
  * the LZ4 token actually decodes to raw_size (the writer uses stored blocks,
    i.e. literals only, so this is a length parse rather than a decompressor);
  * the embedded ELF32 is ET_DYN, has the expected e_machine, e_entry = 0,
    and at least one valid PT_LOAD.

Usage: python tools/check_tos.py FILE.tos [rv32|arm]
"""

import struct
import sys

MACHINE = {"rv32": 243, "arm": 40}
PT_LOAD = 1


def check(path, arch):
    raw = open(path, "rb").read()
    errs = []
    if len(raw) < 29 or raw[:6] != b"LZ4TOS":
        return [f"{path}: not an LZ4TOS image"]
    ver = struct.unpack_from("<H", raw, 6)[0]
    out_len, block_len = struct.unpack_from("<II", raw, 8)
    if ver != 1:
        errs.append(f"version {ver} != 1")
    if block_len != len(raw) - 28:
        errs.append(f"block size {block_len} != file payload {len(raw) - 28}")

    # Stored LZ4: token, extension bytes, then out_len literal bytes.
    i = 28
    token = raw[i]
    i += 1
    lit = token >> 4
    if lit == 15:
        while raw[i] == 255:
            lit += 255
            i += 1
        lit += raw[i]
        i += 1
    if lit != out_len:
        errs.append(f"LZ4 literal length {lit} != raw size {out_len}")
    elf = raw[i:i + out_len]
    if len(elf) != out_len or elf[:4] != b"\x7fELF":
        return errs + [f"{path}: payload is not ELF"]

    machine = struct.unpack_from("<H", elf, 18)[0]
    etype = struct.unpack_from("<H", elf, 16)[0]
    entry = struct.unpack_from("<I", elf, 24)[0]
    phoff = struct.unpack_from("<I", elf, 28)[0]
    phentsize, phnum = struct.unpack_from("<HH", elf, 42)
    if etype != 3:
        errs.append(f"e_type {etype} != ET_DYN")
    if machine != MACHINE[arch]:
        errs.append(f"e_machine {machine} != {MACHINE[arch]} ({arch})")
    if entry != 0:
        errs.append(f"e_entry {entry} != 0")
    loads = 0
    for n in range(phnum):
        off = phoff + n * phentsize
        if off + 32 > len(elf):
            errs.append("program header outside file")
            break
        p_type, _, p_vaddr, _, p_filesz, p_memsz = struct.unpack_from("<6I", elf, off)
        if p_type == PT_LOAD:
            loads += 1
            if p_filesz > p_memsz or p_vaddr + p_memsz > 0x100000000:
                errs.append("invalid PT_LOAD")
    if loads < 1:
        errs.append("no PT_LOAD segment")
    return errs


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[2] not in MACHINE:
        sys.exit("usage: check_tos.py FILE.tos [rv32|arm]")
    errors = check(sys.argv[1], sys.argv[2])
    if errors:
        for e in errors:
            print(f"FAIL {sys.argv[1]}: {e}")
        sys.exit(1)
    print(f"OK {sys.argv[1]}")
