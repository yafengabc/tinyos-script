# TinyOS port

The TinyOS tree currently carries a pinned copy of this project:

| TinyOS path | source here |
|---|---|
| `user/csc/csc.c` | `src/csc.c` |
| `user/rvm/rvm.c` | `src/rvm.c` |
| `user/rcc/rcc.c` | `src/rcc/rcc.c` |
| `user/rcc/rv32.inc` | `src/rcc/rv32.inc` |
| `user/rcc/thumb2.inc` | `src/rcc/thumb2.inc` |
| `user/rcc/thumb1.inc` | `src/rcc/thumb1.inc` |
| `user/py/` (frozen) | `src/py/` |
| `configs/esp32c3-rir.conf` | not in this repo; TinyOS board config |
| `internal/build/config.go` | `[features] rir` gate |

Pinned TinyOS state: code `451fa4d`, acceptance `451fa4d`.

## Integration rules

- Keep `csc`, `rvm` and `rcc` in `defaultUserExclude`; only `[features] rir`
  removes them.  Default images ship `csa` + `pvm`; those two are temporary
  comparison tools and will be retired once the register-IR path closes.
- The target build uses TinyOS `user/lib.h`, not `include/lib.h` here.  The
  host shim exists only for `tools/test.py`.
- The image format is detected by the `RIR2` magic.  Do not add or check
  filename suffixes in the shell, compiler or VM.
- `csc` needs a source file and an output path; `rvm` needs only the image.
  Both can be extensionless.
- `rcc` reads RIR2 and writes an ELF/LZ4TOS image.  The driver is
  `src/rcc/rcc.c` (pinned into TinyOS as `user/rcc/rcc.c`) and includes
  exactly one backend, selected by `-DRCC_ARCH_*`: `rv32.inc` for RV32,
  `thumb2.inc` for ARMv7/ARMv8-M (M33), and `thumb1.inc` for ARMv6-M (M0+,
  RP2040).  All three cover the full RIR2 core including strings and native
  calls; the 44-program corpus runs on both RP2350 halves.  TinyOS
  `configs/arm-rir.conf` and `configs/rpi-pico2-rir.conf` are the images
  that carry the backends on board.
- `Copy-Item` keeps the source timestamp.  TinyOS rebuilds a user program only
  when its source is newer than the object, so a copy can silently leave a stale
  binary in the image (it happened with `csc`: the build kept the 32-function
  table while `user/csc/csc.c` already had 256).  Touch the destination after
  copying:

  ```powershell
  Copy-Item ..\tinyos-script\src\csc.c user\csc\csc.c -Force
  (Get-Item user\csc\csc.c).LastWriteTime = Get-Date
  ```

## Board numbers (ESP32-C3, `esp32c3-rir.conf`)

| binary | /bin size | window |
|---|---:|---:|
| `csc` | ~35.2 KiB | 124 KiB |
| `rvm` | ~4.7 KiB | 32 KiB |
| `rcc` | ~18.1 KiB | 72 KiB |

`rvm` limits: 256 IR, 512 global words, 1 KiB strings, 512 arena bytes,
32 frames.

## Legacy `py`

TinyOS still carries `user/py` because `scripts/esp-c3/soak.py` and
`scripts/rp2350/smptest.py` invoke `py demo.py`.  Treat that copy as frozen:
make changes in `src/py/` here, then update the pin.  When those scripts are
updated (or their images explicitly opt into py), delete `user/py` and keep
only this project as the source of truth.  The plan is to retire the separate
bytecode VM and run Python through the shared AST + RIR2 pipeline.

## Updating the pin

1. Run `python tools/test.py` here.
2. Copy `src/csc.c`, `src/rvm.c`, `src/rcc/rcc.c` and `src/rcc/rv32.inc`
   into the TinyOS paths.
3. Build `configs/esp32c3-rir.conf`, flash COM4, and run the on-board
   compile/run check with `tosput-cli` (do not use msh `echo` for large
   sources: `MAX_ARGS 8`, `LINE_MAX 256`).
4. Run TinyOS T0/T1/T2 and a C3 T3 card before changing the pin in docs.
