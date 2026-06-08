# Puzzle 03: Branch Lottery

## Learning objective

Learn how unpredictable branches appear in hardware performance counters and
how to validate a branchless equivalent.

## Scenario

Both programs generate the same deterministic pseudo-random values. Values
below the high-bit threshold contribute unchanged; values above it contribute
their bitwise complement. The bad version expresses this as an unpredictable
branch. The fixed version uses a mask.

## Suggested workflow

1. Compare runtimes and verify matching checksums.
2. Run `ptf perf-stat 03 bad`.
3. Compare the default `branches` and `branch-misses` counters with the fixed
   version. If your `perf` build omits them, run
   `perf stat -e branches,branch-misses -- build/03/bad` directly.
4. Express branch misses as a percentage of branch instructions.
5. Predict how the source can compute the same result without a data-dependent
   branch.

Follow:

`hypothesis -> tool -> evidence -> diagnosis -> fix -> validation`
