# tinyos-script

Standalone compiler/VM experiment for TinyOS scripting:

```text
source.c --csc3--> RIR2 image --rirvm--> run (small, portable VM)
                              \--irc--> native ELF (planned, per target)
```

The project is deliberately independent of the TinyOS build matrix so the
language, IR, register allocator and native backend can iterate quickly on the
host.  The TinyOS tree carries only a pinned copy/port and the board config.

## Layout

```text
src/csc3.c            AST -> RIR2 compiler (streaming, per function)
src/rirvm.c           portable RIR2 interpreter
include/lib.h         host shim for the TinyOS user API (desktop only)
spec/rir2.md          RIR2 file format, opcodes, natives
tests/                small C programs and expected results
tools/test.py         host build + golden test runner
port/tinyos/          integration notes and pinned TinyOS configuration
```

## Build and test

On Windows or any host with Python 3 and a C compiler:

```sh
python tools/test.py
```

or with make:

```sh
make
make test
```

The tests write extensionless images and let `rirvm` detect them by the
`RIR2` magic; no `.rir`/`.bin` suffix is required or checked.

## Status

- Source is read through a refill buffer, so source size is not capped by a
  fixed 4 KiB array.
- AST and IR are per function; function signatures and global layout are kept
  for the whole program.
- Calls use function ids from an explicit function table, so forward calls do
  not need call-site backpatching while streaming.
- Language subset: int/float (Q16.16), structs, struct arrays, arrays, UFCS,
  functions/recursion, if/while/for, printf/puts, GPIO/ADC/PWM/sleep/uptime.
- `rirvm` is intentionally small: 256 IR, 512 global words, 1 KiB strings,
  32 frames.  Larger programs are the job of the future native backend.

## Roadmap

1. Larger RIR2 interpreter profile (48 KiB window) for medium scripts.
2. `irc`: RIR2 -> RV32 native ELF, with target register allocation and a small
   built-in runtime; `rirvm` stays the differential-test oracle.
3. Optional XIP/paging if native code must exceed the window.
