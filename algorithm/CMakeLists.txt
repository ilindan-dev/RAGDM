cmake_minimum_required(VERSION 3.10)

project(SpacedRepetition C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED True)

include_directories(include)

add_library(spaced_rep STATIC
        src/algorithm.c
)