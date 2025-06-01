#include "aiger_checker.hpp"
#include "logger.hpp"

aiger_checker::aiger_checker(const std::vector<std::vector<int>>& cnf_clauses,
              const sequential<aig_network, true>& aig_network_after_opt,
              const sequential<aig_network, true>& aig_network_before_opt)
    : cnf_clauses(cnf_clauses),
      aig_network_after_opt(aig_network_after_opt),
      aig_network_before_opt(aig_network_before_opt) {
    // do sanity check, the aig_network_after_opt and aig_network_before_opt should have the same PIs
    if (aig_network_after_opt.num_pis() != aig_network_before_opt.num_pis()) {
        Logger::error("AIG networks after and before optimization have different number of PIs.");
        Logger::error("AIG network before optimization: " 
              + std::to_string(aig_network_before_opt.num_pis()) + " PIs, "
              + std::to_string(aig_network_before_opt.num_pos()) + " POs, "
              + std::to_string(aig_network_before_opt.num_cis()) + " CIs, "
              + std::to_string(aig_network_before_opt.num_cos()) + " COs, "
              + std::to_string(aig_network_before_opt.num_gates()) + " GATEs.");
        Logger::error("AIG network after optimization: "
              + std::to_string(aig_network_after_opt.num_pis()) + " PIs, "
              + std::to_string(aig_network_after_opt.num_pos()) + " POs, "
              + std::to_string(aig_network_after_opt.num_cis()) + " CIs, "
              + std::to_string(aig_network_after_opt.num_cos()) + " COs, "
              + std::to_string(aig_network_after_opt.num_gates()) + " GATEs.");
        throw std::runtime_error("AIG networks after and before optimization have different number of PIs.");
    }

    // do sanity check, the aig_network_after_opt and aig_network_before_opt should have the same POs
    if (aig_network_after_opt.num_pos() != aig_network_before_opt.num_pos()) {
        Logger::error("AIG networks after and before optimization have different number of POs.");
        Logger::error("AIG network before optimization: " 
              + std::to_string(aig_network_before_opt.num_pis()) + " PIs, "
              + std::to_string(aig_network_before_opt.num_pos()) + " POs, "
              + std::to_string(aig_network_before_opt.num_cis()) + " CIs, "
              + std::to_string(aig_network_before_opt.num_cos()) + " COs, "
              + std::to_string(aig_network_before_opt.num_gates()) + " GATEs.");
        Logger::error("AIG network after optimization: "
              + std::to_string(aig_network_after_opt.num_pis()) + " PIs, "
              + std::to_string(aig_network_after_opt.num_pos()) + " POs, "
              + std::to_string(aig_network_after_opt.num_cis()) + " CIs, "
              + std::to_string(aig_network_after_opt.num_cos()) + " COs, "
              + std::to_string(aig_network_after_opt.num_gates()) + " GATEs.");
        throw std::runtime_error("AIG networks after and before optimization have different number of POs.");
    }
    

    // print the aig_network_before_opt information:
    Logger::info("AIG network before optimization: " 
              + std::to_string(aig_network_before_opt.num_pis()) + " PIs, "
              + std::to_string(aig_network_before_opt.num_pos()) + " POs, "
              + std::to_string(aig_network_before_opt.num_cis()) + " CIs, "
              + std::to_string(aig_network_before_opt.num_cos()) + " COs, "
              + std::to_string(aig_network_before_opt.num_gates()) + " GATEs.");

    Logger::info("AIG network after optimization: "
              + std::to_string(aig_network_after_opt.num_pis()) + " PIs, "
              + std::to_string(aig_network_after_opt.num_pos()) + " POs, "
              + std::to_string(aig_network_after_opt.num_cis()) + " CIs, "
              + std::to_string(aig_network_after_opt.num_cos()) + " COs, "
              + std::to_string(aig_network_after_opt.num_gates()) + " GATEs.");
    
    this->aig_network_after_opt_logic = mockturtle::aig_network(aig_network_after_opt);
    this->aig_network_before_opt_logic = mockturtle::aig_network(aig_network_before_opt);


    if (!cnf_clauses.empty()){
        check_cnf_conflit();
    }
}

aig_network aiger_checker::convert_cnf_to_aig()
{
    // convert cnf to aig_network
    // it should be noted that, the CNF variables can only contains the inputs and latches
    aig_network aig;
    std::vector<aig_network::signal> vars;

    // 1. create PIs for each variable in CNF clauses
    int max_var = this->aig_network_before_opt_logic.num_pis();
    if (max_var == 0) {
        Logger::warning("AIG network before optimization has 0 PIs, inferring max_var from CNF clauses.");
        max_var = 0;
        for (const auto& clause : cnf_clauses) {
            for (int lit : clause) {
                int var = std::abs(lit);
                if (var > max_var) {
                    max_var = var;
                }
            }
        }
    }

    for (int i = 0; i < max_var; ++i) {
        vars.push_back(aig.create_pi());
    }

    // 2. convert each clause to an AND gate with negated literals
    //    (clause = (l1 or l2 or ... ln) => AND(NOT(l1), NOT(l2), ..., NOT(ln)))
    std::vector<aig_network::signal> clause_signals;
    for (const auto& clause : cnf_clauses) {
        std::vector<aig_network::signal> negated_lits;
        for (int lit : clause) {
            int var = std::abs(lit) - 1; // 0-based
            aig_network::signal s = vars[var];
            if (lit > 0) {
                negated_lits.push_back(aig.create_not(s));
            } else {
                negated_lits.push_back(s);
            }
        }
        // AND all negated literals, then NOT (De Morgan: or = not(and(not)))
        aig_network::signal anded = negated_lits[0];
        for (size_t i = 1; i < negated_lits.size(); ++i) {
            anded = aig.create_and(anded, negated_lits[i]);
        }
        clause_signals.push_back(aig.create_not(anded));
    }

    // 3. and together all clause signals to create the final output
    //    (final output = AND(clause_signals[0], clause_signals[1], ..., clause_signals[n]))
    if (clause_signals.empty()) {
        Logger::error("No clauses in CNF.");
        throw std::runtime_error("No clauses in CNF.");
    }
    aig_network::signal out = clause_signals[0];
    for (size_t i = 1; i < clause_signals.size(); ++i) {
        out = aig.create_and(out, clause_signals[i]);
    }
    aig.create_po(out);
    Logger::info("Converted CNF clauses to AIGER network with " + std::to_string(max_var) + " variables and " 
              + std::to_string(cnf_clauses.size()) + " clauses.");
    return aig;
}



