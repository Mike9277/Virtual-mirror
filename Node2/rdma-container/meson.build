project(
    'rdma-container',
    'cpp',
    version: '1.0.0',
    default_options: ['cpp_std=c++20', 'warning_level=2'],
)

# Get doka dependency from subproject
doka_proj = subproject('doka')
doka_dep = doka_proj.get_variable('doka_dep')

# Get pybind11 dependency from subproject
pybind11_dep = dependency('pybind11', version: '>=2.0.0', required: true)
py = import('python').find_installation(pure: false)

# Source files
example_cpp_sources = files(
    'example.cpp',
    'rdma.cpp',
    'rdma.hpp',
)

module_sources = files(
    'rdma.hpp',
    'rdma.cpp',
    'pybind11_module.cpp',
)

# Build executable
executable(
    'example_cpp',
    example_cpp_sources,
    dependencies: [
        doka_dep,
    ],
    install: true,
)

py.extension_module('rdma',
    module_sources,
    install : true,
    dependencies : [pybind11_dep, doka_dep],
)
