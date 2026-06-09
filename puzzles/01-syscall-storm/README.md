# Puzzle 01: Syscall Storm

## Objective

Use `strace` evidence to locate excessive syscall overhead, then optimize the
C++ implementation.

## Performance target

Reach at least **100x speedup** over the starter while printing the same newline
count.

The stretch goal is to **exceed 1000x speedup**. Use `strace -c` to confirm that
the result comes from reducing `read()` calls rather than timing noise.

## Assignment

The program counts newline characters in a deterministic text file. The starter
produces the correct result and takes several seconds on a typical Linux
machine.

Create your editable workspace:

```sh
ptf start 01
```

Then investigate and optimize `work/01/work.cpp`.

## Suggested process

1. Run `ptf 01 work` and record the baseline.
2. Predict which kernel interaction dominates runtime.
3. Run `ptf strace 01 work`.
4. Connect the dominant syscall count to a line of C++.
5. Edit `work/01/work.cpp`.
6. Repeat the run and `strace` measurements.
7. Submit the result with `ptf check 01`.

Use `ptf hint 01`, `ptf hint 01 2`, and `ptf hint 01 3` when you need a nudge.
Read `ptf reveal 01` after completing the target.
