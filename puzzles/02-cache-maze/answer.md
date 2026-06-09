# Answer: Cache Maze

## Diagnosis

The image is stored in row-major order, while the starter advances down a
column in its innermost loop. Consecutive output pixels are 4096 elements
apart. Their 3x3 input neighborhoods are also far apart, so the loop gets
little reuse from each fetched cache line.

## Strongest evidence

`perf stat -d` should show worse runtime and lower IPC for the starter.
Available cache and TLB counters may also increase. `perf record -g` should
place most samples in the blur loop.

`strace` remains quiet because the expensive work consists of user-space memory
accesses.

## Fix

Traverse each image row from left to right. Neighboring output pixels then
reuse most of the same input neighborhood and write adjacent destination
elements. The reference changes the order of the two image loops; further
optimizations can reduce indexing overhead or process several pixels together.

## Validation

Both versions print the same position-sensitive image checksum. The optimized
version should run faster and improve the available cache, TLB, or IPC
evidence.
