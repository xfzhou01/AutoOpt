#ifndef __AIGER_CHECKER_HPP__
#define __AIGER_CHECKER_HPP__

#include <vector>
#include <string>
#include <mockturtle/mockturtle.hpp>
#include <mockturtle/algorithms/miter.hpp>
#include <mockturtle/algorithms/equivalence_checking.hpp>

using namespace mockturtle;

class aiger_checker {
    
    // this class is used to check the equivalence of AIGER networks
    // under CNF constraints.
private:
    std::vector<std::vector<int>> cnf_clauses; // CNF clauses
    aig_network cnf_clauses_aig; // AIGER network for CNF clauses
    aig_network cnf_clauses_aig_assumption;
    sequential<aig_network, true> aig_network_after_opt;
    sequential<aig_network, true> aig_network_before_opt;

    aig_network aig_network_before_opt_logic;
    aig_network aig_network_after_opt_logic;

    

public:
    aiger_checker(const std::vector<std::vector<int>>& cnf_clauses,
                  const sequential<aig_network, true>& aig_network_after_opt,
                  const sequential<aig_network, true>& aig_network_before_opt);
    
    aig_network convert_cnf_to_aig();
    bool check_cnf_conflit();
    
    // Check if the AIGER network after optimization is equivalent to the one before optimization
    bool check_equivalence(bool is_debug = false);

    // merge n1 and n2
    // make sure the following:
    //  n1 and n2 have the same PIs
    //  n2 have only 1 PO
    // do:
    //  merge all PIs of n1 to n2
    //  and the output of n1 to every PO of n2
    //  return the merged network 
    aig_network merge_aig_networks_and_output(
        aig_network& n1,
        aig_network& n2
    );
};



#endif