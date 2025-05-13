/* also: Advanced Logic Synthesis and Optimization tool
 * Copyright (C) 2019- Ningbo University, Ningbo, China
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use,
 * copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following
 * conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 */
// #include "store.hpp"
// #include "commands/mighty.hpp"
// #include "commands/load.hpp"
// #include "commands/exact_imply.hpp"
// #include "commands/lut_mapping.hpp"
// #include "commands/lut_resyn.hpp"
// #include "commands/xmginv.hpp"
// #include "commands/exact_m5ig.hpp"
// #include "commands/exact_m3ig.hpp"
// #include "commands/exact_maj.hpp"
// #include "commands/exprsim.hpp"
// #include "commands/xmgrw.hpp"
// #include "commands/xmgrs.hpp"
// #include "commands/cutrw.hpp"
// #include "commands/xmgcost.hpp"
// #include "commands/write_dot.hpp"
// #include "commands/cog.hpp"
// #include "commands/test_tt.hpp"
// #include "commands/test_img.hpp"
// #include "commands/test_xagdec.hpp"
// #include "commands/imgrw.hpp"
// #include "commands/imgff.hpp"
// #include "commands/dm.hpp"
// #include "commands/xagrs.hpp"
// #include "commands/xagopt.hpp"
// #include "commands/xmgcost2.hpp"
// #include "commands/xagrw.hpp"
// #include "commands/xagban.hpp"
// #include "commands/stochastic.hpp"
// #include "commands/app.hpp"
// #include "commands/xmgban.hpp"
// #include "commands/heusto.hpp"
// #include "commands/techmap.hpp"
// #include "commands/exact_map.hpp"
// #include "commands/restore_names.hpp"

// ALICE_MAIN( also )
#include <mockturtle/mockturtle.hpp>
#include <mockturtle/io/aiger_reader.hpp>

#include <mockturtle/traits.hpp>
#include <mockturtle/networks/aig.hpp>
#include <mockturtle/networks/mig.hpp>
#include <mockturtle/networks/xag.hpp>
#include <mockturtle/networks/xmg.hpp>
#include <mockturtle/networks/klut.hpp>
#include <mockturtle/views/dont_care_view.hpp>
#include <mockturtle/algorithms/sim_resub.hpp>
#include <mockturtle/algorithms/cleanup.hpp>
#include <mockturtle/algorithms/equivalence_checking.hpp>
#include <mockturtle/algorithms/miter.hpp>

#include <string>
#include <vector>
#include <fstream>


int aig_translate_index_to_i_index(int index, int num_input) {
    // var index = 2, i0
    // the i index should not exceed, number of inputs
    int var_index = index / 2;
    // if (!var_index - 1 <= num_input - 1) {
    //     std::cerr << "Error: variable index exceeds number of inputs" << std::endl;
    //     std::cerr << "Variable index: " << var_index << std::endl;
    //     std::cerr << "Number of inputs: " << num_input << std::endl;
    //     assert(false);
    //     return -1;
    // }
    return var_index - 1;
}

void read_array_from_file( std::vector<std::vector<int>>& cnf_array, const std::string filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error opening file: " << filename << std::endl;
        return;
    }
    std::string line;
    while (std::getline(file, line)) {
        std::vector<int> row;
        std::istringstream iss(line);
        std::string number_str;
        int number;
        while (iss >> number_str) {
            number = std::stoi(number_str);
            row.push_back(number);
        }

        cnf_array.push_back(row);
    }

    file.close();
}

std::string get_first_line_of_file(const std::string &filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        return "";  // Return empty string if file can't be opened
    }
    std::string line;
    std::getline(file, line);
    return line;
}

void show_all_aig_input_name(const mockturtle::sequential<mockturtle::aig_network> &aig,
    const mockturtle::names_view<mockturtle::sequential<mockturtle::aig_network>> &named_aig) {
    std::cout << "show all pi in aig" << std::endl;
    for (int i = 0; i < aig.num_pis(); i++)
    {
        auto pi_i = aig.pi_at(i);
        auto pi_i_name = named_aig.get_name(aig.make_signal(pi_i));
        std::cout << "pi index " << i << " " << pi_i_name << std::endl;
    }
    std::cout << "------------" << std::endl;
}



