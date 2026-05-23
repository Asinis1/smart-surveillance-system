cmake_minimum_required(VERSION 3.10)
project(SmartSurveillance VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Release build by default
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS_RELEASE "-O2")

# ── Find OpenCV ──────────────────────────────────────────────────────────────
find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})

# ── Executable ───────────────────────────────────────────────────────────────
add_executable(surveillance surveillance.cpp)
target_link_libraries(surveillance ${OpenCV_LIBS})

# ── Install (optional) ────────────────────────────────────────────────────────
install(TARGETS surveillance DESTINATION bin)

message(STATUS "OpenCV version : ${OpenCV_VERSION}")
message(STATUS "Build type     : ${CMAKE_BUILD_TYPE}")