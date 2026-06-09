// Repeatedly applies a 3x3 box blur to a generated grayscale image.

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <vector>

namespace {

constexpr std::size_t kWidth = 4096;
constexpr std::size_t kHeight = 4096;
constexpr int kRounds = 6;

std::uint16_t pixel_value(std::size_t row, std::size_t column) {
    const std::uint32_t index =
        static_cast<std::uint32_t>(row * kWidth + column);
    return static_cast<std::uint16_t>(
        ((index * UINT32_C(2654435761)) ^ (index >> 5U)) & UINT32_C(0xffff));
}

std::uint64_t checksum(const std::vector<std::uint16_t> &image) {
    std::uint64_t result = 0;
    for (std::uint16_t pixel : image) {
        result = result * UINT64_C(11400714819323198485) + pixel;
    }
    return result;
}

}  // namespace

int main() {
    std::vector<std::uint16_t> first(kWidth * kHeight);
    std::vector<std::uint16_t> second(kWidth * kHeight);
    for (std::size_t row = 0; row < kHeight; ++row) {
        for (std::size_t column = 0; column < kWidth; ++column) {
            first[row * kWidth + column] = pixel_value(row, column);
        }
    }
    second = first;

    auto *source = &first;
    auto *destination = &second;
    for (int round = 0; round < kRounds; ++round) {
        for (std::size_t column = 1; column + 1 < kWidth; ++column) {
            for (std::size_t row = 1; row + 1 < kHeight; ++row) {
                std::uint32_t sum = 0;
                for (std::size_t kernel_row = row - 1; kernel_row <= row + 1;
                     ++kernel_row) {
                    for (std::size_t kernel_column = column - 1;
                         kernel_column <= column + 1; ++kernel_column) {
                        sum += (*source)[kernel_row * kWidth + kernel_column];
                    }
                }
                (*destination)[row * kWidth + column] =
                    static_cast<std::uint16_t>(sum / 9U);
            }
        }
        std::swap(source, destination);
    }

    std::cout << "checksum=" << checksum(*source) << '\n';
    return 0;
}
