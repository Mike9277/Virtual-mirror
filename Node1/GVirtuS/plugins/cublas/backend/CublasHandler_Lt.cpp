#include "CublasHandler.h"
#include <cuda_runtime.h>

using gvirtus::communicators::Buffer;
using gvirtus::communicators::Result;

CUBLAS_ROUTINE_HANDLER(LtMatmulAlgoGetHeuristic) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("LtMatmulAlgoGetHeuristic"));
    
    cublasLtHandle_t lightHandle = in->Get<cublasLtHandle_t>();
    cublasLtMatmulDesc_t operationDesc = in->Get<cublasLtMatmulDesc_t>();
    cublasLtMatrixLayout_t Adesc = in->Get<cublasLtMatrixLayout_t>();
    cublasLtMatrixLayout_t Bdesc = in->Get<cublasLtMatrixLayout_t>();
    cublasLtMatrixLayout_t Cdesc = in->Get<cublasLtMatrixLayout_t>();
    cublasLtMatrixLayout_t Ddesc = in->Get<cublasLtMatrixLayout_t>();
    cublasLtMatmulPreference_t preference = in->Get<cublasLtMatmulPreference_t>();
    int requestedAlgoCount = in->Get<int>();

    cublasLtMatmulHeuristicResult_t heuristicResultsArray[requestedAlgoCount];
    int returnAlgoCount;

    LOG4CPLUS_DEBUG(logger, "Executing LtMatmulAlgoGetHeuristic with requestedAlgoCount: "
        << requestedAlgoCount);

    // Call the actual CUBLAS function
    cublasStatus_t cs = cublasLtMatmulAlgoGetHeuristic(lightHandle, operationDesc, Adesc, Bdesc, Cdesc, Ddesc,
                                        preference, requestedAlgoCount, heuristicResultsArray, &returnAlgoCount);
    if (cs != CUBLAS_STATUS_SUCCESS) {
        LOG4CPLUS_ERROR(logger, "Failed to get heuristic: " << cs);
        return std::make_shared<Result>(cs);
    }

    LOG4CPLUS_DEBUG(logger, "cublasLtMatmulAlgoGetHeuristic Executed with returnAlgoCount: "
        << returnAlgoCount);

    // Prepare the output buffer
    std::shared_ptr<Buffer> out = std::make_shared<Buffer>();
    out->Add<cublasLtMatmulHeuristicResult_t>(heuristicResultsArray, requestedAlgoCount);
    out->Add<int>(returnAlgoCount);

    return std::make_shared<Result>(cs, out);
}

CUBLAS_ROUTINE_HANDLER(LtMatmulDescCreate) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("LtMatmulDescCreate"));
    
    cublasLtMatmulDesc_t matmulDesc;
    cublasComputeType_t computeType = in->Get<cublasComputeType_t>();
    cudaDataType_t scaleType = in->Get<cudaDataType_t>();

    LOG4CPLUS_DEBUG(logger, "Creating LtMatmulDesc with computeType: "
        << computeType << ", scaleType: " << scaleType);
    
    cublasStatus_t cs = cublasLtMatmulDescCreate(&matmulDesc, computeType, scaleType);
    if (cs != CUBLAS_STATUS_SUCCESS) {
        LOG4CPLUS_ERROR(logger, "Failed to create LtMatmulDesc: " << cs);
        return std::make_shared<Result>(cs);
    }

    LOG4CPLUS_DEBUG(logger, "cublasLtMatmulDescCreate Executed");
    std::shared_ptr<Buffer> out = std::make_shared<Buffer>();
    out->Add<cublasLtMatmulDesc_t>(matmulDesc);
    return std::make_shared<Result>(cs, out);
}

CUBLAS_ROUTINE_HANDLER(LtMatmulDescDestroy) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("LtMatmulDescDestroy"));
    
    cublasLtMatmulDesc_t matmulDesc = in->Get<cublasLtMatmulDesc_t>();
    
    cublasStatus_t cs = cublasLtMatmulDescDestroy(matmulDesc);
    if (cs != CUBLAS_STATUS_SUCCESS) {
        LOG4CPLUS_ERROR(logger, "Failed to destroy LtMatmulDesc: " << cs);
    }

    LOG4CPLUS_DEBUG(logger, "cublasLtMatmulDescDestroy Executed");
    return std::make_shared<Result>(cs);
}

