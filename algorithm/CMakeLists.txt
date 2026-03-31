cmake_minimum_required(VERSION 3.14)

project(SpacedRepetition C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_C_STANDARD_REQUIRED True)
set(CMAKE_CXX_STANDARD_REQUIRED True)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -pedantic -Werror")
endif()

include_directories(include)

add_library(spaced_rep STATIC src/algorithm.c)

include(FetchContent)
FetchContent_Declare(
        googletest
        URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
        DOWNLOAD_EXTRACT_TIMESTAMP true
)

set(INSTALL_GTEST OFF CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_algorithm.cpp")
    add_executable(test_algorithm tests/test_algorithm.cpp)

    target_link_libraries(test_algorithm
            PRIVATE
            spaced_rep
            GTest::gtest_main
            m
    )

    include(GoogleTest)
    include(CTest)
    gtest_discover_tests(test_algorithm)
endif()