#include "aiger_checker.hpp"
#include "logger.hpp"
#include <cassert>
#include <iostream>
#include <mockturtle/io/write_dot.hpp>

// ---- TOOLS ----
// aig_network clone to sequential<aig_network, true>
sequential<aig_network, true> clone_aig_to_sequential(const aig_network& aig) {
    sequential<aig_network, true> seq;
    std::vector<sequential<aig_network, true>::signal> pis;
    // 1. create all PI nodes in sequential network
    aig.foreach_pi([&](auto n, auto) {
        pis.push_back(seq.create_pi());
    });
    // 2. clone all nodes from aig to sequential network
    std::unordered_map<aig_network::node, sequential<aig_network, true>::signal> node2sig;
    // constant node
    node2sig[aig.get_node(aig.get_constant(false))] = seq.get_constant(false);
    node2sig[aig.get_node(aig.get_constant(true))] = seq.get_constant(true);
    // pi nodes
    int pi_idx = 0;
    aig.foreach_pi([&](auto n, auto) {
        node2sig[n] = pis[pi_idx++];
    });
    // gate nodes
    aig.foreach_gate([&](auto n) {
        std::vector<sequential<aig_network, true>::signal> children;
        aig.foreach_fanin(n, [&](auto s) {
            children.push_back(aig.is_complemented(s) ? !node2sig[aig.get_node(s)] : node2sig[aig.get_node(s)]);
        });
        // AIG: always 2 fanins
        auto s = seq.create_and(children[0], children[1]);
        node2sig[n] = s;
    });
    // 3. create po
    aig.foreach_po([&](auto s, auto) {
        auto sig = aig.is_complemented(s) ? !node2sig[aig.get_node(s)] : node2sig[aig.get_node(s)];
        seq.create_po(sig);
    });
    return seq;
}

// test functions
void test_check_cnf_conflit_unsat() {
    // (x1) & (!x1) => UNSAT
    std::vector<std::vector<int>> cnf = { {1}, {-1} };
    sequential<aig_network, true> dummy1, dummy2;
    aiger_checker checker(cnf, dummy1, dummy2);
    bool result = checker.check_cnf_conflit();
    assert(result == true);
    std::cout << "test_check_cnf_conflit_unsat passed\n";
}

void test_check_cnf_conflit_sat() {
    // (x1) => SAT
    std::vector<std::vector<int>> cnf = { {1} };
    sequential<aig_network, true> dummy1, dummy2;
    aiger_checker checker(cnf, dummy1, dummy2);
    bool result = checker.check_cnf_conflit();
    assert(result == false);
    std::cout << "test_check_cnf_conflit_sat passed\n";
}

void test_unsat_cnf() {
    // (x1) & (!x1) is UNSAT
    std::vector<std::vector<int>> cnf = { {1}, {-1} };
    sequential<aig_network, true> dummy1, dummy2;
    aiger_checker checker(cnf, dummy1, dummy2);
    assert(checker.check_cnf_conflit() && "UNSAT CNF should return true");
    std::cout << "test_unsat_cnf passed\n";
}

void test_sat_cnf() {
    // (x1) is SAT
    std::vector<std::vector<int>> cnf = { {1} };
    sequential<aig_network, true> dummy1, dummy2;
    aiger_checker checker(cnf, dummy1, dummy2);
    assert(!checker.check_cnf_conflit() && "SAT CNF should return false");
    std::cout << "test_sat_cnf passed\n";
}

void test_merge_aig_networks_and_output() {
    // n1: f1 = ((a & b) | (c ^ d)) & (!e)
    mockturtle::aig_network aig1;
    auto a = aig1.create_pi();
    auto b = aig1.create_pi();
    auto c = aig1.create_pi();
    auto d = aig1.create_pi();
    auto e = aig1.create_pi();
    auto and1 = aig1.create_and(a, b);
    auto xor1 = aig1.create_xor(c, d);
    auto or1 = aig1.create_or(and1, xor1);
    auto not_e = aig1.create_not(e);
    auto f1 = aig1.create_and(or1, not_e);
    aig1.create_po(f1);

    // n2: f2 = ((a | b) & (c | d)) ^ e
    mockturtle::aig_network aig2;
    auto a2 = aig2.create_pi();
    auto b2 = aig2.create_pi();
    auto c2 = aig2.create_pi();
    auto d2 = aig2.create_pi();
    auto e2 = aig2.create_pi();
    auto or2_1 = aig2.create_or(a2, b2);
    auto or2_2 = aig2.create_or(c2, d2);
    auto and2 = aig2.create_and(or2_1, or2_2);
    auto f2 = aig2.create_xor(and2, e2);
    aig2.create_po(f2);

    // save dot files before merge
    mockturtle::write_dot(aig1, "aig1_before_merge.dot");
    mockturtle::write_dot(aig2, "aig2_before_merge.dot");

    // merge
    aiger_checker checker({}, sequential<aig_network, true>(), sequential<aig_network, true>());
    auto merged = checker.merge_aig_networks_and_output(aig1, aig2);

    // save dot
    mockturtle::write_dot(merged, "aig_after_merge.dot");

    Logger::info("AIG merge test completed. Dot files written: aig1_before_merge.dot, aig2_before_merge.dot, aig_after_merge.dot");
}

