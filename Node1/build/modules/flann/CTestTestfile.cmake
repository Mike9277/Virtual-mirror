# CMake generated Testfile for 
# Source directory: /home/cldemo/guaitolini/virtual_mirror/opencv/modules/flann
# Build directory: /home/cldemo/guaitolini/virtual_mirror/build/modules/flann
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(opencv_test_flann "/home/cldemo/guaitolini/virtual_mirror/build/bin/opencv_test_flann" "--gtest_output=xml:opencv_test_flann.xml")
set_tests_properties(opencv_test_flann PROPERTIES  LABELS "Main;opencv_flann;Accuracy" WORKING_DIRECTORY "/home/cldemo/guaitolini/virtual_mirror/build/test-reports/accuracy" _BACKTRACE_TRIPLES "/home/cldemo/guaitolini/virtual_mirror/opencv/cmake/OpenCVUtils.cmake;1799;add_test;/home/cldemo/guaitolini/virtual_mirror/opencv/cmake/OpenCVModule.cmake;1365;ocv_add_test_from_target;/home/cldemo/guaitolini/virtual_mirror/opencv/cmake/OpenCVModule.cmake;1123;ocv_add_accuracy_tests;/home/cldemo/guaitolini/virtual_mirror/opencv/modules/flann/CMakeLists.txt;2;ocv_define_module;/home/cldemo/guaitolini/virtual_mirror/opencv/modules/flann/CMakeLists.txt;0;")
