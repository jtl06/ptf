# perf-mystery Agent Guide

## Purpose

`perf-mystery` is an active Linux performance lab inspired by CS:APP systems
labs. Learners receive correct but slow C++ starter code. They profile it, edit
their own copy, and submit it to a correctness and performance grader.

The challenge loop is:

`profile -> explain -> edit -> test -> measure -> repeat`

## Main paths

- `ptf`: CLI, puzzle metadata, build logic, profilers, and grader.
- `pmystery.py`: compatibility entry point for the old command name.
- `puzzles/<slug>/src/bad.cpp`: starter implementation.
- `puzzles/<slug>/src/fixed.cpp`: reference implementation.
- `work/<id>/solution.cpp`: learner-owned editable source, ignored by Git.
- `build/<id>/`: generated binaries, ignored by Git.
- `runs/<id>/`: profiler evidence and lab notes, ignored by Git.

All benchmark implementations use C++17 and compile with `g++`.

## Learner workflow

```sh
ptf start 01
ptf 01 work
ptf strace 01 work
# edit work/01/solution.cpp
ptf check 01
```

`ptf start` copies the starter into `work/<id>/solution.cpp` and creates a lab
journal. It preserves an existing solution.

`ptf check`:

1. Compiles the working solution.
2. Compares its output with the reference output.
3. Measures median starter, solution, and reference runtimes.
4. Grades the puzzle-specific speedup target.

Profiling commands accept `bad`, `work`, and `fixed`. The `work` binary rebuilds
when `solution.cpp` is newer than its binary.

## Commands

```text
ptf help
ptf list
ptf start <id>
ptf build <id>
ptf run <id> <bad|work|fixed>
ptf strace <id> <bad|work|fixed>
ptf perf-stat <id> <bad|work|fixed>
ptf perf-record <id> <bad|work|fixed>
ptf check <id> [--runs N]
ptf compare <id>
ptf lesson <id>
ptf hint <id> [level]
ptf diagnose <id>
ptf journal <id> <bad|work|fixed>
ptf reveal <id>
```

Puzzle-first shortcuts:

- `ptf 01` shows lesson 01.
- `ptf 01 work` runs the learner solution.
- `ptf 01 bad` runs the starter.

## Targets

- Puzzle 01, Syscall Storm: 100x required, greater than 1000x stretch.
- Puzzle 02, Cache Maze: 4x speedup.
- Puzzle 03, Branch Lottery: 1.5x speedup.

Targets are relative to the starter measured during the same `check` command.
Exact runtimes remain machine-dependent.

Optional `stretch_speedup` metadata adds a separately reported stretch goal.
Required targets control pass/fail; stretch goals recognize further optimization.

## Puzzle behavior

### 01: Syscall Storm

- Starter reads an 8 MiB file one byte per `read()` call.
- Main evidence is the `read()` syscall count from `strace -c`.
- Input is generated deterministically and excluded from Git.

### 02: Cache Maze

- Starter follows a randomized dependent traversal through a large node vector.
- Its order-sensitive checksum requires the exact logical visit sequence.
- Learners may change physical layout and traversal mechanics.
- Main evidence includes runtime, IPC, cache/TLB symptoms, and hot traversal
  samples.

### 03: Branch Lottery

- Starter branches on the high bit of deterministic pseudo-random values.
- Main evidence is the branch-miss rate.
- The GCC optimization attribute keeps the starter branch visible.

## Correctness invariants

- Starter, learner, and reference variants must produce equivalent output.
- Every benchmark prints a checksum or result.
- Input and pseudo-random generation remain deterministic.
- Avoid undefined behavior.
- Preserve frame pointers for useful `perf record -g` stacks.
- Keep starter runtimes roughly between 0.2 and 5 seconds on common Linux
  systems.

## Validation

Run:

```sh
make clean
make
ptf compare 01
ptf compare 02
ptf compare 03
```

For each puzzle, also validate the grader by starting a workspace, copying the
reference algorithm into `solution.cpp`, and confirming `ptf check <id>` passes.

The project has been exercised on macOS for compilation and on the Linux x86
hosts `alcidae` and `aethia`. Use `alcidae` or `aethia` for remote validation.
Do not use `cancun`.

## Profiling constraints

`strace` and `perf` may be absent or restricted. Keep errors concise and
actionable.

`aethia` previously reported `perf_event_paranoid=4`, unsupported hardware
counters, and denied `perf record`. The CLI warns about unavailable events and
reports permission guidance.

PMU events vary across Intel, AMD, Graviton 3, and Graviton 4. Prefer portable
event categories and record architecture, kernel, compiler, and virtualization
context.

## Development rules

- Keep the CLI standard-library only.
- Add puzzle metadata and target speedups in `PUZZLES`.
- Add new benchmarks as C++17 `bad.cpp` and `fixed.cpp` pairs.
- Preserve learner files under `work/` during cleanup.
- Preserve lab notes under `runs/` during cleanup.
- Exclude generated inputs, binaries, evidence, and learner solutions from Git.
- Update the root README and puzzle lesson when changing the workflow.

An Arm Performix backend may later collect Graviton-specific PMU evidence while
using the same editable solution and grading flow.