CUBLAS_ROUTINE_HANDLER(LtMatmulDescSetAttribute) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("LtMatmulDescSetAttribute"));

    cublasLtMatmulDesc_t matmulDesc = in->Get<cublasLtMatmulDesc_t>();
    cublasLtMatmulDescAttributes_t attr = in->Get<cublasLtMatmulDescAttributes_t>();
    size_t sizeInBytes = in->Get<size_t>();
    const void *buf = in->Assign<void>(sizeInBytes);

    cublasStatus_t cs = cublasLtMatmulDescSetAttribute(matmulDesc, attr, buf, sizeInBytes);
    if (cs != CUBLAS_STATUS_SUCCESS) {
        LOG4CPLUS_ERROR(logger, "Failed to set attribute on LtMatmulDesc: " << cs);
        return std::make_shared<Result>(cs);
    }

    LOG4CPLUS_DEBUG(logger, "cublasLtMatmulDescSetAttribute Executed");

    std::shared_ptr<Buffer> out = std::make_shared<Buffer>();
    out->Add<cublasLtMatmulDesc_t>(matmulDesc);
    return std::make_shared<Result>(cs, out);
}

CUBLAS_ROUTINE_HANDLER(LtMatrixLayoutCreate) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("cublasLtMatrixLayoutCreate"));

    cublasLtMatrixLayout_t matLayout;
    cudaDataType type = in->Get<cudaDataType>();
    uint64_t rows = in->Get<uint64_t>();
    uint64_t cols = in->Get<uint64_t>();
    int64_t ld = in->Get<int64_t>();

    LOG4CPLUS_DEBUG(logger, "Creating LtMatrixLayout with type: "
        << type << ", rows: " << rows << ", cols: " << cols << ", ld: " << ld);

    cublasStatus_t cs = cublasLtMatrixLayoutCreate(&matLayout, type, rows, cols, ld);
    if (cs != CUBLAS_STATUS_SUCCESS) {
        LOG4CPLUS_ERROR(logger, "Failed to create LtMatrixLayout: " << cs);
        return std::make_shared<Result>(cs);
    }

    LOG4CPLUS_DEBUG(logger, "cublasLtMatrixLayoutCreate Executed");

    std::shared_ptr<Buffer> out = std::make_shared<Buffer>();
    out->Add<cublasLtMatrixLayout_t>(matLayout);
    return std::make_shared<Result>(cs, out);
}

CUBLAS_ROUTINE_HANDLER(LtMatrixLayoutDestroy) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("cublasLtMatrixLayoutDestroy"));

    cublasLtMatrixLayout_t matLayout = in->Get<cublasLtMatrixLayout_t>();

    cublasStatus_t cs = cublasLtMatrixLayoutDestroy(matLayout);
    if (cs != CUBLAS_STATUS_SUCCESS) {
        LOG4CPLUS_ERROR(logger, "Failed to destroy LtMatrixLayout: " << cs);
        return std::make_shared<Result>(cs);
    }

    LOG4CPLUS_DEBUG(logger, "cublasLtMatrixLayoutDestroy Executed");
    return std::make_shared<Result>(cs);
}

CUBLAS_ROUTINE_HANDLER(LtMatmulPreferenceCreate) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("cublasLtMatmulPreferenceCreate"));

    cublasLtMatmulPreference_t preference;

    cublasStatus_t cs = cublasLtMatmulPreferenceCreate(&preference);
    if (cs != CUBLAS_STATUS_SUCCESS) {
        LOG4CPLUS_ERROR(logger, "Failed to create LtMatmulPreference: " << cs);
        return std::make_shared<Result>(cs);
    }

    LOG4CPLUS_DEBUG(logger, "cublasLtMatmulPreferenceCreate Executed");

    std::shared_ptr<Buffer> out = std::make_shared<Buffer>();
    out->Add<cublasLtMatmulPreference_t>(preference);
    return std::make_shared<Result>(cs, out);
}

