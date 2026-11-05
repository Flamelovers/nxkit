// Decode Godot's Smol-V shader stages before vk_shaders.py translates them.
#include "smolv.h"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <vector>
#include <cstdint>

int main(int argc, char **argv) {
    if (argc != 3) {
        std::cerr << "usage: godot-smolv <smolv dir> <spirv dir>\n";
        return 2;
    }
    const std::filesystem::path input(argv[1]), output(argv[2]);
    std::filesystem::create_directories(output);
    size_t count = 0;
    for (const auto &entry : std::filesystem::directory_iterator(input)) {
        if (!entry.is_regular_file() || entry.path().extension() != ".smolv") continue;
        std::ifstream in(entry.path(), std::ios::binary);
        std::vector<uint8_t> encoded(std::istreambuf_iterator<char>{in}, {});
        const size_t size = smolv::GetDecodedBufferSize(encoded.data(), encoded.size());
        if (size < 20 || size > (1u << 26) || (size & 3)) {
            std::cerr << "invalid Smol-V header: " << entry.path() << '\n';
            return 1;
        }
        std::vector<uint8_t> decoded(size);
        if (!smolv::Decode(encoded.data(), encoded.size(), decoded.data(), decoded.size()) ||
            decoded[0] != 3 || decoded[1] != 2 || decoded[2] != 35 || decoded[3] != 7) {
            std::cerr << "invalid Smol-V stage: " << entry.path() << '\n';
            return 1;
        }
        std::filesystem::path dest = output / entry.path().filename();
        dest.replace_extension(".spv");
        std::ofstream out(dest, std::ios::binary);
        out.write(reinterpret_cast<const char *>(decoded.data()), decoded.size());
        if (!out) return 1;
        ++count;
    }
    std::cout << "decoded " << count << " SPIR-V shaders\n";
    return count ? 0 : 1;
}
