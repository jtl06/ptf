# ptf

`ptf` is a small Linux performance lab inspired by the systems labs in CS:APP.
Each puzzle gives you a correct but slow C++ program. Use `strace`, `perf`, and
the source code to find the bottleneck, change the program, and meet a
performance target without changing its result.

The current puzzles cover excessive system calls, cache-unfriendly image
convolution, and unpredictable branches.

| ID | Puzzle | Main evidence | Target |
|---|---|---|---|
| 01 | Syscall Storm | `strace -c` | 100x speedup, >1000x stretch |
| 02 | Cache Maze | `perf stat`, `perf record` | 4x speedup |
| 03 | Branch Lottery | branch counters | 1.5x speedup |

Targets are measured against the starter on the same machine.

## Setup

You need Linux, Python 3, `g++`, and `make`. The profiling commands also require
`strace` and Linux `perf`.

```sh
git clone https://github.com/jtl06/ptf.git
cd ptf
make
make install
```

`make install` links `ptf` into `~/.local/bin`. Add that directory to `PATH` if
your shell does not already use it.

## Trying a puzzle

Start with the lesson and create an editable copy:

```sh
ptf lesson 02
ptf start 02
```

This creates `work/02/work.cpp` and a copy of the original program at
`work/02/bad_reference.cpp`.

Run and profile your copy:

```sh
ptf 02 work
ptf perf-stat 02 work
ptf perf-record 02 work
perf report -i runs/02/work/perf.data
```

Edit `work/02/work.cpp`, repeat the measurements, and grade it:

```sh
ptf check 02
```

`ptf check` compares the output with the reference implementation and measures
the median speedup over the starter. Use `--runs 5` when you want a steadier
timing result.

Running `ptf start 02` again resets `work.cpp`. The previous file is saved as a
timestamped `work.backup-*.cpp`. Lab notes in `runs/02/work/lab.md` are kept.

## Commands

```text
ptf help
ptf list
ptf lesson <id>
ptf start <id>
ptf <id> <bad|work|fixed>
ptf strace <id> <bad|work|fixed>
ptf perf-stat <id> <bad|work|fixed>
ptf perf-record <id> <bad|work|fixed>
ptf check <id> [--runs N]
ptf hint <id> [1|2|3]
ptf diagnose <id>
ptf reveal <id>
```

Use `bad` for the starter, `work` for your code, and `fixed` for the reference
implementation. Puzzle IDs may be written as `2`, `02`, or
`02-cache-maze`.

Profiler output and lab notes are stored under `runs/`. Build products are
stored under `build/`. If hardware counters are unavailable, `ptf` reports the
relevant `perf_event_paranoid`, kernel, or PMU issue.
