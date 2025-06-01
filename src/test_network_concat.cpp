#include <mockturtle/networks/aig.hpp>
#include <mockturtle/algorithms/cleanup.hpp>
#include <iostream>

using namespace mockturtle;

// 本例将两个AIG网络拼接为一个新网络，输出为两者输出的AND
int main() {
    // 构造第一个AIG网络: f1 = a & b
    aig_network aig1;
    auto a = aig1.create_pi();
    auto b = aig1.create_pi();
    auto f1 = aig1.create_and(a, b);
    aig1.create_po(f1);

    // 构造第二个AIG网络: f2 = c | d
    aig_network aig2;
    auto c = aig2.create_pi();
    auto d = aig2.create_pi();
    auto f2 = aig2.create_or(c, d);
    aig2.create_po(f2);

    // 新网络，拼接输入
    aig_network concat;
    std::vector<aig_network::signal> inputs;
    for (int i = 0; i < 4; ++i) {
        inputs.push_back(concat.create_pi());
    }

    // 用cleanup_dangling把aig1和aig2的逻辑分别迁移到新网络
    auto outputs1 = cleanup_dangling(aig1, concat, inputs.begin(), inputs.begin() + 2);
    auto outputs2 = cleanup_dangling(aig2, concat, inputs.begin() + 2, inputs.end());

    // 拼接输出: AND(outputs1[0], outputs2[0])
    auto final_out = concat.create_and(outputs1[0], outputs2[0]);
    concat.create_po(final_out);

    std::cout << "Network concatenation test finished. PI count: " << concat.num_pis()
              << ", PO count: " << concat.num_pos() << std::endl;
    return 0;
}
