#ifndef __AIGER_EXDC_NAIVE_OPTIMIZER_HPP__
#define __AIGER_EXDC_NAIVE_OPTIMIZER_HPP__

#include <vector>
#include <string>

#include <mockturtle/mockturtle.hpp>
#include <mockturtle/algorithms/miter.hpp>
#include <mockturtle/algorithms/equivalence_checking.hpp>
#include "aiger_checker.hpp"
#include "logger.hpp"
#include "aiger_naive_optimizer.hpp"
using namespace mockturtle;
class aiger_exdc_naive_optimizer {
    // This class is used to provide optimization candidates for AIGER networks
    // specifically for EXDC (EXtra Deduced Constraints) optimizations.
private:
    std::vector<std::vector<int>> cnf_clauses; // CNF clauses
    sequential<aig_network, true> aig_network_original; // The aiger network before optimization
public:
    aiger_exdc_naive_optimizer(std::vector<std::vector<int>> cnf_clauses,
                               const sequential<aig_network, true>& aig_network_original);
    
    // Optimize the AIGER network using naive optimization
    void optimize();


};


#endif