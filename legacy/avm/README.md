# avm (backup)

This is the old TinyOS **AMX-compatible VM experiment** (`user/avm`), moved
here as a reference and spare implementation.  It is not built by the host
test runner and is no longer part of any TinyOS image.

It implements the core Pawn 4.1 P-code subset (32-bit cells, `-O1`, no
overlay/packed opcodes) with its own `avm_init`/`avm_run` state block and
native callbacks.

The supported AMX path remains the old `csa` compiler + `pvm`; the current
register-IR path is `csc` + `rvm` + `rcc`.
