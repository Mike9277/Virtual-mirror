# Install script for directory: /home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS

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
   "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/include/gvirtus")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/include" TYPE DIRECTORY FILES "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/include/gvirtus")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-common.so")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib" TYPE SHARED_LIBRARY FILES "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/libgvirtus-common.so")
  if(EXISTS "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-common.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-common.so")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-common.so")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/include/nlohmann")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/include" TYPE DIRECTORY FILES "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/include/nlohmann")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/etc")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS" TYPE DIRECTORY FILES "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/etc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-communicators.so")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib" TYPE SHARED_LIBRARY FILES "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/libgvirtus-communicators.so")
  if(EXISTS "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-communicators.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-communicators.so")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-communicators.so")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-communicators-tcp.so")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib" TYPE SHARED_LIBRARY FILES "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/libgvirtus-communicators-tcp.so")
  if(EXISTS "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-communicators-tcp.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-communicators-tcp.so")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-communicators-tcp.so")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-communicators-ib.so")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib" TYPE SHARED_LIBRARY FILES "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/libgvirtus-communicators-ib.so")
  if(EXISTS "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-communicators-ib.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-communicators-ib.so")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-communicators-ib.so")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-frontend.so")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib" TYPE SHARED_LIBRARY FILES "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/libgvirtus-frontend.so")
  if(EXISTS "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-frontend.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-frontend.so")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/lib/libgvirtus-frontend.so")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/bin/gvirtus-backend")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/bin" TYPE EXECUTABLE FILES "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/gvirtus-backend")
  if(EXISTS "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/bin/gvirtus-backend" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/bin/gvirtus-backend")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/bin/gvirtus-backend")
    endif()
  endif()
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/plugins/cudart/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/plugins/cudadr/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/plugins/cublas/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/plugins/cufft/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/plugins/cusolver/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/plugins/cusparse/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/plugins/curand/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/plugins/nvrtc/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/plugins/cudnn/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/tests/cmake_install.cmake")
endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
