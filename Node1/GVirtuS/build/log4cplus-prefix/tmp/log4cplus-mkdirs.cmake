# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/log4cplus-prefix/src/log4cplus"
  "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/log4cplus-prefix/src/log4cplus-build"
  "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/log4cplus-prefix"
  "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/log4cplus-prefix/tmp"
  "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/log4cplus-prefix/src/log4cplus-stamp"
  "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/log4cplus-prefix/src"
  "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/log4cplus-prefix/src/log4cplus-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/log4cplus-prefix/src/log4cplus-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/build/log4cplus-prefix/src/log4cplus-stamp${cfgdir}") # cfgdir has leading slash
endif()
