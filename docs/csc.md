# csc — C frontend

`csc` compiles the TinyOS scripting subset of C into a RIR2 image:

```text
csc input.c output.rir
```

The output is a register IR, not machine code.  `rvm` interprets it and `rcc`
turns it into a native ELF.  The file format and opcode list live in
[`../spec/rir2.md`](../spec/rir2.md); this page is about the compiler itself.

## Compilation model

The source is **streamed**, not loaded into one buffer:

1. **Pass 1** scans the file: string pool, global layout, struct layout and
   function signatures.  Function bodies are skipped with `skip_balanced()`, so
   a file of any size works.
2. The file is rewound (`lseek(fd, 0, 0)`).
3. **Pass 2** re-reads it and compiles **one function at a time**: parse the
   body into the AST, run the optimizer, allocate registers, append the IR, and
   reset the AST/IR scratch for the next function.

Only the function table has to survive the whole program.  That table is a
compact `Sig` (name offset, entry pc, parameter types, return type) plus a name
pool, so 256 functions cost roughly what 32 used to.

## Optimizer

After a function body is parsed:

1. constant folding (integers and Q16.16) happens in the parser;
2. straight-line copy propagation (`copy_prop`);
3. peephole rewrites (`peephole`);
4. dead pure definitions (`dce`);
5. NOP compaction with branch remap (`compact`);
6. register allocation (`regalloc_one`) with spill slots through
   `LOADL`/`STOREL`.

## Limits

| Limit | Host build | Board build (`__riscv` / `__arm__`) |
|---|---:|---:|
| AST nodes per function | 4096 | 256 |
| IR instructions per function | 1024 | 256 |
| Functions per program | 1024 | 256 |
| Symbols | 64 | 64 |
| Struct types / fields | 16 / 8 | 8 / 8 |
| String pool | 1024 B | 1024 B |
| Byte arena | 512 B | 512 B |
| Declaration/field text | per function, 3072 B | same |

Hitting one prints a diagnostic and exits non-zero; nothing is truncated
silently.  The board limits are why the large tests (`bigbody`, and the `-rir`
images) are compiled on the host and only `rcc` runs on the target.

## AST representation

An AST node is 56 bytes:

```c
uint64_t hash;        /* 64-bit FNV-1a of an identifier; N_DECL: text offset */
Node *lhs, *rhs, *cond, *then, *els, *body, *next, *args;
int val;
uint32_t field_off;   /* dotted field path, in the per-function text pool */
uint16_t alen, line;
uint8_t kind, stype, ftype, ctype;
```

Identifiers are hashes; the symbol, function, struct and constant tables keep
the real names, so a collision (equal hash, different spelling) is detected at
insertion and reported instead of silently merging.  Declarations and dotted
field paths are the only node text kept, in a scratch pool reset per function.

## Native functions

Besides string builtins (`strlen`, `strcmp`, `strlcpy`, `strlcat`, `atoi`,
`print`/`printf`/`puts`), a small native table is available:

| Name | Args | Returns |
|---|---|---|
| `gpio_count/mode/write/read` | 0-2 | some |
| `adc_count/read`, `pwm_count/set/off` | 0-3 | some |
| `sleep`, `uptime` | 0-1 | some |
| `run(path)` | 1 string | child exit code |
| `open(path)`, `create(path)` | 1 string | fd or -1 |
| `read(fd, buf, len)`, `write(fd, buf, len)` | int, string, int | bytes or -1 |
| `close(fd)`, `unlink(path)` | 1 | 0 or -1 |
| `capture(path, buf, cap)` | string, string, int | bytes captured |
| `readdir(index, buf, len)` | int, string, int | name length or 0 |
| `isdir(path)` | string | 1 dir, 0 file, -1 error |

`run()` spawns the program and waits; it does not replace the caller.  File paths and buffers are arena offsets; `read`/`write` move bytes through the 512-byte mutable arena.  The
argument is checked to be a string (`csc` rejects `run(42)`).  The host `rvm`
returns -1 because it has no child processes; QEMU/boards exercise it.

## Output and diagnostics

The output starts with the `RIR2` magic; no filename suffix is required.
Parse and codegen errors name the source line, e.g. `csc: AST full at line 30`.

`csc` must not be confused with `csa`, the older C→AMX compiler that is still
in TinyOS as a comparison baseline.

## Testing

`python tools/test.py` builds `csc`, compiles every program in `tests/` and
checks the `rvm` output.  Native-only programs (more than 256 IR) are listed
separately in the same runner and only have to produce an `LZ4TOS` image.
