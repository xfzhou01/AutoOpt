#include "aiger_exdc_naive_optimizer.hpp"

aiger_exdc_naive_optimizer::aiger_exdc_naive_optimizer(std::vector<std::vector<int>> cnf_clauses, 
    const sequential<aig_network, true> &aig_network_original):cnf_clauses(cnf_clauses),
    aig_network_original(aig_network_original)
{
    // Constructor implementation
    // Initialize the AIGER network with the given CNF clauses and original AIGER network
    Logger::info("AIGER EXDC Naive Optimizer initialized with " + std::to_string(cnf_clauses.size()) + " CNF clauses.");
    Logger::info("Original AIGER network has " + std::to_string(aig_network_original.num_pis()) + " PIs and " +
                 std::to_string(aig_network_original.num_pos()) + " POs.");
}