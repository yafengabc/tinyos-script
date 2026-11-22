# rvm — RIR2 interpreter

`rvm` executes a RIR2 image produced by `csc`:

```text
rvm image [reps]
```

`reps` (default 1) runs the program again from the initial data image; it is
only for timing.  With `reps == 1` the interpreter also prints the summary line
below; with more repetitions it stays quiet between runs.

## Output

Program output goes to stdout unchanged.  The last line is a summary:

```text
result=17 ir=10 reps=1 exec_ms=0
```

- `result` — `main`'s return value;
- `ir` — instructions in the image;
- `reps` — repetitions requested;
- `exec_ms` — host milliseconds for the whole run.

The summary is an interpreter convenience: native images from `rcc` print only
the program's own output, so tests that compare both sides strip this line.

## Limits

| Resource | Limit |
|---|---:|
| Instructions (whole program) | paged from the image; header cap 65,536 |
| Global words | 512 |
| String pool | 1024 B |
| Mutable arena | 512 B |
| Functions | 256 |
| Spill slots per frame | 16 |
| Call frames | 32 |

The instruction array is **not** held in RAM.  `rvm` keeps a small page cache
(`PAGE_IR` = 256 instructions, one 5120-byte read per fault; 8 slots on the
host, 2 on the board) and maps the page holding `pc`.  A page range check costs
two subtractions and one compare per instruction, which is why `benchloop`
reads about 15-30% slower than the old whole-image build; everything else is
unchanged.

This replaced a hard 256-instruction ceiling, so the four programs that used to
be `native-only` (`bigcode` 535 IR, `many100` 898, `bigir` 1436, `hugeir` 2948)
are now checked by `rvm` as well as `rcc` in `tools/test.py`.  The two board
slots mean a program larger than 512 instructions can still run, it just refills
pages on jumps between distant functions.

Other limits are enforced at load time: the header must fit the file, and a
`pc` outside `[0, nir)` stops the run with `rvm: pc out of range` instead of
reading memory that is not there.  A truncated image or a bad header stops with
`rvm: bad or missing image`.

An image that exceeds one of the table's windows is still valid RIR2 — `rcc`
builds it with no such limit — so `rvm` names the limit that was hit and points
at the native path:

```text
rvm: global words 600 exceeds rvm limit 512; use csc -> rcc
```

Programs that need more than rvm's window therefore go through `csc -> rcc`;
the interpreter is only for the small programs it can hold in memory.

## Execution model

- `main` receives no arguments; `argc`/`argv` setup is a TinyOS concern.
- `print`/`printf` write to stdout; `puts` adds a newline.
- Strings are arena offsets; a bounds violation prints `bounds` and exits 1.
- Native ids (GPIO/ADC/PWM/sleep/uptime) return 0 on the host; they exist so the
  same image links and runs — behaviour lives in `rcc`/TinyOS.
- Divide by zero in both `/` and `%` yields 0; division follows C truncation.
  `INT_MIN / -1` yields `INT_MIN` and `INT_MIN % -1` yields 0, matching the
  RV32/Thumb-2 divide instructions and avoiding a host integer-overflow trap.
  `csc` applies the same rules when folding constants.

Exit status is 0 on success, 1 for a load error or a bounds failure, 2 for a
usage error.

## Role in testing

`rvm` is the golden model for `csc` and for the native backends: for every
interpreter-compatible program the ARM/RV32 image must print the same lines
(minus the summary).  `tools/test.py` checks `rvm` first and only then builds
the native image; programs that need a TinyOS filesystem or child processes
(`capture`, file IO, `readdir`) are the only ones left to the target.