bool aiger_checker::check_cnf_conflit()
{
    this->cnf_clauses_aig = convert_cnf_to_aig();
    // create zero AIG network, all POs are constant false
    // the pi number should match cnf_clauses_aig
    if (cnf_clauses_aig.num_pis() == 0) {
        Logger::error("No PIs in CNF clauses AIG network.");
        return true;
    }
    aig_network zero_aig;
    for (uint32_t i = 0; i < cnf_clauses_aig.num_pis(); ++i) {
        zero_aig.create_pi();
    }
    zero_aig.create_po(zero_aig.get_constant(false));

    // generate miter
    auto miter_ntk_opt = mockturtle::miter<aig_network>(cnf_clauses_aig, zero_aig);
    
    if (!miter_ntk_opt) {
        Logger::error("Miter construction failed: networks have different number of PIs or POs.");
        return true;
    }
    const auto& miter_ntk = *miter_ntk_opt;

    // use equivalence_checking 
    auto result = mockturtle::equivalence_checking(miter_ntk);
    // result.has_value() && *result == true equivalence to false (cnf has conflict)
    if (!result.has_value()) {
        Logger::error("Equivalence checking failed.");
        return true;
    }
    return result && *result;
}

bool aiger_checker::check_equivalence(bool is_debug)
{
    this->cnf_clauses_aig_assumption = convert_cnf_to_aig();
    // create miter on the two AIG networks
    auto miter_ntk_opt = mockturtle::miter<aig_network>(aig_network_before_opt_logic, aig_network_after_opt_logic);
    if (!miter_ntk_opt) {
        Logger::error("Miter construction failed: networks have different number of PIs or POs.");
        return false;
    }
    auto& miter_ntk = *miter_ntk_opt;

    // concatenate the miter with the CNF clauses AIG network
    auto merged_network = merge_aig_networks_and_output(miter_ntk, cnf_clauses_aig_assumption);

    // debug: output dot if requested
    if (is_debug) {
        mockturtle::write_dot(merged_network, "merged_network.dot");
        Logger::info("Merged network written to merged_network.dot");
    }

    // use equivalence_checking on the merged network
    auto result = mockturtle::equivalence_checking(merged_network);

    if (!result.has_value()) {
        Logger::error("Equivalence checking failed.");
        return false;
    }
    // result.has_value() && *result == true means the two AIG networks are equivalent
    if (*result) {
        Logger::info("The AIG networks before and after optimization are equivalent.");
        return true;
    }
    Logger::info("The AIG networks before and after optimization are not equivalent.");
    // if not equivalent, we can also print the counter-example
    return false;
}

aig_network aiger_checker::merge_aig_networks_and_output(aig_network &n1, aig_network &n2)
{
    // make sure n1 and n2 have the same PIs
    if (n1.num_pis() != n2.num_pis()) {
        Logger::error("Cannot merge AIG networks: different number of PIs.");
        throw std::runtime_error("Cannot merge AIG networks: different number of PIs.");
    }
    // make sure n2 has only 1 PO
    if (n2.num_pos() != 1) {
        Logger::error("Cannot merge AIG networks: n2 must have only 1 PO.");
        throw std::runtime_error("Cannot merge AIG networks: n2 must have only 1 PO.");
    }
    // create a new aig_network to hold the merged network
    aig_network concat;
    std::vector<aig_network::signal> inputs;
    for (int i = 0; i < n1.num_pis(); ++i) {
        inputs.push_back(concat.create_pi());
    }
    // cleanup_dangling to copy the logic of n1 and n2 to concat
    auto outputs2 = mockturtle::cleanup_dangling(n2, concat, inputs.begin(), inputs.begin() + n1.num_pis());
    auto outputs1 = mockturtle::cleanup_dangling(n1, concat, inputs.begin(), inputs.begin() + n1.num_pis());
    // and the output of n1 to every PO of n2
    for (uint32_t i = 0; i < n1.num_pos(); ++i) {
        auto po_signal = n1.po_at(i);
        auto output_signal = outputs2[0]; // assuming n1 has only one output
        concat.create_po(concat.create_and(po_signal, output_signal));
    }
    Logger::info("Merged AIG networks: n1 and n2 with " + std::to_string(n1.num_pis()) + " PIs and "
              + std::to_string(n2.num_pos()) + " POs into a new AIG network with "
              + std::to_string(concat.num_pis()) + " PIs and "
              + std::to_string(concat.num_pos()) + " POs.");
    return concat;
}
