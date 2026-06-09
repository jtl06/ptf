#include <cstddef>
#include <cstdint>
#include <iostream>
#include <vector>

namespace {

constexpr std::size_t kValueCount = 16U * 1024U * 1024U;
constexpr int kRounds = 6;

// Generate the same input sequence used by the starter.
std::uint32_t random_next(std::uint32_t &state) {
    std::uint32_t value = state;
    value ^= value << 13U;
    value ^= value >> 17U;
    value ^= value << 5U;
    state = value;
    return value;
}

std::uint64_t accumulate(const std::vector<std::uint32_t> &values) {
    std::uint64_t checksum = 0;
    for (int round = 0; round < kRounds; ++round) {
        for (std::uint32_t value : values) {
            // Expand the high bit into either all zeroes or all ones.
            const std::uint32_t mask = UINT32_C(0) - (value >> 31U);
            // XOR selects value or its complement without a data-dependent branch.
            checksum += value ^ mask;
        }
    }
    return checksum;
}

}  // namespace

int main() {
    // Build the input once so repeated rounds focus on the accumulation loop.
    std::vector<std::uint32_t> values(kValueCount);
    std::uint32_t state = UINT32_C(0xa341316c);
    for (std::uint32_t &value : values) {
        value = random_next(state);
    }

    std::cout << "checksum=" << accumulate(values) << '\n';
    return 0;
}