CUBLAS_ROUTINE_HANDLER(LtMatmulPreferenceSetAttribute) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("cublasLtMatmulPreferenceSetAttribute"));

    cublasLtMatmulPreference_t preference = in->Get<cublasLtMatmulPreference_t>();
    cublasLtMatmulPreferenceAttributes_t attr = in->Get<cublasLtMatmulPreferenceAttributes_t>();
    size_t sizeInBytes = in->Get<size_t>();
    const void *buf = in->Assign<void>(sizeInBytes);

    cublasStatus_t cs = cublasLtMatmulPreferenceSetAttribute(preference, attr, buf, sizeInBytes);
    if (cs != CUBLAS_STATUS_SUCCESS) {
        LOG4CPLUS_ERROR(logger, "Failed to set attribute on LtMatmulPreference: " << cs);
        return std::make_shared<Result>(cs);
    }

    LOG4CPLUS_DEBUG(logger, "cublasLtMatmulPreferenceSetAttribute Executed");

    std::shared_ptr<Buffer> out = std::make_shared<Buffer>();
    out->Add<cublasLtMatmulPreference_t>(preference);
    return std::make_shared<Result>(cs, out);
}

CUBLAS_ROUTINE_HANDLER(LtMatmulPreferenceDestroy) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("cublasLtMatmulPreferenceDestroy"));

    cublasLtMatmulPreference_t preference = in->Get<cublasLtMatmulPreference_t>();

    cublasStatus_t cs = cublasLtMatmulPreferenceDestroy(preference);
    if (cs != CUBLAS_STATUS_SUCCESS) {
        LOG4CPLUS_ERROR(logger, "Failed to destroy LtMatmulPreference: " << cs);
        return std::make_shared<Result>(cs);
    }

    LOG4CPLUS_DEBUG(logger, "cublasLtMatmulPreferenceDestroy Executed");
    return std::make_shared<Result>(cs);
}

// TODO: now it only works only if alpha, beta are floats on host
// In reality, they can bei float, double or int on host or device
// This needs to be fixed in the future
CUBLAS_ROUTINE_HANDLER(LtMatmul) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("cublasLtMatmul"));

    cublasLtHandle_t lightHandle = in->Get<cublasLtHandle_t>();
    cublasLtMatmulDesc_t computeDesc = in->Get<cublasLtMatmulDesc_t>();
    const void *alpha = in->Assign<void>(sizeof(float));
    const void *A = in->GetFromMarshal<void*>();
    cublasLtMatrixLayout_t Adesc = in->Get<cublasLtMatrixLayout_t>();
    const void *B = in->GetFromMarshal<void*>();
    cublasLtMatrixLayout_t Bdesc = in->Get<cublasLtMatrixLayout_t>();
    const void *beta = in->Assign<void>(sizeof(float));
    const void *C = in->GetFromMarshal<void*>();
    cublasLtMatrixLayout_t Cdesc = in->Get<cublasLtMatrixLayout_t>();
    void *D = in->GetFromMarshal<void*>();
    cublasLtMatrixLayout_t Ddesc = in->Get<cublasLtMatrixLayout_t>();
    const cublasLtMatmulAlgo_t *algo = in->Assign<cublasLtMatmulAlgo_t>();
    void *workspace = in->GetFromMarshal<void*>();
    size_t workspaceSizeInBytes = in->Get<size_t>();
    cudaStream_t stream = in->Get<cudaStream_t>();

    LOG4CPLUS_DEBUG(logger, "Executing LtMatmul with lightHandle: "
        << lightHandle << ", computeDesc: " << computeDesc
        << ", alpha: " << *(float*)alpha << ", A: " << A << ", Adesc: " << Adesc
        << ", B: " << B << ", Bdesc: " << Bdesc << ", beta: " << *(float*)beta
        << ", C: " << C << ", Cdesc: " << Cdesc
        << ", D: " << D << ", Ddesc: " << Ddesc
        << ", algo: " << algo << ", workspace: " << workspace
        << ", workspaceSizeInBytes: " << workspaceSizeInBytes
        << ", stream: " << stream);

    cublasStatus_t cs = cublasLtMatmul(lightHandle, computeDesc, alpha, A, Adesc, B, Bdesc, beta, C, Cdesc, D, Ddesc, algo, workspace, workspaceSizeInBytes, stream);
    if (cs != CUBLAS_STATUS_SUCCESS) {
        LOG4CPLUS_ERROR(logger, "Failed to execute LtMatmul: " << cs);
        return std::make_shared<Result>(cs);
    }

    LOG4CPLUS_DEBUG(logger, "cublasLtMatmul Executed");

    return std::make_shared<Result>(cs);
}