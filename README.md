# perf-mystery

`perf-mystery` is a hands-on Linux performance lab inspired by the systems labs
in CS:APP. Every puzzle starts with working C++ code that is too slow. Your job
is to investigate the program, change the code, and meet a performance target
while preserving the result.

The challenge loop is:

> profile -> explain -> edit -> test -> measure -> repeat

Runtime tells you whether the target was met. `strace` and `perf` provide the
evidence needed to choose an effective code change.

## What you practice

- Turning a runtime symptom into a testable bottleneck hypothesis.
- Choosing a profiling tool that can confirm or reject that hypothesis.
- Connecting syscall counts and hardware counters to C++ source code.
- Editing data access, control flow, and I/O behavior.
- Preserving correctness during optimization.
- Iterating until an objective performance target is reached.

## Challenges

| ID | Challenge | Main tool | Target |
|---|---|---|---|
| 01 | Syscall Storm | `strace -c` | 100x pass, >1000x stretch |
| 02 | Cache Maze | `perf stat`, `perf record` | 4x faster than starter |
| 03 | Branch Lottery | branch counters | 1.5x faster than starter |

Targets use speedup relative to the starter on the same machine. This keeps the
grading useful across Intel, AMD, Graviton 3, and Graviton 4 systems.

Puzzle 01 has a stretch goal because buffered I/O can improve the pathological
one-byte-read starter by several orders of magnitude. At millisecond runtimes,
use the `strace -c` call count alongside timing results.

## Challenge workflow

Start a puzzle:

```sh
ptf start 01
```

This creates:

```text
work/01/solution.cpp
runs/01/work/lab.md
```

The solution begins as a copy of the slow starter. Work through the following
cycle:

1. Run the starter and record its behavior.
2. Profile the working solution with the tool suggested by your hypothesis.
3. Inspect and edit `work/<id>/solution.cpp`.
4. Run or profile the `work` variant again.
5. Grade correctness and performance with `ptf check <id>`.
6. Repeat until the target passes.

Example:

```sh
ptf start 01
ptf 01 work
ptf strace 01 work

# Edit work/01/solution.cpp

ptf 01 work
ptf strace 01 work
ptf check 01
```

`ptf check` performs three steps:

1. Compiles the working C++ solution.
2. Compares its output with the reference result.
3. Measures median runtime and grades the required speedup.

Use more or fewer timing runs when needed:

```sh
ptf check 02 --runs 5
```

## Tools and hints

The profiling commands accept `bad`, `work`, and `fixed` variants:

```sh
ptf strace 01 work
ptf perf-stat 02 work
ptf perf-record 02 work
perf report -i runs/02/work/perf.data
```

Progressive hints guide the investigation while leaving the code change to you:

```sh
ptf hint 02
ptf hint 02 2
ptf hint 02 3
```

After completing the challenge:

```sh
ptf diagnose 02
ptf reveal 02
```

`reveal` explains the reference diagnosis and optimization.

## Commands

```text
ptf list
ptf start <id>
ptf lesson <id>
ptf run <id> <bad|work|fixed>
ptf strace <id> <bad|work|fixed>
ptf perf-stat <id> <bad|work|fixed>
ptf perf-record <id> <bad|work|fixed>
ptf check <id> [--runs N]
ptf hint <id> [level]
ptf diagnose <id>
ptf reveal <id>
```

Puzzle-first shortcuts are available:

```sh
ptf 01          # show lesson 01
ptf 01 work     # run your solution
ptf 01 bad      # run the starter
```

Puzzle IDs accept `1`, `01`, or a full slug such as `01-syscall-storm`.

## Requirements

- Linux
- Python 3
- `g++` with C++17 support
- `make`
- `strace`
- Linux `perf`

The CLI reports missing tools, restricted `perf_event_paranoid` settings, and
unavailable PMU events.

## Setup

```sh
git clone https://github.com/jtl06/ptf.git
cd ptf
make
make install
ptf list
```

`make install` creates `~/.local/bin/ptf` as a symlink to the checkout. Ensure
`~/.local/bin` is on `PATH`.

Generated binaries live in `build/`. Editable solutions live in `work/`.
Profiling evidence and notes live in `runs/`. Git ignores all three directories
except for their placeholder files.

## Comparing architectures

Run the same solution and grading command on each machine. Record:

- CPU model and architecture
- Kernel version
- Compiler version
- Virtual machine or container environment
- `perf_event_paranoid` value
- Available PMU events

Counter availability and exact values vary by processor. The source-level
challenge remains the same, while the evidence shows how each architecture
responds to the optimization.

## Future direction

An Arm Performix backend could add Graviton-focused event collection and guided
analysis while preserving the same editable C++ challenge and grading workflow.
