/* GVirtuS - A Virtualization Framework for GPU-Accelerated Applications
 * Written by: Theodoros Aslanidis <theodoros.aslanidis@ucdconnect.ie>,
 *             School of Computer Science, University College Dublin
 */

 
#include "CublasHandler.h"

using gvirtus::communicators::Buffer;
using gvirtus::communicators::Result;

CUBLAS_ROUTINE_HANDLER(GemmEx) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("GemmEx"));

    cublasHandle_t handle = in->Get<cublasHandle_t>();
    cublasOperation_t transa = in->Get<cublasOperation_t>();
    cublasOperation_t transb = in->Get<cublasOperation_t>();
    int m = in->Get<int>();
    int n = in->Get<int>();
    int k = in->Get<int>();
    const void *alpha = in->Assign<const float>();
    const void *A = in->GetFromMarshal<const void*>();
    cudaDataType_t Atype = in->Get<cudaDataType_t>();
    int lda = in->Get<int>();
    const void *B = in->GetFromMarshal<const void*>();
    cudaDataType_t Btype = in->Get<cudaDataType_t>();
    int ldb = in->Get<int>();
    const void *beta = in->Assign<const float>();
    void *C = in->GetFromMarshal<void*>();
    cudaDataType_t Ctype = in->Get<cudaDataType_t>();
    int ldc = in->Get<int>();
    cublasComputeType_t computeType = in->Get<cublasComputeType_t>();
    cublasGemmAlgo_t algo = in->Get<cublasGemmAlgo_t>();

    cublasStatus_t cs = cublasGemmEx(handle, transa, transb, m, n, k, alpha, A, Atype, lda, B, Btype, ldb, beta, C, Ctype, ldc, computeType, algo);

    LOG4CPLUS_DEBUG(logger, "cublasGemmEx executed");
    return std::make_shared<Result>(cs);
}