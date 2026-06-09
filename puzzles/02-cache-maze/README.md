# Puzzle 02: Cache Maze

## Objective

Use `perf` evidence to diagnose poor memory locality in a C++ image filter.

## Performance target

Reach at least **4x speedup** over the starter while producing the same
filtered-image checksum.

## Assignment

The program generates a 4096 by 4096 grayscale image and repeatedly applies a
3x3 box blur. The starter produces the correct result, but its memory traversal
leaves substantial performance on the table.

Create your workspace:

```sh
ptf start 02
```

This gives you:

```text
work/02/bad_reference.cpp
work/02/work.cpp
```

`bad_reference.cpp` is a convenient read-only reference. Make changes in
`work.cpp`.

### Correctness contract

Preserve:

- Image dimensions and number of blur rounds.
- The `pixel_value()` calculation.
- The 3x3 box-blur calculation and unchanged border pixels.
- The final image contents and checksum.

You may change loop structure, traversal order, indexing, and temporary
storage.

## Suggested process

1. Run `ptf 02 work` and record the baseline.
2. Inspect how image addresses change in the inner loop.
3. Run `ptf perf-stat 02 work`.
4. Run `ptf perf-record 02 work` and inspect the hot blur loop.
5. Edit `work/02/work.cpp`.
6. Profile the new version and compare elapsed time, IPC, and L1 data-cache
   miss rate.
7. Submit the result with `ptf check 02`.

Use the hints progressively. Read `ptf reveal 02` after completing the target.
