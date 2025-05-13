/**
 * @file opt_aiger_reader.hpp
 *
 * @brief an interface to take in both aag and aig
 *
 * @author Zhufei Chu
 * @since  0.1
 */


#ifndef __HLSINV_IO_OPT_AIGER_READER_HPP__
#define __HLSINV_IO_OPT_AIGER_READER_HPP__

#include <mockturtle/io/aiger_reader.hpp>
#include <mockturtle/networks/aig.hpp>
#include <mockturtle/networks/sequential.hpp>
#include <mockturtle/views/names_view.hpp>
#include <string>
#include "../utils/sanity_checker.hpp"

using namespace mockturtle;

class opt_aiger_reader
{
private:
    std::string aag_file_path;
    std::string aig_file_path;

    int aag_M;
    int aag_input_count;
    int aag_latch_count;
    int aag_output_count;
    int aag_and_gate_count;
    int aig_M;
    int aig_input_count;
    int aig_latch_count;
    int aig_output_count;
    int aig_and_gate_count;

    // the aig instance
    aig_network aig;
    names_view<aig_network> named_aig;
public:
    opt_aiger_reader(const std::string &aig_file_path, const std::string &aag_file_path);
    ~opt_aiger_reader();

    static void opt_aiger_reader_print_err(const std::string &err_msg);
    static void opt_aiger_reader_print_info(const std::string &info_msg);
    static void opt_aiger_reader_print_warning(const std::string &warning_msg);


    
private:

    /** 
    * @brief read aiger file
    */
    void read_aiger();

    /**
     * @brief read aiger file encoded in ascii format, this function only derives variable mapping 
     */
    void read_aag();
    /**
     * @brief do some sanity check to make sure the read is correct
     */
    void sanity_check_read_files();
};




#endif