#include <errno.h>
#include <fcntl.h>
#include <cstdint>
#include <cstdio>
#include <unistd.h>

enum { BUFFER_SIZE = 64 * 1024 };

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

    // Read into a fixed-size buffer.
    unsigned char buffer[BUFFER_SIZE];
    std::uint64_t newlines = 0;
    for (;;) {
        ssize_t bytes_read = read(fd, buffer, sizeof(buffer));
        if (bytes_read > 0) {
            for (ssize_t index = 0; index < bytes_read; ++index) {
                newlines += (buffer[index] == '\n');
            }
        } else if (bytes_read == 0) {
            break;
        } else if (errno != EINTR) {
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
