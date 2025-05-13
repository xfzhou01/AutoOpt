#include_directories(commands)

file(GLOB_RECURSE FILENAMES *.cpp)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

message(STATUS "The value of CMAKE_BINARY_DIR is: ${CMAKE_BINARY_DIR}")
message(STATUS "The value of FILENAMES is: ${FILENAMES}")

add_executable(test main.cpp ${FILENAMES})

target_link_libraries(test mockturtle)
