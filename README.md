# perf-mystery

`perf-mystery` is a small local CTF-style lab for learning Linux performance
debugging. Each puzzle contains a deliberately slow program, an equivalent
faster version, progressive hints, a diagnosis quiz, and an explanation.

The point is not merely to benchmark two binaries. Work through the full loop:

> hypothesis -> tool -> evidence -> diagnosis -> fix -> validation

Write down what you expect before collecting data. Pick a tool that can test
that expectation. Explain the evidence before looking at the fixed version.

## Requirements

- Linux
- Python 3
- `gcc`, `g++`, and `make`
- `strace` for syscall exercises
- Linux `perf` for hardware counters and sampling

The CLI detects missing profiling tools. Some systems also restrict `perf`
through `/proc/sys/kernel/perf_event_paranoid` or container capabilities; the
CLI reports that case without a Python traceback.

## Quick start

Build every puzzle:

```sh
make
```

Run the CLI directly from the checkout as `./ptf`. To install it as the `ptf`
command for the current user:

```sh
make install
```

This installs to `~/.local/bin/ptf` by default. Ensure `~/.local/bin` is on
`PATH`, or override the location with `make install PREFIX=/another/path`. The
installed command is a symlink to this checkout, so move or remove the checkout
only after reinstalling from its new location.

Explore a lesson:

```sh
ptf list
ptf lesson 01
ptf journal 01 bad
ptf run 01 bad
ptf compare 01
ptf strace 01 bad
ptf perf-stat 02 bad
ptf perf-record 02 bad
perf report -i runs/02/bad/perf.data
ptf diagnose 03
ptf reveal 01
```

Puzzle IDs may be written as `01`, `1`, or the full directory slug such as
`01-syscall-storm`.

Generated binaries live under `build/`. Profiling evidence and lab notes live
under `runs/`. Puzzle 01 generates its deterministic input file on first build;
that large file is ignored by Git.

## Suggested lab workflow

1. Run `lesson` and create a `journal`.
2. State a concrete bottleneck hypothesis.
3. Run the bad program once to establish runtime and checksum.
4. Choose `strace`, `perf stat`, or `perf record` based on the hypothesis.
5. Record the decisive output pattern in the journal.
6. Take the `diagnose` quiz before revealing the answer.
7. Run `compare` and profile the fixed version to validate the expected metric.

Benchmark timing varies by CPU, kernel, virtualization, and system load. Treat
the counters and relative behavior as evidence, not as universal fixed numbers.

## Comparing x86 and Arm

The puzzle sources build unchanged on x86-64 and AArch64 with GCC. Run the same
lab sequence on each machine, but do not expect identical event counts. Intel,
AMD, Graviton 3, and Graviton 4 expose different PMUs, and virtual machines may
restrict some events. Start with portable `perf stat -d` metrics such as cycles,
instructions, IPC, branches, and branch misses. Record the CPU model, kernel,
compiler version, and compiler flags in the journal before comparing systems.

The diagnosis should survive the architecture change: syscall storm still means
too many `read()` calls, cache maze still means serialized poor-locality loads,
and branch lottery still means a high branch-miss rate in the bad version.

## Future collector backends

The CLI currently invokes Linux `strace` and `perf` directly. A later version
could define a small collector interface and add an Arm Performix backend for
Arm-specific guided analysis. That backend could collect Arm PMU events,
normalize them into the same evidence files, and add architecture-specific
questions without changing the puzzle or journal format.
