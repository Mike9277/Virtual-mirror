// Created by Theodoros Aslanidis on 01/08/2025.

#include "CudaDrHandler.h"

using namespace log4cplus;

using gvirtus::communicators::Buffer;
using gvirtus::communicators::Result;

CUDA_DRIVER_HANDLER(MemAddressReserve) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("MemAddressReserve"));
    
    CUdeviceptr ptr;
    size_t size = input_buffer->Get<size_t>();
    size_t alignment = input_buffer->Get<size_t>();
    CUdeviceptr addr = input_buffer->Get<CUdeviceptr>();
    unsigned long long flags = input_buffer->Get<unsigned long long>();

    CUresult exit_code = cuMemAddressReserve(&ptr, size, alignment, addr, flags);
    
    std::shared_ptr<Buffer> out = std::make_shared<Buffer>();
    out->AddMarshal(ptr);
    
    LOG4CPLUS_DEBUG(logger, "cuMemAddressReserve executed, ptr: " << ptr);
    return std::make_shared<Result>((cudaError_t) exit_code, out);
}