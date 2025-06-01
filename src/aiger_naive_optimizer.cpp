#include "aiger_naive_optimizer.hpp"

aiger_naive_optimizer::aiger_naive_optimizer(
    const sequential<aig_network, true> &aig_network_before_opt) 
:aig_network_before_opt(aig_network_before_opt) 
{
    // Initialize the aig_network_during_opt with the original network
    this->aig_network_during_opt = aig_network_before_opt;
    // Print the initial state of the AIG network before optimization
    Logger::info("AIG network before optimization: " 
                 + std::to_string(aig_network_before_opt.num_pis()) + " PIs, "
                 + std::to_string(aig_network_before_opt.num_pos()) + " POs, "
                 + std::to_string(aig_network_before_opt.num_cis()) + " CIs, "
                 + std::to_string(aig_network_before_opt.num_cos()) + " COs, "
                 + std::to_string(aig_network_before_opt.num_gates()) + " GATEs.");
}

void aiger_naive_optimizer::optimize(int target_gate, int method)
{
    // update the set of gates that is already optimized
    Logger::info("Optimizing gate " + std::to_string(target_gate) + " using method " + std::to_string(method));
    // Perform optimization based on the method

    switch (method) {
        case 0: // Set output to constant 0
            optimize_set_zero(target_gate);
            break;
        case 1: // Set output to constant 1
            optimize_set_one(target_gate);
            break;
        case 2: // Optimize A input
            optimize_A_input(target_gate);
            break;
        case 3: // Optimize A input NOT
            optimize_A_input_not(target_gate);
            break;
        case 4: // Optimize B input
            optimize_B_input(target_gate);
            break;
        case 5: // Optimize B input NOT
            optimize_B_input_not(target_gate);
            break;
        default:
            Logger::error("Unknown optimization method: " + std::to_string(method));
            throw std::runtime_error("Unknown optimization method");
    }
}



void aiger_naive_optimizer::optimize_set_zero(int target_gate)
{
    // Set the output of the target gate to constant 0
    auto opt_net = this->aig_network_during_opt;
    // get the aig network from the sequential network
    aig_network& aig = static_cast<aig_network&>(opt_net);
    // substitute the target gate with constant false
    aig.substitute_node(aig.index_to_node(target_gate), aig.get_constant(false));
    // cleanup the network to remove dangling nodes
    //aig = mockturtle::cleanup_dangling(aig);
    // Print the optimization result
    this->aig_network_during_opt = opt_net; // Update the network after optimization
}

void aiger_naive_optimizer::optimize_set_one(int target_gate)
{
    // Set the output of the target gate to constant 1
    auto opt_net = this->aig_network_during_opt;
    // get the aig network from the sequential network
    aig_network& aig = static_cast<aig_network&>(opt_net);
    // substitute the target gate with constant false
    aig.substitute_node(aig.index_to_node(target_gate), aig.get_constant(true));
    // cleanup the network to remove dangling nodes
    //aig = mockturtle::cleanup_dangling(aig);
    //
    this->aig_network_during_opt = opt_net;
}

void aiger_naive_optimizer::optimize_A_input(int target_gate)
{
    // copy net
    auto opt_net = this->aig_network_during_opt;
    aig_network& aig = static_cast<aig_network&>(opt_net);
    // get the target gate node
    auto node = aig.index_to_node(target_gate);
    // Sanity check: node must have exactly two inputs
    int fanin_count = 0;
    aig.foreach_fanin(node, [&](auto, auto) { ++fanin_count; });
    if (fanin_count != 2) {
        throw std::runtime_error("optimize_A_input: target gate does not have exactly two inputs, input count: " + std::to_string(fanin_count));
    }
    // get 1st input
    aig_network::signal a_input;
    int idx = 0;
    aig.foreach_fanin(node, [&](auto s, auto i) {
        if (i == 0) a_input = s;
    });
    // sub
    aig.substitute_node(node, a_input);
    //aig = mockturtle::cleanup_dangling(aig);
    this->aig_network_during_opt = opt_net;
}

