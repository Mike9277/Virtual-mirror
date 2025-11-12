project(gvirtus-plugin-curand)
find_package(CUDAToolkit REQUIRED)

include_directories(${CUDAToolkit_INCLUDE_DIRS})

resolve_cuda_library_version(curand CURAND_VERSION)

gvirtus_add_backend(curand ${CURAND_VERSION}
    backend/CurandHandler.cpp
    backend/CurandHandler_host.cpp
)

target_link_libraries(${PROJECT_NAME}
    CUDA::curand
)

gvirtus_add_frontend(curand ${CURAND_VERSION}
    frontend/Curand.cpp
    frontend/CurandFrontend.cpp)
