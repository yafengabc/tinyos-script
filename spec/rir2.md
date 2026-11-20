# RIR2 image format

RIR2 is the portable output of `csc3` and the input of `rirvm` (and, later,
`irc`).  It is detected by magic, not by a filename extension.

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
| 24 | reserved | 0 |

## Layout

```text
header (28)
nir * 20-byte instruction records
nfuncs * 4-byte entry PCs
strsize bytes of NUL-terminated strings
```

An instruction record is five int32s: `op, a, b, c, d`.  Operand meaning is
opcode-specific.  Branches store absolute instruction indices in the final
image.  CALL stores a function id in `a`; the VM resolves it through the
function table.

## Execution model

- One frame per call, 32 frames; frame 0 is main.
- 16 registers per frame; r13–r15 are spill scratch during execution of
  rewritten code.
- Arguments are staged by `ARG` and copied into the callee's r0.. by `CALL`.
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
BOUNDS PRINTFIXN
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
- `NATIVE id, arg0, arg1, arg2`
- `NATIVER id, arg0, arg1, dst`

## Native ids

```text
0  gpio_count     1  gpio_mode      2  gpio_write    3  gpio_read
4  adc_count      5  adc_read       6  pwm_count     7  pwm_set
8  pwm_off        9  sleep          10 uptime
```

The native table is part of the ABI and must stay in sync with the TinyOS
port and with `irc`.
