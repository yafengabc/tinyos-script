#!/usr/bin/env python3
"""Compile the pinned target sources against a TinyOS checkout.

tools/test.py builds csc/rvm/rcc against this repository's include/lib.h, the
host shim.  The shipped image builds the same files against TinyOS user/lib.h,
which is a different header with the same API - so a rename in the shim (or a
new call site that only the shim provides) passes every host test and breaks
the board build.  That happened once: `struct tos_stat` existed only in the
shim and the pinned rvm stopped compiling for every target.

This runs the target half of the check:

    python tools/check_target_build.py --tos ../TinyOS

CI checks TinyOS out next to this repo and runs it; locally it is optional.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    # (name, source, extra flags)
    ("csc", ROOT / "src" / "csc.c", []),
    ("rvm", ROOT / "src" / "rvm.c", []),
    ("rcc", ROOT / "src" / "rcc" / "rcc.c",
     ["-DRCC_ARCH_RV32", "-I", str(ROOT / "src" / "rcc")]),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tos", default=os.environ.get("TINYOS", ""),
                    help="path to the TinyOS checkout (or set TINYOS)")
    ap.add_argument("--cc", default=os.environ.get("CC", ""),
                    help="compiler to use; defaults to clang for the target "
                         "parse (gcc does not accept --target=...) and to "
                         "$CC/cc for --host-cc")
    ap.add_argument("--host-cc", action="store_true",
                    help="parse for the host instead of rv32 (does not cover the "
                         "target-only native block; for debugging only)")
    ap.add_argument("--werror", action="store_true",
                    help="treat warnings as errors (noisier: the target headers "
                         "redeclare libc builtins on purpose)")
    args = ap.parse_args()
    if not args.tos:
        ap.error("--tos is required (or set TINYOS)")
    if not args.cc:
        # The rv32 parse needs clang: `--target=riscv32-unknown-elf` is a clang
        # flag and gcc (the usual `cc` on Linux) rejects it.  Host mode may use
        # whatever CC/cc the caller has.
        args.cc = "cc" if args.host_cc else "clang"
    tos = Path(args.tos).resolve()
    for hdr in ("user/lib.h", "include/tos_abi.h", "kernel/types.h"):
        if not (tos / hdr).is_file():
            ap.error("%s does not look like a TinyOS checkout (missing %s)" % (tos, hdr))

    inc = ["-I", str(tos / "user"), "-I", str(tos / "include"),
           "-I", str(tos / "kernel")]
    # Build for the target ISA, not the host: rvm.c guards its whole native
    # syscall block with `#if defined(__riscv) || defined(__arm__)`, so a host
    # x86 parse silently skips the code that broke last time.  rv32 covers
    # that block; the ARM half is the same source.
    target = [] if args.host_cc else ["--target=riscv32-unknown-elf", "-march=rv32im"]
    failed = []
    for name, src, extra in TARGETS:
        cmd = [args.cc, *target, "-fsyntax-only", "-std=gnu11", *extra, *inc, str(src)]
        if args.werror:
            cmd.append("-Werror")
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, errors="replace")
        # -fsyntax-only still returns 0 with warnings; only errors matter.
        if p.returncode != 0:
            print("FAIL %s against %s" % (name, tos))
            print(p.stdout.rstrip())
            if target and ("unrecognized command-line option" in p.stdout
                           or "unknown argument" in p.stdout):
                print("hint: the rv32 parse needs clang; pass --cc clang")
            failed.append(name)
        else:
            print("PASS %s" % name)
    if failed:
        print("target build broken for: %s" % ", ".join(failed))
        return 1
    print("TARGET BUILD OK (%d sources against %s)" % (len(TARGETS), tos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
