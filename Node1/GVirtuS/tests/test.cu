// simple kernel launch test passes
#include <iostream>
#include <cuda_runtime.h>
#include <cudnn.h>
#include <vector>

using namespace std;

__global__ void simpleKernel(int* output) {
    *output = 123;
}

int main() {
    int* d_out = nullptr;
    int h_out = 0;

    // Allocate memory on device
    cudaMalloc(&d_out, sizeof(int));

    // Launch kernel with <<<>>> syntax
    simpleKernel<<<1, 1>>>(d_out);

    // Wait for kernel to complete
    cudaDeviceSynchronize();

    // Copy result back to host
    cudaMemcpy(&h_out, d_out, sizeof(int), cudaMemcpyDeviceToHost);

    cudaFree(d_out);
    std::cout << "Kernel output: " << h_out << std::endl;
}


// kernel launch with multiple blocks and threads test passes
// #include <iostream>
// #include <cuda_runtime.h>

// __global__ void simpleKernel(int* output, int N) {
//     int idx = blockIdx.x * blockDim.x + threadIdx.x;

//     if (idx < N) {
//         output[idx] = idx;  // Each thread writes its global index
//     }
// }

// int main() {
//     const int N = 100;  // total number of elements
//     const int threadsPerBlock = 32;
//     const int blocks = (N + threadsPerBlock - 1) / threadsPerBlock;  // ceil(N / threadsPerBlock)

//     int* d_out = nullptr;
//     int h_out[N];

//     // Allocate memory on device
//     cudaMalloc(&d_out, N * sizeof(int));

//     // Launch kernel with multiple blocks and threads
//     simpleKernel<<<blocks, threadsPerBlock>>>(d_out, N);

//     // Wait for kernel to complete
//     cudaDeviceSynchronize();

//     // Copy result back to host
//     cudaMemcpy(h_out, d_out, N * sizeof(int), cudaMemcpyDeviceToHost);

//     // Free device memory
//     cudaFree(d_out);

//     // Print result
//     std::cout << "Kernel output:\n";
//     for (int i = 0; i < N; ++i) {
//         std::cout << "h_out[" << i << "] = " << h_out[i] << "\n";
//     }

//     return 0;
// }


// kernel launch with multiple calls test passes
// #include <iostream>
// #include <cuda_runtime.h>

// __global__ void simpleKernel(int* output, int value) {
//     *output = value;
// }

// int main() {
//     int* d_out = nullptr;
//     int h_out = 0;

//     // Allocate memory on device
//     cudaMalloc(&d_out, sizeof(int));

//     // Call the kernel multiple times
//     for (int i = 0; i < 10; ++i) {
//         // Launch kernel with different value each time
//         simpleKernel<<<1, 1>>>(d_out, i * 100);

//         // Wait for kernel to complete
//         cudaDeviceSynchronize();

//         // Copy result back to host
//         cudaMemcpy(&h_out, d_out, sizeof(int), cudaMemcpyDeviceToHost);

//         std::cout << "Kernel call " << i << ", output: " << h_out << std::endl;
//     }

//     cudaFree(d_out);

//     return 0;
// }


// multiple kernel launch test passes
// #include <iostream>
// #include <cuda_runtime.h>

// __global__ void kernelA(int* output) {
//     *output = 111;
// }

// __global__ void kernelB(int* output) {
//     *output = 222;
// }

// __global__ void kernelC(int* output) {
//     *output = 333;
// }

// int main() {
//     int* d_out = nullptr;
//     int h_out = 0;

//     // Allocate memory on device
//     cudaMalloc(&d_out, sizeof(int));

//     // --- Launch kernel A
//     kernelA<<<1, 1>>>(d_out);
//     cudaDeviceSynchronize();
//     cudaMemcpy(&h_out, d_out, sizeof(int), cudaMemcpyDeviceToHost);
//     std::cout << "Kernel A output: " << h_out << std::endl;

//     // --- Launch kernel B
//     kernelB<<<1, 1>>>(d_out);
//     cudaDeviceSynchronize();
//     cudaMemcpy(&h_out, d_out, sizeof(int), cudaMemcpyDeviceToHost);
//     std::cout << "Kernel B output: " << h_out << std::endl;

//     // --- Launch kernel C
//     kernelC<<<1, 1>>>(d_out);
//     cudaDeviceSynchronize();
//     cudaMemcpy(&h_out, d_out, sizeof(int), cudaMemcpyDeviceToHost);
//     std::cout << "Kernel C output: " << h_out << std::endl;

//     // Free device memory
//     cudaFree(d_out);

//     return 0;
// }


// cudaMemcpyFromSymbol test failing
// #include <iostream>
// #include <cuda_runtime.h>

// // Declare __device__ global variables
// __device__ int globalCounter = 0;
// __device__ float globalValue = 42.42f;

// __global__ void kernelIncrementCounter() {
//     globalCounter += 1;
// }

// __global__ void kernelMultiplyValue() {
//     globalValue *= 2.0f;
// }

// int main() {
//     // Host copies of the global variables
//     int h_counter = 0;
//     float h_value = 0.0f;

//     // Launch first kernel
//     kernelIncrementCounter<<<1, 1>>>();
//     cudaDeviceSynchronize();

