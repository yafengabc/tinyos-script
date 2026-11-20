# tinyos-script

Standalone compiler/VM experiment for TinyOS scripting:

```text
source.c --csc--> RIR2 image --rvm--> run (small, portable VM)
                              \--rcc--> native RV32 ELF (C, board-side)
```

The project is deliberately independent of the TinyOS build matrix so the
language, IR, register allocator and native backend can iterate quickly on the
host.  The TinyOS tree carries only a pinned copy/port and the board config.

## Layout

```text
src/csc.c            AST -> RIR2 compiler (streaming, per function)
src/rvm.c           portable RIR2 interpreter
src/rcc.c             RIR2 -> RV32 ELF/LZ4TOS native backend (board-side C)
src/py/               legacy Python interpreter (frozen reference)
include/lib.h         host shim for the TinyOS user API (desktop only)
spec/rir2.md          RIR2 file format, opcodes, natives
tests/                C programs and expected results
tests/py/demo.py      legacy interpreter demo
tools/test.py         host build + golden test runner
port/tinyos/          integration notes and pinned TinyOS configuration
legacy/avm/           old AMX-compatible VM backup (not built)
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

The C tests write extensionless images and let `rvm` detect them by the
`RIR2` magic; no `.rir`/`.bin` suffix is required or checked.  The runner also
builds the legacy `py` interpreter and checks `tests/py/demo.py` (`sum: 13`,
`fib(10): 55`, `done`).

## Status

- Source is read through a refill buffer, so source size is not capped by a
  fixed 4 KiB array.
- AST and IR are per function; function signatures and global layout are kept
  for the whole program.
- Calls use function ids from an explicit function table, so forward calls do
  not need call-site backpatching while streaming.
- Language subset: int/float (Q16.16), structs (nested fields, parameters and
  returns), struct arrays, arrays, UFCS, functions/recursion, if/while/for,
  printf/puts, GPIO/ADC/PWM/sleep/uptime.
- Operators: `+ - * / %`, `< > == != <= >=`, short-circuit `&&`/`||`,
  unary `!` and `-`; integer constant folding covers the arithmetic,
  comparison and logical forms.
- Optimizer: integer and Q16.16 constant folding, straight-line copy
  propagation, dead pure definitions, and NOP compaction with branch remap.
- `tests/benchfib.c` / `tests/benchloop.c` are manual on-board speed
  benchmarks (uptime-based), not part of the golden runner.
- `src/rcc.c` compiles RIR2 to a TinyOS-loadable RV32 ELF and a stored-LZ4TOS
  envelope.  It runs on the board (`user/rcc.c`) and on the host; every golden
  test is also assembled natively by `tools/test.py`.
- Strings: `char[]` byte arrays and `string` variables in a 512-byte mutable
  arena, with `strlen`, `strcmp`, `strlcpy`, `strlcat`, `atoi`, `print` and
  `printf("%s")`.  String parameters and string returns are supported.
- `rvm` is intentionally small: 256 IR, 512 global words, 1 KiB strings,
  512 arena bytes, 32 frames.  Larger programs are the job of `rcc` or the
  future larger interpreter profile.
- Final TinyOS toolchain is `csc` + `rvm` + `rcc`; `csa` + `pvm` stay in
  TinyOS temporarily as the comparison baseline.

## On-board speed (ESP32-C3)

Same source, timed with `uptime()` around the workload:

| workload | csa + pvm | csc + rvm | native rcc |
|---|---:|---:|---:|
| recursive `fib(24)` | 608 ms | 242 ms | 84 ms |
| 10,000,000-iteration loop | 53698 ms | 8286 ms | 578 ms |

`tests/benchfib.c` and `tests/benchloop.c` are the manual benchmark sources.
Native is 7.2x faster than `csa + pvm` on recursion and 92.9x faster on the
loop; the recursive case is dominated by the 13-register frame save/restore.

## Legacy `py`

`src/py` is the existing Python-subset interpreter: its own lexer, compiler,
bytecode and VM, with a small arena allocator over `sbrk()`.  It is kept here
so the project has the full scripting story in one place and so its demo can
be tested on the host.

The long-term direction is **not** to maintain a second language stack.  The
target is:

```text
Python source -> (shared frontend) -> AST -> RIR2 -> rvm / rcc
```

That would retire `py_compile`/`py_vm` and make Python just another frontend
for the same register IR and backends.  Until that exists, `py` is a frozen
reference interpreter.

TinyOS still carries a copy under `user/py` because its soak/smptest scripts
invoke it; that copy is frozen.  Make changes here first, then update the pin.

## Roadmap

1. Larger RIR2 interpreter profile (48 KiB window) for medium scripts.
2. `rcc`: RIR2 -> RV32 native ELF.  The board-side C implementation is
   `src/rcc.c`; the earlier Go reference remains in TinyOS `goc32/cmd/rcc`.
   `rvm` stays the differential-test oracle.
3. Unify the Python frontend onto AST + RIR2 (retire the separate bytecode VM).
4. Optional XIP/paging if native code must exceed the window.
