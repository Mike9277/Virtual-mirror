# Install script for directory: /home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/plugins/cudart/demo

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/add_grid.e")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart" TYPE EXECUTABLE FILES "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/plugins/cudart/demo/add_grid.e")
  if(EXISTS "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/add_grid.e" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/add_grid.e")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/add_grid.e")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/dummy0.e")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart" TYPE EXECUTABLE FILES "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/plugins/cudart/demo/dummy0.e")
  if(EXISTS "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/dummy0.e" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/dummy0.e")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/dummy0.e")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/launchKernel.e")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart" TYPE EXECUTABLE FILES "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/plugins/cudart/demo/launchKernel.e")
  if(EXISTS "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/launchKernel.e" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/launchKernel.e")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/launchKernel.e")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/matrixMul.e")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart" TYPE EXECUTABLE FILES "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/plugins/cudart/demo/matrixMul.e")
  if(EXISTS "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/matrixMul.e" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/matrixMul.e")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/demo/cudart/matrixMul.e")
    endif()
  endif()
endif()

