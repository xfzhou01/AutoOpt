
#ifndef __UTILS_SANITY_CHECKER_HPP__
#define __UTILS_SANITY_CHECKER_HPP__
#include <string>
#include <cassert>
#include <filesystem>
#include <iostream>

namespace sanity_check {

/** 
 * @brief Print error information
 */
void sanity_check_print_err(const std::string &err_msg);

/**
 * @brief Checks if two files belong to the same directory.
 *
 * This function takes the paths of two files as input and determines
 * if they reside in the same directory by comparing their parent paths.
 *
 * @param file1 The path to the first file.
 * @param file2 The path to the second file.
 */
void sanity_check_file_same_dir(const std::string& file1, const std::string& file2);


/**
 * Checks if the file path ends with the ".aig" extension.
 * 
 * @param filePath The file path to check.
 * @return true if the file path ends with ".aig", false otherwise.
 */
bool sanity_check_is_aig_file(const std::string& filePath);

/**
 * Checks if the file path ends with the ".aag" extension.
 * 
 * @param filePath The file path to check.
 * @return true if the file path ends with ".aag", false otherwise.
 */
bool sanity_check_is_aag_file(const std::string& filePath);


/**
 * @brief Checks if a string is empty.
 * 
 * This function checks if the provided string is empty. If the string is 
 * empty, it prints an error message and asserts false, indicating a 
 * failure condition. If the string is not empty, the function completes 
 * without any action.
 *
 * @param str The string to be checked.
 */
void check_string_is_empty(const std::string& str);

// end of namespace
};



#endif