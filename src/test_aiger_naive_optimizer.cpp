// Unit tests for aiger_naive_optimizer
#include "aiger_naive_optimizer.hpp"
#include "logger.hpp"
#include <mockturtle/io/write_dot.hpp>
#include <cassert>
#include <iostream>

// Helper: create a simple AIG network with a single AND gate
aig_network create_simple_and_network() {
    aig_network aig;
    auto a = aig.create_pi();
    auto b = aig.create_pi();
    auto and1 = aig.create_and(a, b);
    aig.create_po(and1);
    return aig;
}

// Helper: clone aig_network to sequential<aig_network, true>
sequential<aig_network, true> clone_aig_to_sequential(const aig_network& aig) {
    sequential<aig_network, true> seq;
    std::vector<sequential<aig_network, true>::signal> pis;
    aig.foreach_pi([&](auto n, auto) { pis.push_back(seq.create_pi()); });
    std::unordered_map<aig_network::node, sequential<aig_network, true>::signal> node2sig;
    node2sig[aig.get_node(aig.get_constant(false))] = seq.get_constant(false);
    node2sig[aig.get_node(aig.get_constant(true))] = seq.get_constant(true);
    int pi_idx = 0;
    aig.foreach_pi([&](auto n, auto) { node2sig[n] = pis[pi_idx++]; });
    aig.foreach_gate([&](auto n) {
        std::vector<sequential<aig_network, true>::signal> children;
        aig.foreach_fanin(n, [&](auto s) {
            children.push_back(aig.is_complemented(s) ? !node2sig[aig.get_node(s)] : node2sig[aig.get_node(s)]);
        });
        auto s = seq.create_and(children[0], children[1]);
        node2sig[n] = s;
    });
    aig.foreach_po([&](auto s, auto) {
        auto sig = aig.is_complemented(s) ? !node2sig[aig.get_node(s)] : node2sig[aig.get_node(s)];
        seq.create_po(sig);
    });
    return seq;
}

void test_optimize_set_zero() {
    auto aig = create_simple_and_network();
    mockturtle::write_dot(aig, "and_before_set_zero.dot");
    auto seq = clone_aig_to_sequential(aig);
    aiger_naive_optimizer opt(seq);
    // The AND gate is the only gate, its index is 2 (after 2 PIs)
    opt.optimize(3, 0); // set to zero
    // Save after optimization
    aig_network& aig_opt = static_cast<aig_network&>(seq);
    mockturtle::write_dot(aig_opt, "and_after_set_zero.dot");
    Logger::info("test_optimize_set_zero: Dot files written: and_before_set_zero.dot, and_after_set_zero.dot");
}

void test_optimize_set_one() {
    auto aig = create_simple_and_network();
    mockturtle::write_dot(aig, "and_before_set_one.dot");
    auto seq = clone_aig_to_sequential(aig);
    aiger_naive_optimizer opt(seq);
    opt.optimize(3, 1); // set to one
    aig_network& aig_opt = static_cast<aig_network&>(seq);
    mockturtle::write_dot(aig_opt, "and_after_set_one.dot");
    Logger::info("test_optimize_set_one: Dot files written: and_before_set_one.dot, and_after_set_one.dot");
}

void test_optimize_A_input() {
    auto aig = create_simple_and_network();
    mockturtle::write_dot(aig, "and_before_A_input.dot");
    auto seq = clone_aig_to_sequential(aig);
    aiger_naive_optimizer opt(seq);
    opt.optimize(3, 2); // replace with A input
    aig_network& aig_opt = static_cast<aig_network&>(seq);
    mockturtle::write_dot(aig_opt, "and_after_A_input.dot");
    Logger::info("test_optimize_A_input: Dot files written: and_before_A_input.dot, and_after_A_input.dot");
}

void test_optimize_A_input_not() {
    auto aig = create_simple_and_network();
    mockturtle::write_dot(aig, "and_before_A_input_not.dot");
    auto seq = clone_aig_to_sequential(aig);
    aiger_naive_optimizer opt(seq);
    opt.optimize(3, 3); // replace with NOT A input
    aig_network& aig_opt = static_cast<aig_network&>(seq);
    mockturtle::write_dot(aig_opt, "and_after_A_input_not.dot");
    Logger::info("test_optimize_A_input_not: Dot files written: and_before_A_input_not.dot, and_after_A_input_not.dot");
}

void test_optimize_B_input() {
    auto aig = create_simple_and_network();
    mockturtle::write_dot(aig, "and_before_B_input.dot");
    auto seq = clone_aig_to_sequential(aig);
    aiger_naive_optimizer opt(seq);
    opt.optimize(3, 4); // replace with B input
    aig_network& aig_opt = static_cast<aig_network&>(seq);
    mockturtle::write_dot(aig_opt, "and_after_B_input.dot");
    Logger::info("test_optimize_B_input: Dot files written: and_before_B_input.dot, and_after_B_input.dot");
}

void test_optimize_B_input_not() {
    auto aig = create_simple_and_network();
    mockturtle::write_dot(aig, "and_before_B_input_not.dot");
    auto seq = clone_aig_to_sequential(aig);
    aiger_naive_optimizer opt(seq);
    opt.optimize(3, 5); // replace with NOT B input
    aig_network& aig_opt = static_cast<aig_network&>(seq);
    mockturtle::write_dot(aig_opt, "and_after_B_input_not.dot");
    Logger::info("test_optimize_B_input_not: Dot files written: and_before_B_input_not.dot, and_after_B_input_not.dot");
}

void test_gate_index() {
    // Test the gate index retrieval
    auto aig = create_simple_and_network();
    auto seq = clone_aig_to_sequential(aig);
    auto seq2 = seq;
    auto node_seq = seq.index_to_node(3); // The AND gate is the 3rd node (after 2 PIs)
    auto node_seq2 = seq2.index_to_node(3);
    // Logger::info("node_seq index: " + std::to_string(seq.node_to_index(node_seq)));
    // Logger::info("node_seq2 index: " + std::to_string(seq2.node_to_index(node_seq2)));
    // Logger::info("node_seq: " + std::to_string(node_seq));
    // Logger::info("node_seq2: " + std::to_string(node_seq2));
    assert(seq.node_to_index(node_seq) == seq2.node_to_index(node_seq2));
    assert(seq.node_to_index(node_seq) == 3); // The AND gate should be at index 3
    Logger::info("test_gate_index passed");
}


int main() {
    test_optimize_set_zero();
    test_optimize_set_one();
    test_optimize_A_input();
    test_optimize_A_input_not();
    test_optimize_B_input();
    test_optimize_B_input_not();
    test_gate_index();
    std::cout << "All aiger_naive_optimizer tests passed!\n";
    return 0;
}
