# Toolchain notes

The pipeline is:

```text
source.c --csc--> RIR2 image --rvm--> run
                              \--rcc--> native ELF/LZ4TOS
```

- [`csc.md`](csc.md) — the C frontend: streaming two-pass model, optimizer,
  AST layout, limits, diagnostics.
- [`rvm.md`](rvm.md) — the interpreter: usage, summary line, limits, exit
  codes, role as the golden model.
- [`rcc.md`](rcc.md) — the native backend: backend selection, ELF/LZ4TOS
  layout, RV32 and Thumb-2 ABIs, code generation, limits, QEMU procedure.

The byte-level image format and opcode semantics are in
[`../spec/rir2.md`](../spec/rir2.md).  The TinyOS integration (pinned copies,
`[features] rir`, board configs) is in
[`../port/tinyos/README.md`](../port/tinyos/README.md).
