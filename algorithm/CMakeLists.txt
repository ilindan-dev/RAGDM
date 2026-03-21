cmake_minimum_required(VERSION 3.10)

project(SpacedRepetition C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED True)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(CMAKE_COMPILER_IS_GNUCC OR CMAKE_C_COMPILER_ID MATCHES "Clang")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -pedantic -Werror")
endif()

include_directories(include)

add_library(spaced_rep STATIC
        src/algorithm.c
)

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_algorithm.c")
    add_executable(test_algorithm
            tests/test_algorithm.c
    )
    target_link_libraries(test_algorithm spaced_rep)
endif()