#include "sanity_checker.hpp"

namespace sanity_check {

/** 
 * @brief Print error information
 */
void sanity_check_print_err(const std::string &err_msg) {
    std::cerr << "[ERROR] [sanity-check] " << err_msg << std::endl;
}

/**
 * @brief Checks if two files belong to the same directory.
 *
 * This function takes the paths of two files as input and determines
 * if they reside in the same directory by comparing their parent paths.
 *
 * @param file1 The path to the first file.
 * @param file2 The path to the second file.
 */
void sanity_check_file_same_dir(const std::string& file1, const std::string& file2) {
    std::filesystem::path path1(file1);
    std::filesystem::path path2(file2);

    // Check if both paths are files
    if (!std::filesystem::is_regular_file(path1) || !std::filesystem::is_regular_file(path2)) {
        std::string err_msg = file1 + " or " + file2 + " does not exists";
        sanity_check::sanity_check_print_err(err_msg);
        assert(false); // One of the paths is not a regular file
    }

    // Compare the parent paths (directories) of both files
    if (path1.parent_path() != path2.parent_path()) {
        std::string err_msg = file1 + " and " + file2 + " should be in the same folder but not";
        sanity_check::sanity_check_print_err(err_msg);
        assert(false);
    }
}

/**
 * Checks if the file path ends with the ".aig" extension.
 * 
 * @param filePath The file path to check.
 * @return true if the file path ends with ".aig", false otherwise.
 */
bool sanity_check_is_aig_file(const std::string& filePath) {
    // Define the extension we are looking for
    const std::string extension = ".aig";

    // Check if the file path is shorter than the extension itself
    if (filePath.length() < extension.length()) {
        std::string err_msg = "expected the file path to end with .aig but got " + filePath;
        sanity_check::sanity_check_print_err(err_msg);
        assert(false);
    }

    // Compare the end of the filePath with the extension
    // std::string::substr creates a substring starting from the index given to it
    // std::string::npos is used to take the substring to the end of the string
    // The index for the substring starts from the length of filePath minus the length of extension
    if  (!(filePath.substr(filePath.length() - extension.length()) == extension)) {
        std::string err_msg = "expected the file path to end with .aig but got " + filePath;
        sanity_check::sanity_check_print_err(err_msg);
        assert(false);
    }
}


/**
 * Checks if the file path ends with the ".aag" extension.
 * 
 * @param filePath The file path to check.
 * @return true if the file path ends with ".aag", false otherwise.
 */
bool sanity_check_is_aag_file(const std::string& filePath) {
    // Define the extension we are looking for
    const std::string extension = ".aag";

    // Check if the file path is shorter than the extension itself
    if (filePath.length() < extension.length()) {
        std::string err_msg = "expected the file path to end with .aag but got " + filePath;
        sanity_check::sanity_check_print_err(err_msg);
        assert(false);
    }

    // Compare the end of the filePath with the extension
    // std::string::substr creates a substring starting from the index given to it
    // std::string::npos is used to take the substring to the end of the string
    // The index for the substring starts from the length of filePath minus the length of extension
    if  (!(filePath.substr(filePath.length() - extension.length()) == extension)) {
        std::string err_msg = "expected the file path to end with .aig but got " + filePath;
        sanity_check::sanity_check_print_err(err_msg);
        assert(false);
    }
}


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
void check_string_is_empty(const std::string& str) {
    // Check if the string is empty
    if (str.empty()) {
        // Print error message if the string is empty
        sanity_check_print_err("The string is empty.");
        // Throw an exception
        assert(false);
    }
    // If the string is not empty, the function will simply return
}

// end of namespace
};
