# Puzzle 02: Cache Maze

## Objective

Use `perf` evidence to diagnose dependent pointer chasing and improve the C++
data layout.

## Performance target

Reach at least **4x speedup** over the starter while printing the same checksum.

## Assignment

The starter builds a large data structure and traverses it repeatedly. The
result is correct, and the access pattern leaves substantial performance
available.

Create your editable solution:

```sh
ptf start 02
```

Then investigate and optimize `work/02/solution.cpp`.

## Suggested process

1. Run `ptf 02 work` and record the baseline.
2. Write down what you expect from syscall activity, IPC, and cache behavior.
3. Run `ptf perf-stat 02 work`.
4. Run `ptf perf-record 02 work` and inspect the hot traversal.
5. Edit the representation or traversal in `work/02/solution.cpp`.
6. Profile the new version and compare the expected metrics.
7. Submit the result with `ptf check 02`.

Use the hints progressively. Read `ptf reveal 02` after completing the target.
