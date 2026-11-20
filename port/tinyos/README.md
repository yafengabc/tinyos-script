# TinyOS port

The TinyOS tree currently carries a pinned copy of this project:

| TinyOS path | source here |
|---|---|
| `user/csc3/csc3.c` | `src/csc3.c` |
| `user/rirvm/rirvm.c` | `src/rirvm.c` |
| `user/py/` (frozen) | `src/py/` |
| `configs/esp32c3-csc3.conf` | not in this repo; TinyOS board config |
| `internal/build/config.go` | `[features] csc3` gate |

Pinned TinyOS state: code `d54fa8d`, acceptance `f2c7ed3`.

## Integration rules

- Keep `csc3` and `rirvm` in `defaultUserExclude`; only `[features] csc3`
  removes them.  Default images ship `csc` + `pvm` only.
- The target build uses TinyOS `user/lib.h`, not `include/lib.h` here.  The
  host shim exists only for `tools/test.py`.
- The image format is detected by the `RIR2` magic.  Do not add or check
  filename suffixes in the shell, compiler or VM.
- `csc3` needs a source file and an output path; `rirvm` needs only the image.
  Both can be extensionless.

## Board numbers (ESP32-C3, `esp32c3-csc3.conf`)

| binary | /bin size | window |
|---|---:|---:|
| `csc3` | ~31.6 KiB | 116 KiB |
| `rirvm` | ~4.7 KiB | 32 KiB |

`rirvm` limits: 256 IR, 512 global words, 1 KiB strings, 512 arena bytes,
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
2. Copy `src/csc3.c` and `src/rirvm.c` into the TinyOS paths.
3. Build `configs/esp32c3-csc3.conf`, flash COM4, and run the on-board
   compile/run check with `tosput-cli` (do not use msh `echo` for large
   sources: `MAX_ARGS 8`, `LINE_MAX 256`).
4. Run TinyOS T0/T1/T2 and a C3 T3 card before changing the pin in docs.
