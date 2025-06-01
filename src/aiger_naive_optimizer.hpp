#ifndef __AIGER_NAIVE_OPTIMIZER_HPP__
#define __AIGER_NAIVE_OPTIMIZER_HPP__
#include <vector>
#include <string>
#include <set>

#include <mockturtle/mockturtle.hpp>
#include <mockturtle/algorithms/miter.hpp>
#include <mockturtle/algorithms/equivalence_checking.hpp>

#include "aiger_checker.hpp"
#include "logger.hpp"

using namespace mockturtle;


class aiger_naive_optimizer {
    // this class is used to provide optimization candidates for AIGER networks
private:
    // the safe AIGER network after optimization
    sequential<aig_network, true> aig_network_after_opt;

    // the buffer to hold the AIGER network during optimization
    sequential<aig_network, true> aig_network_during_opt;

    // the original AIGER network before optimization
    sequential<aig_network, true> aig_network_before_opt;
public:
    aiger_naive_optimizer(const sequential<aig_network, true>& aig_network_before_opt);

    // Optimize the AIGER network using naive optimization
    void optimize(int target_gate, int method);
    void optimize_set_zero(int target_gate);
    void optimize_set_one(int target_gate);
    void optimize_A_input(int target_gate);
    void optimize_A_input_not(int target_gate);
    void optimize_B_input(int target_gate);
    void optimize_B_input_not(int target_gate);

    // Getter for the optimized network
    const sequential<aig_network, true>& get_optimized_network() const;
    sequential<aig_network, true>& get_optimized_network();

    // Keep optimized network during optimization, can only be called after showing the correctness
    void keep_optimized_network();
    // reset the optimized network to the last successful optimization
    void reset_optimized_network_by_last();

    int get_next_target_gate(int target_gate_index, bool is_successful);
};


#endif