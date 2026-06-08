# Puzzle 01: Syscall Storm

## Learning objective

Learn when `strace` is more useful than `perf`, and recognize syscall overhead
caused by tiny I/O operations.

## Scenario

Both programs count newline characters in the same deterministic text file and
print the same result. One is needlessly slow.

Start with a hypothesis. Is the program waiting on storage, doing too much CPU
work, or crossing into the kernel too often?

## Suggested workflow

1. Run `../../pmystery.py journal 01 bad`.
2. Compare the two runtimes.
3. Use `../../pmystery.py strace 01 bad`.
4. Record the dominant syscall and its call count.
5. Profile the fixed version and validate what changed.

The useful loop is:

`hypothesis -> tool -> evidence -> diagnosis -> fix -> validation`

