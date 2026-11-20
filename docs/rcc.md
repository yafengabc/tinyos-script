# rcc 鈥?RIR2 to native ELF

`rcc` turns a RIR2 image into a TinyOS-loadable native program:

```text
rcc input.rir output.tos
```

The output is an ELF32 `ET_DYN` wrapped in a stored-LZ4TOS envelope.  One
source tree emits either target: `rcc.c` is the shared driver and includes
exactly one backend,

```text
src/rcc/rcc.c      RIR2 reader, analysis, two-pass driver, ELF/LZ4TOS, layout
src/rcc/rv32.inc   RV32IM backend
src/rcc/thumb2.inc Thumb-2 backend (ARMv7-M / ARMv8-M Mainline)
```

Selection is by architecture at build time (`__riscv` / `RCC_ARCH_RV32`,
`__arm__` / `RCC_ARCH_THUMB2`).  A board therefore carries only its own backend.

## Output image

```text
file 0x000  LZ4TOS header (28 bytes)
file 0x01c  stored-LZ4 token(s) + ELF
file 0x100  ELF .text      (vaddr 0, RX)
            padding to 16/32
            ELF data       (vaddr = align(text, arch), RW)
```

- ELF: `ET_DYN`, `e_entry = 0`, two `PT_LOAD` segments, no section table.
- `e_machine`: 243 (`EM_RISCV`) or 40 (`EM_ARM`); `e_flags`: 0 or
  `0x05000000` (EABI v5).
- The kernel relocates by load bias; `rcc` emits **no relocation table** and no
  `PT_DYNAMIC` (see *Address materialisation* below).
- The data segment holds, in order: the mutable arena (`dsize` bytes),
  globals (`gsize` words, at least one), the 64-byte argument buffer, the
  12-byte PWM request block, then `.bss` (zero-filled by the loader).
- `TEXT_OFF = 0x100`: the text segment's file offset; its virtual address is 0.

### LZ4TOS header (28 bytes)

| Offset | Field |
|---:|---|
| 0 | `"LZ4TOS"` |
| 6 | `u16` version (1) |
| 8 | `u32` raw ELF size |
| 12 | `u32` LZ4 block size |
| 16 | `u32` span hint (rounded to 4 KiB) |
| 20 | `u32` reserved (0) |
| 24 | `u32` reserved (0) |

`exec()` reserves the window from the span before decompressing straight into
it; a file without the hint is refused.  The exact kernel-side layout is in
`kernel/process.c` (`lz4_wrap_info_prefix`).

## Register mapping and ABI

### RV32

| RIR | Machine | Notes |
|---|---|---|
| 0..1 | `s0..s1` | callee saved |
| 2..11 | `s2..s11` | callee saved |
| 12 | `gp` | callee saved |
| 13..15 | `t0..t2` | callee saved in this ABI |
| scratch | `t3..t6`, `a0..a7` | |
| args | `data_argbuf[]` | stored by `ARG`, loaded in the prologue |
| return | `a0` | |
| syscall | `a7` = number, `a0..a2` = args | `ecall` |

### Thumb-2

| RIR | Machine | Notes |
|---|---|---|
| 0..6 | `r4..r10` | callee saved |
| 7..15 | frame slots | `[sp, 4*(n-7)]` |
| scratch | `r0..r3`, `r12` | |
| args | `data_argbuf[]` | same convention as RV32 |
| return | `r0` | |
| syscall | `r0` = number, `r1..r3` = args | `svc #0` |

Helpers (print, strings, float, bounds) save `r4-r11` and use only the scratch
registers, so a call cannot clobber a live RIR value.  The frame also holds the
register allocator's spill slots, starting after the nine RIR slots.

## Code generation

- **Two passes.**  Pass 1 emits sizes only; pass 2 emits bytes.  Every helper
  has a fixed size in both passes (`e_la` always emits `movw` *and* `movt`).
- **Labels.**  One label per IR instruction is allocated in order, so branch
  targets are link-time offsets.  `LABEL_MAX` therefore bounds the program as
  much as `PC_MAX` does.
- **Branches.**  Thumb-2 uses `B.W` (卤16 MiB), `Bcc.W` (卤1 MiB) and `BL`
  (卤16 MiB); RV32 uses `JAL`/`B<cond>` with an inverted near branch where
  needed.
- **Address materialisation.**  RV32 uses `auipc`+`addi`.  Thumb-2 has no
  cheap PC-relative 32-bit address, so `e_la` does `bl .+4` (LR := next
  instruction), clears the Thumb bit, and adds the link-time delta with
  `movw/movt`.  That costs five instructions per address but keeps the image
  relocation-free.
- **Data alignment.**  `rcc_arch_data_align()` is 16 on RV32 and 32 on ARM; the
  ARM MPU's smallest region is 32 bytes, and a 16-aligned arena made the first
  words of the data segment land in the read-only code region.
- **Division.**  RV32 uses `div/divu/rem/remu`; Thumb-2 uses `sdiv`+`mls`.
- **Float.**  Q16.16 only: `smull` for multiply, a 16-step shift/subtract loop
  for divide.  `print(float)` prints up to four decimals with trailing zeros
  removed; `printf("%.Nf")` keeps exactly N digits.

## Limits

| Limit | Host | Board (`__riscv` / `__arm__`) |
|---|---:|---:|
| RIR2 image | 256 KiB | 40 KiB (about 2000 instructions) |
| IR instructions (`PC_MAX`) | 16384 | 2048 |
| Labels | 16384 | 4096 |
| Text | 256 KiB | 48 KiB |
| Functions | 1024 | 256 |
| Window (ESP32-C3 / rv32) | 鈥?| 120 KiB |

Capacity note: labels cost about 1.45 per IR instruction because `%` and
`/` need sign fixups.  A program over a limit stops with a named diagnostic
(`pc out of range`, `too many labels`, `text overflow`, `cannot read input`).

## Supported IR

Every RIR2 opcode is implemented on both backends (constants, arithmetic,
comparisons, branches, calls/recursion, globals, arrays with bounds,
`LOADD/STORED`, byte strings, Q16.16 float, print family, native syscalls).
Unsupported future opcodes stop with `rcc: thumb2: NN not implemented yet`
rather than emitting wrong code.

## Testing

Host build (output can be inspected without a target):

```sh
gcc -std=gnu11 -O2 -I include -DRCC_ARCH_RV32 src/rcc/rcc.c -o build/rcc
gcc -std=gnu11 -O2 -I include -DRCC_ARCH_THUMB2 src/rcc/rcc.c -o build/rcc-arm
```

Checks that matter: `EM_RISCV`/`EM_ARM`, `ET_DYN`, the two `PT_LOAD` virtual
addresses, `e_entry = 0`, and the LZ4TOS raw size.  Runtime verification is on
QEMU: stage the `.tos` under `files.local/bin/` in TinyOS, build with
`configs/rv32-rir.conf` or `configs/arm-rir.conf`, and run the programs through
`tostest smoke`.  The native output must equal `rvm`'s output for the same
image, minus the summary line.  The full procedure, including the 512 KiB
ramdisk batching rule, is in TinyOS `docs/TESTING.md` 搂4.4鈥?.5.

## Port

TinyOS keeps a pinned copy:

```text
user/rcc/rcc.c       src/rcc/rcc.c
user/rcc/rv32.inc    src/rcc/rv32.inc
user/rcc/thumb2.inc  src/rcc/thumb2.inc
```

`Copy-Item` preserves the source timestamp, and the TinyOS build only
recompiles a newer source: touch the destination after copying or the image
keeps the previous backend.  See `port/tinyos/README.md`.
