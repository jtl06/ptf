#include <cstddef>
#include <cstdint>
#include <iostream>
#include <vector>

namespace {

constexpr std::size_t kNodeCount = 3U * 1024U * 1024U;
constexpr int kRounds = 8;

std::uint32_t node_value(std::uint32_t index) {
    return (index * UINT32_C(2654435761)) ^ (index >> 3U);
}

}  // namespace

int main() {
    // Build the value array.
    std::vector<std::uint32_t> values(kNodeCount);
    for (std::size_t index = 0; index < kNodeCount; ++index) {
        values[index] = node_value(static_cast<std::uint32_t>(index));
    }

    // Sum the values several times.
    std::uint64_t checksum = 0;
    for (int round = 0; round < kRounds; ++round) {
        for (std::uint32_t value : values) {
            checksum += value;
        }
    }

    std::cout << "checksum=" << checksum << '\n';
    return 0;
}
