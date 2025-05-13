#include "opt_aiger_reader.hpp"



opt_aiger_reader::opt_aiger_reader(const std::string &aig_file_path, const std::string &aag_file_path) : named_aig(aig) {
    this->aig_file_path = aig_file_path;
    this->aag_file_path = aag_file_path;
    sanity_check::sanity_check_is_aig_file(aig_file_path);
    sanity_check::sanity_check_is_aag_file(aag_file_path);
    sanity_check::sanity_check_file_same_dir(aig_file_path, aag_file_path);

    
    
}

opt_aiger_reader::~opt_aiger_reader()
{
}

void opt_aiger_reader::opt_aiger_reader_print_err(const std::string &err_msg)
{
    std::cerr << "[ERROR] [opt-aiger-reader] " << err_msg << std::endl;
}

void opt_aiger_reader::opt_aiger_reader_print_info(const std::string &info_msg)
{
    std::cout << "[INFO] [opt-aiger-reader] " << info_msg << std::endl;
}

void opt_aiger_reader::opt_aiger_reader_print_warning(const std::string &warning_msg)
{
    std::cout << "[WARNING] [opt-aiger-reader] " << warning_msg << std::endl;
}



void opt_aiger_reader::read_aag()
{
    std::ifstream file(this->aig_file_path); 
    if (!file) {    
        std::string err_msg = "the aag file does not exist, file path is: " + this->aig_file_path;
        opt_aiger_reader_print_err(err_msg);
        assert(false);
    }


}

void opt_aiger_reader::sanity_check_read_files()
{
}

void opt_aiger_reader::read_aiger()
{
    std::ifstream file(this->aig_file_path); 
    if (!file) {    
        std::string err_msg = "the aig file does not exist, file path is: " + this->aig_file_path;
        opt_aiger_reader_print_err(err_msg);
        assert(false);
    }
    std::string fileContents;
    std::string line;
    // Read file line by line
    while (std::getline(file, line)) {
        fileContents += line + "\n"; // Append to the string
    }
    file.close(); // Close the file
    std::istringstream iss(fileContents);
    auto const result = lorina::read_aiger( iss, aiger_reader( this->named_aig ) );
}
