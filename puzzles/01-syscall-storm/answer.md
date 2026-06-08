# Answer: Syscall Storm

## Diagnosis

The bottleneck is syscall overhead. The bad program calls `read(fd, &c, 1)` for
every byte. The file data may be cached, but every call still crosses the
user/kernel boundary and performs syscall bookkeeping.

## Strongest evidence

`strace -c` shows an enormous `read()` count in the bad version. The fixed
version should issue roughly one read per 64 KiB, so its call count falls by
orders of magnitude. `perf` can show time and instruction differences, but
`strace` identifies the cause more directly.

## Fix

Read into a 64 KiB buffer and count newline bytes in user space. Both variants
print the same newline count.

## Validation

Compare wall time and run `strace` on both variants. The expected validation is
a much lower `read()` count and faster runtime in the fixed version.

