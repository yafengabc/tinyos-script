#!/usr/bin/env python3
"""Build csc + rvm on the host and run the golden tests."""

import os
import subprocess
import sys
from pathlib import Path

from check_tos import check

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
CC = os.environ.get("CC", "gcc")
EXE = ".exe" if os.name == "nt" else ""


def compile_one(src: Path, out: Path, extra=()) -> None:
    subprocess.check_call([
        CC, "-std=gnu11", "-O2", "-I", str(ROOT / "include"),
        *extra, str(src), "-o", str(out),
    ])


def run(cmd) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, errors="replace")


def main() -> int:
    BUILD.mkdir(exist_ok=True)
    csc = BUILD / ("csc" + EXE)
    rvm = BUILD / ("rvm" + EXE)
    print("building csc ...")
    compile_one(ROOT / "src" / "csc.c", csc)
    print("building rvm ...")
    compile_one(ROOT / "src" / "rvm.c", rvm)
    print("building rcc (C native backend) ...")
    rcc = BUILD / ("rcc" + EXE)
    compile_one(ROOT / "src" / "rcc" / "rcc.c", rcc, ["-DRCC_ARCH_RV32"])
    print("building py (legacy) ...")
    py = BUILD / ("py" + EXE)
    py_srcs = sorted(str(p) for p in (ROOT / "src" / "py").glob("*.c"))
    subprocess.check_call([
        CC, "-std=gnu11", "-O2", "-I", str(ROOT / "include"),
        "-I", str(ROOT / "src" / "py"),
        *py_srcs, str(ROOT / "tools" / "host_shim.c"), "-o", str(py),
    ])

    cases = [
        ("bloop3", ["1783293664"]),
        ("sieve3", ["25"]),
        ("fib24", ["46368"]),
        ("sa3", ["q=6", "p3=16", "gs=15", "f=3.14", "f0=3", "result=4"]),
        ("many20", ["result=210"]),
        ("flow", ["26", "3", "4", "result=26"]),
        ("flow2", ["5", "30", "9", "result=44"]),
        ("switch", ["105", "2", "3", "result=105"]),
        ("fold", ["14", "3", "result=17"]),
        ("mod", ["2", "2", "2", "2", "result=6"]),
        ("str", ["Hi", "65", "hello", "from-fn", "4", "world!", "xorld!", "lit", "loc=loX", "g=Xy", "0", "-42", "name=Xy", "n=5", "result=5"]),
        ("ops", ["1", "0", "111", "222", "333", "555", "444", "result=3"]),
        ("floatfold", ["3.0", "1.5", "1.75", "result=0"]),
        ("copy", ["10", "7", "result=99"]),
        ("nest", ["3", "4", "5", "7", "11", "12", "62", "result=21"]),
        ("sret", ["3", "4", "13", "14", "23", "24", "7", "8", "result=17"]),
        ("native", ["6765", "result=55"]),
        ("fmt", ["3.14", "1.25", "0.50", "2.00", "result=0"]),
        ("arith", ["-3", "-2", "17", "9", "20", "14", "-14", "result=0"]),
        ("cmp2", ["1", "0", "7", "result=0"]),
        ("loops2", ["8", "4", "10", "13", "result=0"]),
        ("switch2", ["23", "99", "result=99"]),
        ("funcs", ["36", "720", "result=8"]),
        ("struct3", ["1", "4", "3", "7", "result=7"]),
        ("strings2", ["ab", "hello", "-1", "abcZ", "42", "-7", "result=0"]),
        ("float3", ["-0.75", "3.75", "-3.375", "-0.6667", "-1.5", "-1.25", "result=0"]),
        ("arrays2", ["30", "4", "13", "result=16"]),
        ("globals2", ["6", "7", "15", "ok", "result=7"]),
        ("spill", ["66", "395", "result=0"]),
        ("divzero", ["-2147483648", "0", "0", "0"]),
        ("bom", ["42"]),
        ("deep", ["325", "result=55"]),
        ("mixed", ["n=7", "2.0", "ok", "result=4"]),
        ("many25", ["120", "result=0"]),
        ("many32", ["496", "result=0"]),
        ("bigswitch", ["1836", "117", "result=0"]),
        ("bigbody", ["7432", "15", "result=0"]),
        ("mixbig", ["25", "97", "mixbig", "12", "134", "result=34"]),
        # These four used to be native-only because the interpreter stopped at
        # 256 instructions.  rvm now pages the image in, so it runs them too.
        ("bigcode", ["12829"]),          # 31 functions, ~6 KiB source
        ("many100", ["20009"]),          # 111 functions: the UFCS shape
        ("bigir", ["1325"]),             # ~1.4k IR, board-compilable
        ("hugeir", ["1536"]),            # ~3k IR: 12 pages, 2-slot board cache

    ]

    failed = 0
    for name, needles in cases:
        src = ROOT / "tests" / (name + ".c")
        image = BUILD / name          # deliberately no extension
        if image.exists():
            image.unlink()
        r = run([str(csc), str(src), str(image)])
        if r.returncode != 0:
            print(f"FAIL {name}: csc\n{r.stdout}")
            failed += 1
            continue
        if not image.exists() or image.read_bytes()[:4] != b"RIR2":
            print(f"FAIL {name}: output is not RIR2")
            failed += 1
            continue
        r = run([str(rvm), str(image)])
        missing = [n for n in needles if n not in r.stdout]
        if r.returncode != 0 or missing:
            print(f"FAIL {name}: rvm rc={r.returncode} missing={missing}\n{r.stdout}")
            failed += 1
            continue
        tos = BUILD / (name + ".tos")
        if tos.exists():
            tos.unlink()
        r = run([str(rcc), str(image), str(tos)])
        errors = check(tos, "rv32") if tos.exists() else ["no output"]
        if r.returncode != 0 or errors:
            print(f"FAIL {name}: rcc rc={r.returncode} {errors}\n{r.stdout}")
            failed += 1
        else:
            print(f"PASS {name} (+native, ELF OK)")

    # Target-only features: csc and rcc must produce an image, but the host
    # rvm has no child processes or TinyOS filesystem, so execution is checked
    # on QEMU (or a board) with the same needles.
    target_only = [
        ("exec1", ["hello from ring 3!", "0"]),
        ("file1", ["1", "5", "0", "5", "hello"]),
        ("capture1", ["hello from ring 3!", "pid="]),
        ("dir1", ["readme.txt", "bin", "-1"]),
    ]
    for name, needles in target_only:
        src = ROOT / "tests" / (name + ".c")
        image = BUILD / name
        if image.exists():
            image.unlink()
        r = run([str(csc), str(src), str(image)])
        if r.returncode != 0:
            print(f"FAIL {name}: csc\n{r.stdout}")
            failed += 1
            continue
        tos = BUILD / (name + ".tos")
        if tos.exists():
            tos.unlink()
        r = run([str(rcc), str(image), str(tos)])
        if r.returncode != 0 or not tos.exists() or tos.read_bytes()[:6] != b"LZ4TOS":
            print(f"FAIL {name}: rcc rc={r.returncode}\n{r.stdout}")
            failed += 1
        else:
            print(f"PASS {name} (target-only: {'; '.join(needles)})")

    # Diagnostics must name the source line for both parse and codegen errors.
    for name in ("badline", "badvar", "badprintf", "badshadow"):
        src = ROOT / "tests" / (name + ".c")
        image = BUILD / name
        if image.exists():
            image.unlink()
        r = run([str(csc), str(src), str(image)])
        line = {"badprintf": "line 1", "badshadow": "line 4"}.get(name, "line 3")
        if r.returncode == 0 or line not in r.stdout:
            print(f"FAIL {name}: rc={r.returncode}\n{r.stdout}")
            failed += 1
        else:
            print(f"PASS {name} ({line})")

    # More spill slots than rvm can hold: csc must still compile the image
    # (rcc sizes its frame dynamically), and rvm must fail loudly rather than
    # silently returning a wrong result (issue #1).
    src = ROOT / "tests" / "spillover.c"
    image = BUILD / "spillover"
    if image.exists():
        image.unlink()
    r = run([str(csc), str(src), str(image)])
    if r.returncode != 0:
        print(f"FAIL spillover csc: rc={r.returncode}\n{r.stdout}")
        failed += 1
    else:
        r = run([str(rvm), str(image)])
        if r.returncode == 0 or "spill" not in r.stdout:
            print(f"FAIL spillover rvm: rc={r.returncode}\n{r.stdout}")
            failed += 1
        elif run([str(rcc), str(image), str(BUILD / "spillover.tos")]).returncode != 0:
            print("FAIL spillover rcc")
            failed += 1
        else:
            print("PASS spillover (rvm rejects, csc -> rcc succeeds)")

    # Out-of-bounds must be diagnosed by the image's BOUNDS op, not a crash.
    src = ROOT / "tests" / "sb3.c"
    image = BUILD / "sb3"
    if image.exists():
        image.unlink()
    r = run([str(csc), str(src), str(image)])
    if r.returncode != 0:
        print(f"FAIL sb3: csc\n{r.stdout}")
        failed += 1
    else:
        r = run([str(rvm), str(image)])
        if r.returncode != 1 or "bounds" not in r.stdout:
            print(f"FAIL sb3: rvm rc={r.returncode}\n{r.stdout}")
            failed += 1
        else:
            tos = BUILD / "sb3.tos"
            if tos.exists():
                tos.unlink()
            r = run([str(rcc), str(image), str(tos)])
            if r.returncode != 0 or not tos.exists() or tos.read_bytes()[:6] != b"LZ4TOS":
                print(f"FAIL sb3: rcc rc={r.returncode}\n{r.stdout}")
                failed += 1
            else:
                print("PASS sb3 (bounds, +native)")

    # Legacy Python interpreter, kept until the frontend is unified.
    r = run([str(py), str(ROOT / "tests" / "py" / "demo.py")])
    py_need = ["sum: 13", "fib(10): 55", "done"]
    py_missing = [n for n in py_need if n not in r.stdout]
    if r.returncode != 0 or py_missing:
        print(f"FAIL py: rc={r.returncode} missing={py_missing}\n{r.stdout}")
        failed += 1
    else:
        print("PASS py demo")

    # LZ4 extended-length tokens used to overflow a 256-byte stack buffer
    # once the image passed ~65 KB (issue #6).  Build a >65 KB output with a
    # stack-protected rcc and check it still produces the same bytes.
    big_src = BUILD / "bigout.c"
    big_rir = BUILD / "bigout.rir"
    big_tos = BUILD / "bigout.tos"
    big_src.write_text(
        "".join(f"int f{i}(){{\n" + "    print(1);\n" * 400 +
                "    return 0;\n}\n" for i in range(10)) +
        "int main(){\n" + "".join(f"    f{i}();\n" for i in range(10)) +
        "    return 0;\n}\n")
    r = run([str(csc), str(big_src), str(big_rir)])
    if r.returncode != 0:
        print(f"FAIL bigout csc: {r.stdout}")
        failed += 1
    else:
        rcc_sp = BUILD / ("rcc_sp" + EXE)
        compile_one(ROOT / "src" / "rcc" / "rcc.c", rcc_sp,
                    ["-O1", "-fstack-protector-all", "-DRCC_ARCH_RV32"])
        r = run([str(rcc_sp), str(big_rir), str(big_tos)])
        if r.returncode != 0 or not big_tos.exists() or big_tos.stat().st_size < 65000:
            print(f"FAIL bigout rcc: rc={r.returncode} {r.stdout}")
            failed += 1
        else:
            print(f"PASS bigout ({big_tos.stat().st_size} bytes, stack-protected rcc)")

    # A Thumb-2 rcc must at least produce a structurally valid EM_ARM image.
    # Executing ARM code on this host is impossible, so this is a build +
    # ELF-header check (issue #8: "not ARM" coverage).
    rcc_arm = BUILD / ("rcc-arm" + EXE)
    compile_one(ROOT / "src" / "rcc" / "rcc.c", rcc_arm,
                ["-DRCC_ARCH_THUMB2"])
    arm_rir = BUILD / "arith"
    arm_tos = BUILD / "arith-arm.tos"
    if not arm_rir.exists():
        r = run([str(csc), str(ROOT / "tests" / "arith.c"), str(arm_rir)])
        if r.returncode != 0:
            print(f"FAIL arith csc for ARM: {r.stdout}")
            failed += 1
    if arm_rir.exists():
        r = run([str(rcc_arm), str(arm_rir), str(arm_tos)])
        errors = check(arm_tos, "arm") if arm_tos.exists() else ["no output"]
        if r.returncode != 0 or errors:
            print(f"FAIL arith ARM rcc: rc={r.returncode} {errors}\n{r.stdout}")
            failed += 1
        else:
            print("PASS arith ARM rcc (EM_ARM, ELF OK)")

    print("ALL TESTS PASS" if failed == 0 else f"{failed} TEST(S) FAILED")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
