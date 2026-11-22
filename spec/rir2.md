# RIR2 image format

RIR2 is the portable output of `csc` and the input of `rvm` (and `rcc`,
the RV32 native backend in `src/rcc/rcc.c`).  It is detected by magic,
not by a filename extension.

All integers are little-endian int32.

## Header (28 bytes)

| offset | field | meaning |
|---:|---|---|
| 0 | magic | `"RIR2"` |
| 4 | nir | total instruction records |
| 8 | gsize | global data words (`g[]`) |
| 12 | entry | entry instruction (main) |
| 16 | nfuncs | function table entries |
| 20 | strsize | string pool bytes |
| 24 | dsize | mutable string-arena bytes |

## Layout

```text
header (28)
nir * 20-byte instruction records
nfuncs * 4-byte entry PCs
strsize bytes of NUL-terminated strings
dsize bytes of initial string-arena data
```

An instruction record is five int32s: `op, a, b, c, d`.  Operand meaning is
opcode-specific.  Branches store absolute instruction indices in the final
image.  CALL stores a function id in `a`; the VM resolves it through the
function table.

`strsize` bytes are read-only literals used by `PRINTS`, `PRINTN` and printf
formats.  `dsize` bytes are a writable arena holding `char[]` storage and the
copies of string literals used as values.  The VM keeps this initial image and
restores it at the start of every repetition.

## NATIVEC

`NATIVEC a=<native id> d=<destination vreg>`: arguments are written into the
shared `ARG` buffer by preceding `ARG` instructions (up to 3 words); the
return value is placed in the destination vreg (`-1` when the native has no
return value).  Native ids are defined by the `NAT_*` enum in `src/csc.c` and mirrored in `src/rvm.c` and `src/rcc/rcc.c`; they must stay in
sync between `csc`, `rvm` and all `rcc` backends.

## Execution model

- One frame per call, 32 frames; frame 0 is main.
- 16 registers per frame; r13–r15 are spill scratch during execution of
  rewritten code.  `rvm` has a fixed 16-slot spill area and rejects an
  out-of-range `LOADL`/`STOREL` with a diagnostic instead of silently
  corrupting the frame; `csc` still emits larger functions because `rcc`
  sizes its frame from `maxslot`.  Large files therefore use `csc -> rcc`,
  and only cases `rvm` can hold are checked through the interpreter.
- Arguments are staged by `ARG` and copied into the callee's r0.. by `CALL`.
- A struct-returning function receives one hidden extra argument after its
  declared parameters: the destination word base.  It copies the result there
  and returns 0.
- `RET` returns the value in its operand to the caller's destination register.
- Array and struct-array indexing carry a length and trap with `bounds` when
  the index is outside the array.
- The VM validates magic, counts and table bounds; it is not a verifier for
  arbitrary hostile images.

## Opcodes

The primary opcodes are:

```text
CONST MOV ADD SUB MUL DIV LT GT EQ JZ JMP RET HALT
LOADG STOREG LOADA STOREA PRINT ARG CALL LOADL STOREL
INC DEC ADDI SUBI MULI
JLT JGE JGT JLE JEQ JNE
JLT_I JGE_I JGT_I JLE_I JEQ_I JNE_I
STOREA_I NOP PRINTS PRINTN PRINTV
NATIVE NATIVER LOADD STORED
SHLI SHRI FMUL FDIV PRINTFIX PRINTFIXV
BOUNDS PRINTFIXN MOD
LOADB STOREB STRCPY STRCAT STRLEN STRCMP ATOI PRINTSTR
NE LE GE NATIVEC
```

Field conventions worth noting:

- `LOADA offset, index, len, dst`
- `STOREA offset, index, value, len`
- `STOREA_I offset, index, imm, len`
- `LOADD base, field, -, dst`
- `STORED base, field, value, -`
- `JMP target`; `JZ value, target`; fused branches use `c` as target.
- `CALL funcid, dst, argc`
- `BOUNDS index, len`
- `LOADB base, index, -, dst` (byte from the arena)
- `STOREB base, index, value, -`
- `STRCPY dstptr, srcptr, cap, dst` (strlcpy semantics; length in `dst`)
- `STRCAT dstptr, srcptr, cap, dst` (strlcat semantics; length in `dst`)
- `STRLEN srcptr, -, -, dst`
- `STRCMP aptr, bptr, -, dst`
- `ATOI srcptr, -, -, dst`
- `PRINTSTR ptr` (no trailing newline)
- `NATIVE id, arg0, arg1, arg2`
- `NATIVER id, arg0, arg1, dst`

String pointers are arena byte offsets in a register.  A negative offset is a
null string.  `LOADB`/`STOREB` carry the array base as an immediate and the
index in a register; `BOUNDS` is emitted first by the compiler.

## Native ids

```text
0  gpio_count     1  gpio_mode      2  gpio_write    3  gpio_read
4  adc_count      5  adc_read       6  pwm_count     7  pwm_set
8  pwm_off        9  sleep          10 uptime        11 run(path)
12 open(path)    13 create(path)  14 read(fd,buf,len)  15 write(fd,buf,len)
16 close(fd)     17 unlink(path)  18 capture(path,buf,cap)  19 readdir(idx,buf,len)  20 isdir(path)
```

`run(path)` spawns the named program, waits for it, and returns its exit code
(negative when the spawn fails).  It does **not** replace the caller: TinyOS's
`exec()` creates a child and `wait()` returns the status.  The argument is an
arena offset, not an int; `csc` checks that the source passes a string.

The native table is part of the ABI and must stay in sync with the TinyOS
port and with `rcc`.
