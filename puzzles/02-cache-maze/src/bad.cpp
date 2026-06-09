// Links shuffled node indices into a cycle, traverses it repeatedly, and
// prints the sum of the visited values.

#include <cstddef>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <utility>
#include <vector>

namespace {

constexpr std::size_t kNodeCount = 3U * 1024U * 1024U;
constexpr int kRounds = 8;

struct Node {
    // Index of the next node.
    std::uint32_t next;
    std::uint32_t value;
};

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

}  // namespace

int main() {
    std::vector<Node> nodes(kNodeCount);
    std::vector<std::uint32_t> order(kNodeCount);
    std::iota(order.begin(), order.end(), 0U);

    // Create a shuffled traversal order.
    XorShift32 random(UINT32_C(0x6d2b79f5));
    for (std::size_t index = kNodeCount - 1; index > 0; --index) {
        const std::size_t other = random.next() % (index + 1);
        std::swap(order[index], order[other]);
    }

    for (std::size_t index = 0; index < kNodeCount; ++index) {
        nodes[index].value = node_value(static_cast<std::uint32_t>(index));
    }
    for (std::size_t index = 0; index < kNodeCount; ++index) {
        const std::uint32_t current = order[index];
        nodes[current].next = order[(index + 1) % kNodeCount];
    }

    const std::uint32_t head = order[0];
    std::vector<std::uint32_t>().swap(order);

    // Traverse the cycle several times.
    std::uint64_t checksum = 0;
    for (int round = 0; round < kRounds; ++round) {
        std::uint32_t current = head;
        for (std::size_t visited = 0; visited < kNodeCount; ++visited) {
            const Node &node = nodes[current];
            checksum += node.value;
            current = node.next;
        }
    }

    std::cout << "checksum=" << checksum << '\n';
    return 0;
}
