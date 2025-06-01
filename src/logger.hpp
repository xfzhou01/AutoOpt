#pragma once
#include <iostream>
#include <string>

class Logger {
public:
    static void info(const std::string& msg) {
        std::cout << "[INFO] " << msg << std::endl;
    }
    static void error(const std::string& msg) {
        std::cout << "[ERROR] " << msg << std::endl;
    }
    static void warning(const std::string& msg) {
        std::cout << "[WARNING] " << msg << std::endl;
    }
};
