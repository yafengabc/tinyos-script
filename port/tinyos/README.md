# TinyOS port

The TinyOS tree currently carries a pinned copy of this project:

| TinyOS path | source here |
|---|---|
| `user/csc/csc.c` | `src/csc.c` |
| `user/rvm/rvm.c` | `src/rvm.c` |
| `user/rcc.c` | `src/rcc.c` |
| `user/py/` (frozen) | `src/py/` |
| `configs/esp32c3-rir.conf` | not in this repo; TinyOS board config |
| `internal/build/config.go` | `[features] rir` gate |
| `goc32/cmd/rcc` | Go reference for the native backend; the board-side C implementation is `src/rcc.c` |

Pinned TinyOS state: code `6d54b5a`, acceptance `88fd539`.

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
- `rcc` reads RIR2 and writes an RV32 ELF/LZ4TOS image.  The C version runs on
  the board (`user/rcc.c`); `goc32/cmd/rcc` is the host reference.

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
2. Copy `src/csc.c`, `src/rvm.c` and `src/rcc.c` into the TinyOS paths.
3. Build `configs/esp32c3-rir.conf`, flash COM4, and run the on-board
   compile/run check with `tosput-cli` (do not use msh `echo` for large
   sources: `MAX_ARGS 8`, `LINE_MAX 256`).
4. Run TinyOS T0/T1/T2 and a C3 T3 card before changing the pin in docs.
