#include <errno.h>
#include <fcntl.h>
#include <cstdint>
#include <cstdio>
#include <unistd.h>

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s INPUT\n", argv[0]);
        return 2;
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) {
        perror("open");
        return 1;
    }

    // Count every newline and print the total so the work remains observable.
    std::uint64_t newlines = 0;
    unsigned char byte = 0;
    for (;;) {
        // This loop is the main area to investigate with strace.
        ssize_t bytes_read = read(fd, &byte, 1);
        if (bytes_read == 1) {
            newlines += (byte == '\n');
        } else if (bytes_read == 0) {
            break;
        } else if (errno != EINTR) {
            // A signal may interrupt read(); retry that case and report others.
            perror("read");
            close(fd);
            return 1;
        }
    }

    if (close(fd) != 0) {
        perror("close");
        return 1;
    }
    std::printf("newlines=%llu\n", static_cast<unsigned long long>(newlines));
    return 0;
}
