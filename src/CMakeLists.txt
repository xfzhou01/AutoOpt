#include_directories(commands)

file(GLOB_RECURSE FILENAMES *.cpp)
list(REMOVE_ITEM FILENAMES ${CMAKE_CURRENT_SOURCE_DIR}/test_aiger_checker.cpp)
list(REMOVE_ITEM FILENAMES ${CMAKE_CURRENT_SOURCE_DIR}/test_network_concat.cpp)
list(REMOVE_ITEM FILENAMES ${CMAKE_CURRENT_SOURCE_DIR}/test_aiger_naive_optimizer.cpp)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

message(STATUS "The value of CMAKE_BINARY_DIR is: ${CMAKE_BINARY_DIR}")
message(STATUS "The value of FILENAMES is: ${FILENAMES}")

# Avoid using reserved target name 'test' when CTest is enabled
add_executable(main_exec main.cpp ${FILENAMES})
target_link_libraries(main_exec mockturtle)

# Add unit test for aiger_checker
add_executable(test_aiger_checker test_aiger_checker.cpp aiger_checker.cpp)
target_link_libraries(test_aiger_checker PRIVATE mockturtle)
add_test(NAME test_aiger_checker COMMAND test_aiger_checker)

# Add executable for network concatenation test
add_executable(test_network_concat test_network_concat.cpp)
target_link_libraries(test_network_concat PRIVATE mockturtle)

# Add unit test for aiger_naive_optimizer
add_executable(test_aiger_naive_optimizer test_aiger_naive_optimizer.cpp aiger_naive_optimizer.cpp)
target_link_libraries(test_aiger_naive_optimizer PRIVATE mockturtle)
add_test(NAME test_aiger_naive_optimizer COMMAND test_aiger_naive_optimizer)
