# Answer: Cache Maze

## Diagnosis

The bad version suffers from poor memory locality and serialized pointer
chasing. Its next address cannot be known until the current node arrives, which
limits memory-level parallelism. The randomized order also defeats spatial
locality and hardware prefetching.

## Strongest evidence

`perf stat -d` should show worse runtime and lower IPC for the bad version.
Depending on CPU and kernel event support, cache and TLB symptoms may also be
worse. `perf record -g` should place most samples in the pointer-chain traversal.
Exact cache event names and availability vary by processor.

`strace` is mostly quiet because the costly work happens after allocation, in
user-space loads rather than repeated system calls.

## Fix

Recreate the shuffled logical visit order during setup, then store values
contiguously in that order. The repeated computation processes the same
sequence while the CPU receives a sequential stream of cache lines.

## Validation

The order-sensitive checksum confirms that both variants process the same visit
sequence. The fixed version should run faster with higher IPC and less severe
cache/TLB evidence where those counters are available.
