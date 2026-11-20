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
| Instructions (whole program) | 256 |
| Global words | 512 |
| String pool | 1024 B |
| Mutable arena | 512 B |
| Functions | 256 |

`rvm` rejects an image outside these bounds (`rvm: bad or missing image`)
instead of running it partially.  The 256-instruction ceiling is deliberate:
the interpreter is a size-conscious reference, not the target for large
programs.  Anything bigger is verified with `rcc` on QEMU or hardware; the host
runner marks those tests `native-only`.

## Execution model

- `main` receives no arguments; `argc`/`argv` setup is a TinyOS concern.
- `print`/`printf` write to stdout; `puts` adds a newline.
- Strings are arena offsets; a bounds violation prints `bounds` and exits 1.
- Native ids (GPIO/ADC/PWM/sleep/uptime) return 0 on the host; they exist so the
  same image links and runs — behaviour lives in `rcc`/TinyOS.
- Divide by zero in `%` yields 0; division follows C truncation.

Exit status is 0 on success, 1 for a load error or a bounds failure, 2 for a
usage error.

## Role in testing

`rvm` is the golden model for `csc` and for the native backends: for every
interpreter-compatible program the ARM/RV32 image must print the same lines
(minus the summary).  `tools/test.py` checks `rvm` first and only then builds
the native image.
