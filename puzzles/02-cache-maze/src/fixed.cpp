// Stores values in traversal order, processes them repeatedly, and prints the
// resulting checksum.

#include <cstddef>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <utility>
#include <vector>

namespace {

constexpr std::size_t kNodeCount = 3U * 1024U * 1024U;
constexpr int kRounds = 8;

// Deterministic pseudo-random generator.
class XorShift32 {
  public:
    explicit XorShift32(std::uint32_t state) : state_(state) {}

    std::uint32_t next() {
        std::uint32_t value = state_;
        value ^= value << 13U;
        value ^= value >> 17U;
        value ^= value << 5U;
        state_ = value;
        return value;
    }

  private:
    std::uint32_t state_;
};

std::uint32_t node_value(std::uint32_t index) {
    return (index * UINT32_C(2654435761)) ^ (index >> 3U);
}

std::uint64_t update_checksum(std::uint64_t checksum, std::uint32_t value) {
    return checksum * UINT64_C(11400714819323198485) + value;
}

}  // namespace

int main() {
    std::vector<std::uint32_t> order(kNodeCount);
    std::iota(order.begin(), order.end(), 0U);

    // Recreate the starter's shuffled traversal order.
    XorShift32 random(UINT32_C(0x6d2b79f5));
    for (std::size_t index = kNodeCount - 1; index > 0; --index) {
        const std::size_t other = random.next() % (index + 1);
        std::swap(order[index], order[other]);
    }

    // Store values in logical visit order.
    std::vector<std::uint32_t> values(kNodeCount);
    for (std::size_t index = 0; index < kNodeCount; ++index) {
        values[index] = node_value(order[index]);
    }
    std::vector<std::uint32_t>().swap(order);

    // Process the same visit sequence several times.
    std::uint64_t checksum = 0;
    for (int round = 0; round < kRounds; ++round) {
        for (std::uint32_t value : values) {
            checksum = update_checksum(checksum, value);
        }
    }

    std::cout << "checksum=" << checksum << '\n';
    return 0;
}
