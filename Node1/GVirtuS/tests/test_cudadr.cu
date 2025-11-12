#include <gtest/gtest.h>
#include <cuda.h>

#define CUDA_CHECK(err) ASSERT_EQ((err), CUDA_SUCCESS)

TEST(cudaDR, getDriverVersion) {
    int version = 0;
    CUDA_CHECK(cuDriverGetVersion(&version));
    ASSERT_GT(version, 0);
}