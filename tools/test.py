#!/usr/bin/env python3
"""Build csc3 + rirvm on the host and run the golden tests."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
CC = os.environ.get("CC", "gcc")
EXE = ".exe" if os.name == "nt" else ""


def compile_one(src: Path, out: Path) -> None:
    subprocess.check_call([
        CC, "-std=gnu11", "-O2", "-I", str(ROOT / "include"),
        str(src), "-o", str(out),
    ])


def run(cmd) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, errors="replace")


def main() -> int:
    BUILD.mkdir(exist_ok=True)
    csc3 = BUILD / ("csc3" + EXE)
    rirvm = BUILD / ("rirvm" + EXE)
    print("building csc3 ...")
    compile_one(ROOT / "src" / "csc3.c", csc3)
    print("building rirvm ...")
    compile_one(ROOT / "src" / "rirvm.c", rirvm)
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
    ]

    failed = 0
    for name, needles in cases:
        src = ROOT / "tests" / (name + ".c")
        image = BUILD / name          # deliberately no extension
        if image.exists():
            image.unlink()
        r = run([str(csc3), str(src), str(image)])
        if r.returncode != 0:
            print(f"FAIL {name}: csc3\n{r.stdout}")
            failed += 1
            continue
        if not image.exists() or image.read_bytes()[:4] != b"RIR2":
            print(f"FAIL {name}: output is not RIR2")
            failed += 1
            continue
        r = run([str(rirvm), str(image)])
        missing = [n for n in needles if n not in r.stdout]
        if r.returncode != 0 or missing:
            print(f"FAIL {name}: rirvm rc={r.returncode} missing={missing}\n{r.stdout}")
            failed += 1
        else:
            print(f"PASS {name}")

    # Diagnostics must name the source line for both parse and codegen errors.
    for name in ("badline", "badvar"):
        src = ROOT / "tests" / (name + ".c")
        image = BUILD / name
        if image.exists():
            image.unlink()
        r = run([str(csc3), str(src), str(image)])
        if r.returncode == 0 or "line 3" not in r.stdout:
            print(f"FAIL {name}: rc={r.returncode}\n{r.stdout}")
            failed += 1
        else:
            print(f"PASS {name} (line 3)")

    # Out-of-bounds must be diagnosed by the image's BOUNDS op, not a crash.
    src = ROOT / "tests" / "sb3.c"
    image = BUILD / "sb3"
    if image.exists():
        image.unlink()
    r = run([str(csc3), str(src), str(image)])
    if r.returncode != 0:
        print(f"FAIL sb3: csc3\n{r.stdout}")
        failed += 1
    else:
        r = run([str(rirvm), str(image)])
        if r.returncode != 1 or "bounds" not in r.stdout:
            print(f"FAIL sb3: rirvm rc={r.returncode}\n{r.stdout}")
            failed += 1
        else:
            print("PASS sb3 (bounds)")

    # Legacy Python interpreter, kept until the frontend is unified.
    r = run([str(py), str(ROOT / "tests" / "py" / "demo.py")])
    py_need = ["sum: 13", "fib(10): 55", "done"]
    py_missing = [n for n in py_need if n not in r.stdout]
    if r.returncode != 0 or py_missing:
        print(f"FAIL py: rc={r.returncode} missing={py_missing}\n{r.stdout}")
        failed += 1
    else:
        print("PASS py demo")

    print("ALL TESTS PASS" if failed == 0 else f"{failed} TEST(S) FAILED")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
