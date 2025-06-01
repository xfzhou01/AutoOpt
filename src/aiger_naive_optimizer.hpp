#ifndef __AIGER_NAIVE_OPTIMIZER_HPP__
#define __AIGER_NAIVE_OPTIMIZER_HPP__
#include <vector>
#include <string>

#include <mockturtle/mockturtle.hpp>
#include <mockturtle/algorithms/miter.hpp>
#include <mockturtle/algorithms/equivalence_checking.hpp>

#include "aiger_checker.hpp"
#include "logger.hpp"

using namespace mockturtle;


class aiger_naive_optimizer {
    // this class is used to provide optimization candidates for AIGER networks
private:

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
};


#endif