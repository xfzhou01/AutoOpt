#include <mockturtle/mockturtle.hpp>
#include <mockturtle/io/aiger_reader.hpp>
#include <iostream>
#include <string>
#include <fstream>

using namespace mockturtle;

int main(int argc, char* argv[]) {
    std::string aig_file_name;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--aig" && i + 1 < argc) {
            aig_file_name = argv[++i];
        } else {
            std::cerr << "Unknown argument: " << arg << std::endl;
            return 1;
        }
    }
    if (aig_file_name.empty()) {
        std::cerr << "Usage: " << argv[0] << " --aig <file.aig>" << std::endl;
        return 1;
    }
    std::cout << "AIG file: " << aig_file_name << std::endl;
    aig_network aig;
    names_view<aig_network> named_aig{aig};
    lorina::text_diagnostics consumer;
    lorina::diagnostic_engine diag(&consumer);
    auto result = lorina::read_aiger(aig_file_name, aiger_reader(named_aig), &diag);
    if (result != lorina::return_code::success) {
        std::cerr << "Failed to read AIG file." << std::endl;
        return 1;
    }
    std::cout << "Number of PIs: " << aig.num_pis() << std::endl;
    std::cout << "Number of POs: " << aig.num_pos() << std::endl;
    std::cout << "Number of gates: " << aig.num_gates() << std::endl;

    // 可视化AIG结构，输出去掉gate前的dot文件
    {
        std::ofstream dot_file_before("aig_before.dot");
        if (dot_file_before) {
            write_dot(aig, dot_file_before);
            std::cout << "Original AIG structure written to aig_before.dot (Graphviz format)." << std::endl;
        } else {
            std::cerr << "Failed to open aig_before.dot for writing." << std::endl;
        }
    }

    // 示例：将 index 为 i 的 AND gate 输出替换为它的第一个输入
    int i = 0; // 可根据需要修改 i
    if (aig.num_gates() > 0) {
        int gate_count = 0;
        aig_network::node target_node = 0;
        aig.foreach_gate([&](aig_network::node n) {
            if (gate_count == i) {
                target_node = n;
            }
            ++gate_count;
        });
        if (gate_count > i) {
            aig_network::signal first_fanin;
            aig.foreach_fanin(target_node, [&](aig_network::signal s, int fanin_idx) {
                if (fanin_idx == 0) {
                    first_fanin = s;
                }
            });
            aig.substitute_node(target_node, first_fanin);
            std::cout << "Gate at index " << i << " replaced by its first input." << std::endl;
        } else {
            std::cout << "No gate at index " << i << "." << std::endl;
        }
    }
    // 可视化AIG结构，输出dot文件
    std::ofstream dot_file("aig.dot");
    if (dot_file) {
        write_dot(aig, dot_file);
        std::cout << "AIG structure written to aig.dot (Graphviz format)." << std::endl;
        std::cout << "You can visualize it with: dot -Tpng aig.dot -o aig.png" << std::endl;
    } else {
        std::cerr << "Failed to open aig.dot for writing." << std::endl;
    }
    return 0;
}