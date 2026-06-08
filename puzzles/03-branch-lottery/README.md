# Puzzle 03: Branch Lottery

## Objective

Measure unpredictable control flow with hardware counters, then rewrite the hot
C++ loop to reduce branch misses.

## Performance target

Reach at least **1.5x speedup** over the starter while printing the same
checksum.

## Assignment

The starter processes deterministic pseudo-random values. Its hot loop performs
the intended calculation and creates difficult branch outcomes.

Create your editable solution:

```sh
ptf start 03
```

Then investigate and optimize `work/03/solution.cpp`.

## Suggested process

1. Run `ptf 03 work` and record the baseline.
2. Measure `branches` and `branch-misses` with `ptf perf-stat 03 work`.
3. Calculate the branch-miss percentage.
4. Identify the data-dependent branch in the hot loop.
5. Edit `work/03/solution.cpp` while preserving the calculation.
6. Measure the counters and runtime again.
7. Submit the result with `ptf check 03`.

Use the hints progressively. Read `ptf reveal 03` after completing the target.