void show_all_aig_comb_input_name(const mockturtle::sequential<mockturtle::aig_network> &aig,
    const mockturtle::names_view<mockturtle::sequential<mockturtle::aig_network>> &named_aig) {
    std::cout << "show all ci in aig" << std::endl;
    for (int i = 0; i < aig.num_cis(); i++)
    {
        auto pi_i = aig.ci_at(i);
        auto pi_i_name = named_aig.get_name(aig.make_signal(pi_i));
        std::cout << "ci index " << i << " " << pi_i_name << std::endl;
    }
    std::cout << "------------" << std::endl;
}

using namespace mockturtle;

// odc playground

// int main(int argc, char *argv[]) {
//     std::string aig_file_name = argv[1];
//     std::string po_index_tmp = argv[2];
//     //std::string cnf_file_name = argv[2];
//     std::cout << aig_file_name << std::endl;
//     using namespace mockturtle;
//     sequential<aig_network> aig;
//     names_view<sequential<aig_network>> named_aig{ aig };
//     lorina::text_diagnostics consumer;
//     lorina::diagnostic_engine diag( &consumer );
//     auto const result = lorina::read_ascii_aiger( aig_file_name, aiger_reader( named_aig ), &diag );
//     if (!(result == lorina::return_code::success)) {
//         assert(false);
//     }
//     std::cout << "first line of aig file: " << get_first_line_of_file(aig_file_name) << std::endl;
//     std::cout << "number of cis in aig: " << aig.num_cis() << std::endl;
//     std::cout << "number of pis in aig: " << aig.num_pis() << std::endl;
//     std::cout << "the size of aig: " << aig.size() << std::endl;

//     show_all_aig_input_name(aig,named_aig);
//     show_all_aig_comb_input_name(aig,named_aig);
//     std::vector<std::vector<int>> cnf_array;
//     std::cout << "start reading" << std::endl;
//     read_array_from_file(cnf_array, "/home/x/xiaofeng-zhou/AutoOpt/mock_project/test/cnf_read_test_cases/cnf.txt");
//     std::cout << "print read cnf file" << std::endl;
//     for (int i = 0; i < cnf_array.size(); i++)
//     {
//         auto &cnf_ = cnf_array[i];
//         for (int j = 0; j < cnf_.size(); j++)
//         {
//             std::cout << cnf_[j] << " ";
//         } std::cout << std::endl;
//     }

//     aig_network cdc;
//     std::vector<aig_network::signal> cdc_pi;
//     for (int i = 0; i < aig.num_cis(); i++)
//     {
//         cdc_pi.push_back(cdc.create_pi());
//     }
//     std::cout << "cdc_pi.size(): " << cdc_pi.size() << std::endl;
//     auto po = cdc_pi[std::stoi(po_index_tmp)];
//     //for (int i = 1; i < cdc_pi.size(); i++)
//     //{
//     //    po = cdc.create_or(po, cdc_pi[i]);
//     //}
//     cdc.create_po(po);
//     std::cout << "cdc number of pis: " << cdc.num_pis() << std::endl;;
//     std::cout << "aig number of pis: " << aig.num_pis() << std::endl;

//     std::cout << "init dc view" << std::endl;
//     dont_care_view<aig_network, true, false> exdc( aig, cdc );

    
//     resubstitution_params ps;
//     ps.verbose = 1;
//     // ps.odc_levels = -1;
//     std::cout << "start sim resub:" << std::endl;
//     std::cout << "before use EXCDC number of gates: " << aig.num_gates() << std::endl;
//     sim_resubstitution( exdc, ps );
//     std::cout << "end sim resub: " << std::endl;
//     std::cout << "before clean up EXCDC number of gates: " << aig.num_gates() << std::endl;
//     aig = cleanup_dangling( aig );
//     std::cout << "after  EXCDC number of gates: " << aig.num_gates() << std::endl;

    

    
//     return 0;
// }

int inv_literal(int literal) {
    if (literal % 2 == 0) {
        return literal + 1;
    } else {
        return literal - 1;
    }
}

