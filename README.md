# perf-mystery

`perf-mystery` is a local CTF-style lab for learning Linux performance
debugging. Each puzzle gives you a slow program, profiling tools, progressive
hints, and an equivalent optimized version.

The lab develops a repeatable investigation process:

> hypothesis -> tool -> evidence -> diagnosis -> fix -> validation

The goal is to explain why a program is slow using observable evidence. Runtime
establishes the symptom. Tool output supports the diagnosis. The fixed version
tests whether the predicted behavior and metric improve.

## Learning objectives

After completing the puzzles, you should be able to:

- Form a specific performance hypothesis before collecting data.
- Select `strace`, `perf stat`, or `perf record` based on that hypothesis.
- Separate syscall-heavy behavior from CPU and memory bottlenecks.
- Interpret syscall counts, IPC, cache symptoms, and branch-miss rates.
- Connect profiler output to a source-level cause.
- Predict which metric should change after a fix.
- Validate that an optimization preserves program results.
- Record an investigation clearly enough for another person to reproduce it.

The puzzles emphasize tool selection as much as tool operation. A useful
profiling command answers a specific question:

- How often does the program enter the kernel?
- How efficiently does the CPU retire instructions?
- Where are samples concentrated?
- Does the optimized version improve the expected metric?

## Puzzles

### 01: Syscall Storm

**Objective:** Recognize syscall overhead and use `strace -c` to quantify it.

The program counts newlines in a generated text file. The slow version reads one
byte per syscall. The optimized version reads 64 KiB at a time.

Look for:

- The total number of `read()` calls.
- The relationship between input size and syscall count.
- The change in syscall count after buffering.

### 02: Cache Maze

**Objective:** Recognize poor memory locality and dependent pointer chasing in
`perf` evidence.

The slow version traverses a randomized linked structure. The optimized version
performs equivalent work over contiguous storage.

Look for:

- Runtime and instructions per cycle.
- Available cache and TLB symptoms.
- Samples concentrated in the traversal loop.
- Quiet syscall activity during expensive user-space work.

### 03: Branch Lottery

**Objective:** Measure unpredictable branches and validate a branchless
equivalent.

The slow version branches on deterministic pseudo-random data. The optimized
version uses a mask to compute the same result.

Look for:

- `branches` and `branch-misses`.
- Branch misses as a percentage of branch instructions.
- Matching checksums across both implementations.
- The expected counter change after removing the data-dependent branch.

## Lab workflow

1. Read the lesson with `ptf lesson <id>`.
2. Create notes with `ptf journal <id> bad`.
3. Write down a bottleneck hypothesis and the evidence you expect.
4. Run the slow version to capture its runtime and checksum.
5. Choose a profiling command that tests the hypothesis.
6. Record the decisive metrics or output patterns.
7. Complete the diagnosis quiz before reading the answer.
8. Compare the optimized version and inspect the predicted metric.
9. Write a takeaway that connects source code, evidence, and hardware behavior.

Progressive hints preserve the investigation:

```sh
ptf hint 02
ptf hint 02 2
ptf hint 02 3
```

## Requirements

- Linux
- Python 3
- `gcc`, `g++`, and `make`
- `strace` for syscall exercises
- Linux `perf` for hardware counters and sampling

The CLI detects missing tools and reports common `perf` permission restrictions,
including `perf_event_paranoid` and unavailable PMU events.

## Setup

From the repository root:

```sh
make
make install
```

`make install` creates `~/.local/bin/ptf` as a symlink to the checkout. Ensure
`~/.local/bin` is on `PATH`. You can choose another prefix:

```sh
make install PREFIX=/another/path
```

You can also run `./ptf` directly from the checkout.

## Example session

```sh
ptf list
ptf lesson 01
ptf journal 01 bad
ptf run 01 bad
ptf strace 01 bad
ptf diagnose 01
ptf compare 01
ptf strace 01 fixed
ptf reveal 01
```

For CPU and memory analysis:

```sh
ptf perf-stat 02 bad
ptf perf-record 02 bad
perf report -i runs/02/bad/perf.data
```

Puzzle IDs accept `1`, `01`, or a full slug such as `01-syscall-storm`.

Generated binaries live under `build/`. Profiling evidence and lab notes live
under `runs/`. Puzzle 01 creates its deterministic input during the first
build. Generated inputs and run artifacts are excluded from Git.

## Comparing systems

The puzzle sources build on x86-64 and AArch64 with GCC. This makes the same
investigation useful across Intel, AMD, Graviton 3, and Graviton 4 systems.

Record the following context before comparing results:

- CPU model and architecture
- Kernel version
- Compiler version and flags
- Virtual machine or container environment
- `perf_event_paranoid` value
- Available PMU events

Event names, counts, and availability vary across processors and virtualized
environments. Start with portable categories such as cycles, instructions, IPC,
branches, and branch misses. Compare each slow version with its optimized
version on the same system.

The expected diagnosis remains stable across architectures:

- Syscall Storm produces excessive `read()` calls.
- Cache Maze serializes poor-locality memory accesses.
- Branch Lottery creates difficult-to-predict branch outcomes.

## Future direction

A future collector interface could add Arm Performix as a backend for guided
Arm analysis. It could collect architecture-specific PMU events, write evidence
into the existing run directories, and provide Graviton-focused questions while
preserving the same lesson and journal workflow.
