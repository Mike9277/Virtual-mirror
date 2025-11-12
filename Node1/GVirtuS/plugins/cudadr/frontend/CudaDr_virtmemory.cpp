// Created by Theodoros Aslanidis on 01/08/2025.

#include "CudaDr.h"

using namespace std;

extern CUresult cuMemAddressReserve(CUdeviceptr* ptr, size_t size, size_t alignment, CUdeviceptr addr, unsigned long long flags) {
    CudaDrFrontend::Prepare();
    CudaDrFrontend::AddVariableForArguments(size);
    CudaDrFrontend::AddVariableForArguments(alignment);
    CudaDrFrontend::AddVariableForArguments(addr);
    CudaDrFrontend::AddVariableForArguments(flags);
    CudaDrFrontend::Execute("cuMemAddressReserve");
    if (CudaDrFrontend::Success()) {
        *ptr = CudaDrFrontend::GetOutputVariable<CUdeviceptr>();
    }
    return CudaDrFrontend::GetExitCode();
}