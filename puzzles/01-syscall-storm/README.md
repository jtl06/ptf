# Puzzle 01: Syscall Storm

## Learning objective

Use `strace` to identify syscall overhead caused by tiny I/O operations. Connect
the number of `read()` calls to the program's buffer size and runtime.

## Scenario

Both programs count newline characters in the same deterministic text file and
print the same result. One is needlessly slow.

Start with a hypothesis. Is the program waiting on storage, doing too much CPU
work, or crossing into the kernel too often?

## Suggested workflow

1. Run `ptf journal 01 bad`.
2. Run the slow program with `ptf 01 bad`.
3. Write down the syscall pattern you expect.
4. Use `ptf strace 01 bad`.
5. Record the dominant syscall and its call count.
6. Run `ptf compare 01` and profile the fixed version.

The useful loop is:

`hypothesis -> tool -> evidence -> diagnosis -> fix -> validation`