int main(int argc, char *argv[]) {
    // a parser to parse the command line arguments
    // command line be like: ./out --aig_file_name xxx.aig --cnf_file_name xxx.cnf 
    std::string aig_file_name;
    std::string cnf_file_name;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--aig_file_name" && i + 1 < argc) {
            aig_file_name = argv[++i];
        } else if (arg == "--cnf_file_name" && i + 1 < argc) {
            cnf_file_name = argv[++i];
        } else {
            std::cerr << "Unknown argument: " << arg << std::endl;
            return 1;
        }
    }

    if (aig_file_name.empty() || cnf_file_name.empty()) {
        std::cerr << "Usage: " << argv[0] << " --aig_file_name <file.aig> --cnf_file_name <file.cnf>" << std::endl;
        return 1;
    }

    std::cout << "AIG file: " << aig_file_name << std::endl;
    std::cout << "CNF file: " << cnf_file_name << std::endl;

    // Add your logic to process the files here
    sequential<aig_network> aig;
    
    names_view<sequential<aig_network>> named_aig{ aig };
    lorina::text_diagnostics consumer;
    lorina::diagnostic_engine diag( &consumer );
    auto const aiger_read_results = lorina::read_ascii_aiger(aig_file_name,aiger_reader( named_aig ), &diag );

    // read the cnf file
    // cnf file format: each line is a clause, each number is a literal, positive number is a variable, negative number is a negated variable
    std::vector<std::vector<int>> cnf_array;
    read_array_from_file(cnf_array, cnf_file_name);

    std::vector<std::vector<int>> cnf_array_with_inv;
    // for (int i = 0; i < cnf_array.size(); i++) {
    //     std::vector<int> clause;
    //     for (int j = 0; j < cnf_array[i].size(); j++) {
    //         clause.push_back(inv_literal(cnf_array[i][j]));
    //     }
    //     cnf_array_with_inv.push_back(clause);
    // }


    // create a cdc network
    aig_network cdc;
    std::vector<aig_network::signal> cdc_pi;
    for (int i = 0; i < aig.num_cis(); i++) {
        cdc_pi.push_back(cdc.create_pi());
    }

    // push clauses into cdc
    auto po = cdc.get_constant(false);
    // for (int i = 1; i < 20; i++) {
    //     po = cdc.create_or(po, cdc_pi[i]);
    // }


    // auto po = cdc.get_constant(true);
    // for (int i = 0; i < cnf_array_with_inv.size(); i++) {
    //     auto clause = cnf_array_with_inv[i];
    //     auto clause_po = cdc.get_constant(true);
    //     for (int j = 0; j < clause.size(); j++) {
    //         auto literal = clause[j];
    //         auto var_index = aig_translate_index_to_i_index(literal, aig.num_pis());
    //         auto var_signal = cdc_pi[var_index];
    //         if (literal % 2 == 0) {
    //             clause_po = cdc.create_or(clause_po, var_signal);
    //         } else {
    //             clause_po = cdc.create_or(clause_po, cdc.create_not(var_signal));
    //         }
    //     }
    //     po = cdc.create_and(po, clause_po);
    // }
    cdc.create_po(po);

    
    // 
    resubstitution_params ps;
    ps.verbose = 1;
    dont_care_view<aig_network, true, false> exdc( aig, cdc );
    std::cout << "before use EXCDC number of gates: " << aig.num_gates() << std::endl;
    sim_resubstitution( exdc, ps );
    std::cout << "end sim resub: " << std::endl;
    std::cout << "before clean up EXCDC number of gates: " << aig.num_gates() << std::endl;
    aig = cleanup_dangling( aig );
    std::cout << "after  EXCDC number of gates: " << aig.num_gates() << std::endl;

    // equivalence checking with assumption
    // sequential<aig_network> aig_ori;
    // auto aig_ori = aig.clone();
    // std::cout << "start equivalence checking" << std::endl;
    // auto miter_ = *miter( exdc, aig_ori );
    // auto result = *equivalence_checking( miter );
    // std::cout << "equivalence checking result: " << result << std::endl;
    // aig.substitute_node(aig.get_node(), aig.po_at(1));
    // write_aiger( aig, "aig_after.aig" );
    return 0;
}