#include "rdma.hpp"
#include <ibw/roce.hpp>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <stdexcept>

namespace py = pybind11;

namespace {

// No `py::array::forcecast`, because conversions will register the memory
// which is highly inefficient. Caller should ensure array is packed.
void wrap_send(RdmaSink &sink, py::array arr) {

    // Note: It does not work in pybind11 version 2.x when calling
    // `arr.nbytes()`, we need to use `arr.request()` to get the buffer.
    auto info = arr.request();

    if(!(arr.flags() & py::array::c_style)) {
        throw std::runtime_error("Array must be C-contiguous");
    }

    const auto tag = info.ptr;
    const auto data = info.ptr;
    const auto len = static_cast<size_t>(info.size) * info.itemsize;

    // Release GIL for blocking send operation
    py::gil_scoped_release release;
    sink.send(tag, data, len);
}

py::array_t<uint8_t> wrap_recv(RdmaSrc &src) {
    // Release GIL for blocking recv operation
    void *data;
    size_t size;
    {
        py::gil_scoped_release release;
        std::tie(data, size) = src.recv();
    }
    // GIL is automatically reacquired here

    // Create capsule with no-op deleter (buffer managed by RdmaSrc)
    auto capsule = py::capsule(data, [](void *) {
        // No-op: buffer is owned and reused by RdmaSrc
    });

    // Zero-copy: return view of internal buffer
    return py::array_t<uint8_t>(
        {static_cast<ssize_t>(size)},       // shape
        {sizeof(uint8_t)},                  // strides
        static_cast<const uint8_t *>(data), // data pointer
        capsule                             // base object
    );
}

// Find (device, port, gid_idx) from IPv4 address route
std::tuple<std::string, uint, uint> wrap_find_device(const std::string &ipv4) {
    const in_addr addr = ibw::parse_ipv4(ipv4.c_str());
    const auto [iface, local_ipv4] = ibw::find_iface_by_route(addr);

    const auto dev_addr_opt = ibw::find_rocev2_dev_from_ipv4(local_ipv4);
    if(!dev_addr_opt.has_value()) {
        throw std::runtime_error("Failed to find RDMA device for local IP");
    }

    const auto dev_addr = dev_addr_opt.value();
    return std::make_tuple(dev_addr.dev, dev_addr.port, dev_addr.gid_idx);
}

} // namespace

PYBIND11_MODULE(rdma, m) {
    m.doc() = "RDMA bindings for Python (Sender/Receiver-based)";

    // Device discovery function
    m.def("find_device", &wrap_find_device, py::arg("ipv4"),
          R"doc(
            Find RDMA device from local IPv4 address.
            
            Args:
                ipv4: Local IPv4 address (e.g., "192.168.1.10")
            
            Returns:
                tuple: (device_name, rdma_port, gid_index)
                       e.g., ("mlx5_0", 1, 3)
            
            Example:
                dev, port, gid_idx = rdma.find_device("192.168.1.10")
          )doc");

    py::class_<RdmaArgs>(m, "RdmaArgs", "RDMA configuration arguments")
        .def(py::init<>())
        .def_readwrite("dev", &RdmaArgs::dev,
                       "RDMA device name (e.g. 'mlx5_0')")
        .def_readwrite("ip", &RdmaArgs::ip, "Server IP address")
        .def_readwrite("port", &RdmaArgs::port, "Server port")
        .def_readwrite("gid_idx", &RdmaArgs::gid_idx, "RDMA GID index")
        .def_readwrite("is_client", &RdmaArgs::is_client,
                       "True for client, False for server")
        .def_readwrite("max_msg_bytes", &RdmaArgs::max_msg_bytes,
                       "Maximum message size in bytes");

    py::class_<RdmaSrc>(m, "RdmaSrc", R"doc(
        RDMA receiver (zero-copy).
        
        WARNING: recv() returns a zero-copy view of an internal buffer that is
        REUSED on the next recv() call. You MUST process or copy the data before
        calling recv() again, or the data will be corrupted.
        
        Example:
            src = RdmaSrc(args)
            
            # Safe: use data immediately
            data = src.recv()
            process(data)
            
            # Safe: explicit copy if you need to keep data
            data = src.recv()
            saved = data.copy()
            data2 = src.recv()  # Now safe to call
    )doc")
        .def(py::init<const RdmaArgs &>())
        .def("recv", &wrap_recv,
             R"doc(
                Receive data from RDMA (blocking, zero-copy).
                
                Returns:
                    numpy.ndarray: Zero-copy view of received data (uint8).
                                   INVALIDATED on next recv() call!
             )doc");

    py::class_<RdmaSink>(m, "RdmaSink", "RDMA sender")
        .def(py::init<const RdmaArgs &>())
        .def("send", &wrap_send, py::arg("data"),
             R"doc(
                Send data via RDMA (blocking).
                
                Args:
                    data: C-contiguous numpy array of any dtype
             )doc");
}