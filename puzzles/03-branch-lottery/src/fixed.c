#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

enum {
    VALUE_COUNT = 16 * 1024 * 1024,
    ROUNDS = 6
};

static uint32_t random_next(uint32_t *state) {
    uint32_t value = *state;
    value ^= value << 13U;
    value ^= value >> 17U;
    value ^= value << 5U;
    *state = value;
    return value;
}

static uint64_t accumulate(const uint32_t *values) {
    uint64_t checksum = 0;
    for (int round = 0; round < ROUNDS; ++round) {
        for (size_t index = 0; index < VALUE_COUNT; ++index) {
            uint32_t value = values[index];
            uint32_t mask = UINT32_C(0) - (value >> 31U);
            checksum += value ^ mask;
        }
    }
    return checksum;
}

int main(void) {
    uint32_t *values = malloc((size_t)VALUE_COUNT * sizeof(*values));
    if (values == NULL) {
        perror("malloc");
        return 1;
    }

    uint32_t state = UINT32_C(0xa341316c);
    for (size_t index = 0; index < VALUE_COUNT; ++index) {
        values[index] = random_next(&state);
    }

    uint64_t checksum = accumulate(values);
    free(values);
    printf("checksum=%" PRIu64 "\n", checksum);
    return 0;
}

