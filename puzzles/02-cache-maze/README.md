# Puzzle 02: Cache Maze

## Learning objective

Learn how poor memory locality and dependent pointer chasing appear in `perf`,
and why `strace` can be quiet for a CPU or memory bottleneck.

## Scenario

The bad program links a large vector into a deterministic randomized traversal
order. Every next load depends on the previous node. The fixed program performs
the same value accumulation over contiguous storage. Both print the same
checksum.

## Suggested workflow

1. Predict what `strace -c` will show.
2. Compare wall-clock runtimes.
3. Run `ptf perf-stat 02 bad`.
4. Collect samples with `ptf perf-record 02 bad`.
5. Compare IPC and available cache/TLB counters with the fixed version.

Follow:

`hypothesis -> tool -> evidence -> diagnosis -> fix -> validation`