// Test merging two AIG networks where n1 has multiple POs
void test_merge_aig_networks_and_output_multi_po() {
    // n1: f1 = a & b, f2 = a | b
    mockturtle::aig_network aig1;
    auto a = aig1.create_pi();
    auto b = aig1.create_pi();
    auto f1 = aig1.create_and(a, b);
    auto f2 = aig1.create_and(a, b);
    aig1.create_po(f1);
    aig1.create_po(f2);

    // n2: f3 = a ^ b
    mockturtle::aig_network aig2;
    auto a2 = aig2.create_pi();
    auto b2 = aig2.create_pi();
    auto f3 = aig2.create_and(a2, b2);
    aig2.create_po(f3);

    // Save dot files before merge
    mockturtle::write_dot(aig1, "aig1_multi_po_before_merge.dot");
    mockturtle::write_dot(aig2, "aig2_multi_po_before_merge.dot");

    // Merge
    aiger_checker checker({}, sequential<aig_network, true>(), sequential<aig_network, true>());
    auto merged = checker.merge_aig_networks_and_output(aig1, aig2);

    // Save dot after merge
    mockturtle::write_dot(merged, "aig_multi_po_after_merge.dot");

    Logger::info("AIG multi-PO merge test completed. Dot files written: aig1_multi_po_before_merge.dot, aig2_multi_po_before_merge.dot, aig_multi_po_after_merge.dot");
}

void test_equivalence_checking_constant_zero() {
    // Create two AIG networks, both output constant 0
    mockturtle::aig_network aig1;
    auto pi1 = aig1.create_pi();
    aig1.create_po(aig1.get_constant(false));

    mockturtle::aig_network aig2;
    auto pi2 = aig2.create_pi();
    aig2.create_po(aig2.get_constant(false));

    // Use miter and equivalence checking
    auto miter_opt = mockturtle::miter<mockturtle::aig_network>(aig1, aig2);
    assert(miter_opt.has_value());
    auto result = mockturtle::equivalence_checking(*miter_opt);
    assert(result.has_value());
    assert(*result == true);
    std::cout << "test_equivalence_checking_constant_zero passed\n";
}

void test_miter_constant_zero() {
    // Create two AIG networks, both output constant 0
    mockturtle::aig_network aig1;
    auto pi1 = aig1.create_pi();
    aig1.create_po(aig1.get_constant(false));

    auto result = mockturtle::equivalence_checking(aig1);
    assert(result.has_value());
    assert(*result == true);
    std::cout << "test_equivalence_checking_constant_zero miter passed\n";
}

void test_check_equivalence() {
    std::cout << "Testing equivalence checking with AIG networks...\n";
    std::vector<std::vector<int>> cnf = { {-1}, {-2} };
    sequential<aig_network, true> dummy1, dummy2;

    mockturtle::aig_network aig_xor;
    auto x1 = aig_xor.create_pi();
    auto x2 = aig_xor.create_pi();
    auto xor_gate = aig_xor.create_xor(x1, x2);
    aig_xor.create_po(xor_gate);
    dummy1 = clone_aig_to_sequential(aig_xor);

    mockturtle::aig_network aig_or;
    auto x3 = aig_or.create_pi();
    auto x4 = aig_or.create_pi();
    auto or_gate = aig_or.create_or(x3, x4);
    aig_or.create_po(or_gate);
    dummy2 = clone_aig_to_sequential(aig_or);

    aiger_checker checker(cnf, dummy2, dummy1);
    auto result = checker.check_equivalence(true);
    assert(result == true);
}




int main() {
    test_check_cnf_conflit_unsat();
    test_check_cnf_conflit_sat();
    test_unsat_cnf();
    test_sat_cnf();
    test_merge_aig_networks_and_output();
    test_merge_aig_networks_and_output_multi_po();
    test_equivalence_checking_constant_zero();
    test_miter_constant_zero();
    test_check_equivalence();
    std::cout << "All aiger_checker::check_cnf_conflit tests passed!\n";
    return 0;
}