//     // Launch second kernel
//     kernelMultiplyValue<<<1, 1>>>();
//     cudaDeviceSynchronize();

//     // Copy back the global variables from device to host
//     // cudaMemcpyFromSymbol(&h_counter, globalCounter, sizeof(int), 0, cudaMemcpyDeviceToHost);
//     // cudaMemcpyFromSymbol(&h_value, globalValue, sizeof(float), 0, cudaMemcpyDeviceToHost);

//     // // Print values
//     // std::cout << "Global counter after kernel: " << h_counter << std::endl;
//     // std::cout << "Global value after kernel: " << h_value << std::endl;

//     return 0;
// }


// kernel launch with parameters test passes
// #include <iostream>
// #include <cuda_runtime.h>

// __global__ void myKernel(int a, float b, float* out) {
//     int idx = threadIdx.x + blockIdx.x * blockDim.x;
//     out[idx] = a * b + idx;
// }

// int main() {
//     const int N = 16;
//     const int threadsPerBlock = 4;
//     const int blocksPerGrid = (N + threadsPerBlock - 1) / threadsPerBlock;

//     float* d_out = nullptr;
//     float h_out[N];

//     int paramA = 7;
//     float paramB = 3.14f;

//     // Allocate memory on device
//     cudaMalloc(&d_out, N * sizeof(float));

//     // Launch kernel with parameters
//     myKernel<<<blocksPerGrid, threadsPerBlock>>>(paramA, paramB, d_out);

//     // Wait for kernel to complete
//     cudaDeviceSynchronize();

//     // Copy result back to host
//     cudaMemcpy(h_out, d_out, N * sizeof(float), cudaMemcpyDeviceToHost);

//     // Print results
//     for (int i = 0; i < N; ++i) {
//         std::cout << "h_out[" << i << "] = " << h_out[i] << std::endl;
//     }

//     // Cleanup
//     cudaFree(d_out);

//     return 0;
// }


// kernel launch with function pointer test fails due to bug in cudaMemcpyFromSymbol
// #include <iostream>
// #include <cuda_runtime.h>

// __device__ float myOp1(int x) {
//     return x * 2.0f;
// }

// __device__ float myOp2(int x) {
//     return x + 42.0f;
// }

// typedef float (*deviceFuncPtr)(int);

// __global__ void applyFunctionKernel(deviceFuncPtr func, float* out, int N) {
//     int idx = threadIdx.x + blockIdx.x * blockDim.x;
//     if (idx < N) {
//         out[idx] = func(idx);
//     }
// }

// int main() {
//     const int N = 16;
//     float h_out[N];
//     float* d_out;

//     cudaMalloc(&d_out, N * sizeof(float));

//     // Choose function to pass
//     deviceFuncPtr d_funcPtr;
//     cudaMemcpyFromSymbol(&d_funcPtr, myOp1, sizeof(deviceFuncPtr));

//     // Launch kernel with function pointer
//     applyFunctionKernel<<<2, 8>>>(d_funcPtr, d_out, N);

//     cudaDeviceSynchronize();
//     cudaMemcpy(h_out, d_out, N * sizeof(float), cudaMemcpyDeviceToHost);

//     for (int i = 0; i < N; ++i) {
//         std::cout << "h_out[" << i << "] = " << h_out[i] << std::endl;
//     }

//     cudaFree(d_out);
//     return 0;
// }

// kernel launch with array parameter test passes
// #include <iostream>
// #include <cuda_runtime.h>

// __global__ void addKernel(int* arr, int N, int valueToAdd) {
//     int idx = threadIdx.x + blockIdx.x * blockDim.x;
//     if (idx < N) {
//         arr[idx] += valueToAdd;
//     }
// }

// int main() {
//     const int N = 10;
//     int h_array[N];

//     // Initialize host array
//     for (int i = 0; i < N; ++i) {
//         h_array[i] = i;
//     }

//     int* d_array;
//     cudaMalloc(&d_array, N * sizeof(int));

//     // Copy array from host to device
//     cudaMemcpy(d_array, h_array, N * sizeof(int), cudaMemcpyHostToDevice);

//     // Launch kernel: 2 blocks of 5 threads (total 10 threads)
//     int valueToAdd = 100;
//     addKernel<<<2, 5>>>(d_array, N, valueToAdd);

//     cudaDeviceSynchronize();

//     // Copy result back to host
//     cudaMemcpy(h_array, d_array, N * sizeof(int), cudaMemcpyDeviceToHost);

//     // Print results
//     for (int i = 0; i < N; ++i) {
//         std::cout << "h_array[" << i << "] = " << h_array[i] << std::endl;
//     }

//     cudaFree(d_array);
//     return 0;
// }

// int main() {
//  // Initialize cuDNN
//     cudnnHandle_t cudnn;
//     cudnnCreate(&cudnn);

//     int n = 1, c = 1, h = 5, w = 5;
//     // Allocate and initialize host memory
//     std::vector<float> h_input(n * c * h * w, 1.0f);   // Input filled with ones

//     // Allocate device memory
//     float *d_input;
//     cudaMalloc(&d_input, h_input.size() * sizeof(float));

//     cout << "d_input = " <<  d_input << endl;
// }