void aiger_naive_optimizer::optimize_A_input_not(int target_gate)
{
    // copy net
    auto opt_net = this->aig_network_during_opt;
    aig_network& aig = static_cast<aig_network&>(opt_net);
    // get the target gate node
    auto node = aig.index_to_node(target_gate);
    // Sanity check: node must have exactly two inputs
    int fanin_count = 0;
    aig.foreach_fanin(node, [&](auto, auto) { ++fanin_count; });
    if (fanin_count != 2) {
        throw std::runtime_error("optimize_A_input_not: target gate does not have exactly two inputs, input count: " + std::to_string(fanin_count));
    }
    // get 1st input and invert
    aig_network::signal a_input;
    aig.foreach_fanin(node, [&](auto s, auto i) {
        if (i == 0) a_input = s;
    });
    auto not_a_input = aig.create_not(a_input);
    // substitute
    aig.substitute_node(node, not_a_input);
    //aig = mockturtle::cleanup_dangling(aig);
    this->aig_network_during_opt = opt_net;
}


void aiger_naive_optimizer::optimize_B_input(int target_gate)
{
    // copy net
    auto opt_net = this->aig_network_during_opt;
    aig_network& aig = static_cast<aig_network&>(opt_net);
    // get the target gate node
    auto node = aig.index_to_node(target_gate);
    // Sanity check: node must have exactly two inputs
    int fanin_count = 0;
    aig.foreach_fanin(node, [&](auto, auto) { ++fanin_count; });
    if (fanin_count != 2) {
        throw std::runtime_error("optimize_B_input: target gate does not have exactly two inputs, input count: " + std::to_string(fanin_count));
    }
    // get 1st input
    aig_network::signal b_input;
    aig.foreach_fanin(node, [&](auto s, auto i) {
        if (i == 1) b_input = s;
    });
    // sub
    aig.substitute_node(node, b_input);
    //aig = mockturtle::cleanup_dangling(aig);
    this->aig_network_during_opt = opt_net;
}

void aiger_naive_optimizer::optimize_B_input_not(int target_gate)
{
    // copy net
    auto opt_net = this->aig_network_during_opt;
    aig_network& aig = static_cast<aig_network&>(opt_net);
    // get the target gate node
    auto node = aig.index_to_node(target_gate);
    // Sanity check: node must have exactly two inputs
    int fanin_count = 0;
    aig.foreach_fanin(node, [&](auto, auto) { ++fanin_count; });
    if (fanin_count != 2) {
        throw std::runtime_error("optimize_B_input_not: target gate does not have exactly two inputs, input count: " + std::to_string(fanin_count));
    }
    // get 1st input and invert
    aig_network::signal b_input;
    aig.foreach_fanin(node, [&](auto s, auto i) {
        if (i == 1) b_input = s;
    });
    auto not_b_input = aig.create_not(b_input);
    // substitute
    aig.substitute_node(node, not_b_input);
    //aig = mockturtle::cleanup_dangling(aig);
    this->aig_network_during_opt = opt_net;
}

// Getter for the optimized network
const sequential<aig_network, true>& aiger_naive_optimizer::get_optimized_network() const {
    return aig_network_during_opt;
}

sequential<aig_network, true>& aiger_naive_optimizer::get_optimized_network() {
    return aig_network_during_opt;
}

void aiger_naive_optimizer::keep_optimized_network()
{
    this->aig_network_after_opt = this->aig_network_during_opt;
    Logger::info("Optimized AIG network kept after optimization: " 
                 + std::to_string(aig_network_after_opt.num_pis()) + " PIs, "
                 + std::to_string(aig_network_after_opt.num_pos()) + " POs, "
                 + std::to_string(aig_network_after_opt.num_cis()) + " CIs, "
                 + std::to_string(aig_network_after_opt.num_cos()) + " COs, "
                 + std::to_string(aig_network_after_opt.num_gates()) + " GATEs.");
}

void aiger_naive_optimizer::reset_optimized_network_by_last()
{
    this->aig_network_during_opt = this->aig_network_after_opt;
    Logger::info("Optimized AIG network reset to last kept state: " 
                 + std::to_string(aig_network_during_opt.num_pis()) + " PIs, "
                 + std::to_string(aig_network_during_opt.num_pos()) + " POs, "
                 + std::to_string(aig_network_during_opt.num_cis()) + " CIs, "
                 + std::to_string(aig_network_during_opt.num_cos()) + " COs, "
                 + std::to_string(aig_network_during_opt.num_gates()) + " GATEs.");
}

int aiger_naive_optimizer::get_next_target_gate(int target_gate_index, bool is_successful)
{
    // TODO: consider clean up dangling
    // if is successful, means the target_gate is already eliminated,
    // return the next target gate for optimization
    if (aig_network_during_opt.num_gates() == 0) {
        Logger::info("No gates available for optimization.");
        return -1; // No gates to optimize
    }

    // Iterate the gates in the network,
    // the order is in reverse topological order
    return target_gate_index - 1;
}
