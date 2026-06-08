# Answer: Branch Lottery

## Diagnosis

The hot branch depends on the high bit of deterministic pseudo-random data, so
its outcome is close to 50/50 and difficult for the branch predictor to learn.
Mispredictions discard speculative work and restart the pipeline.

## Strongest evidence

Use the puzzle's `perf-stat` command, whose default event group normally includes
branches and branch misses, or request them directly with
`perf stat -e branches,branch-misses`. The bad version should show a much higher
branch-miss count and miss percentage. Exact counts vary by CPU and
virtualization support.

## Fix

For a 32-bit value `v`, `mask = 0 - (v >> 31)` is either all zero bits or all
one bits. `v ^ mask` therefore selects `v` for the low half and `~v` for the
high half without a data-dependent branch.

## Validation

Both variants print the same checksum. The fixed version should reduce branch
misses and usually improve runtime. Inspect generated code if the compiler or
architecture produces surprising counter results.
