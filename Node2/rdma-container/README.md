# rdma-container

## Introduction

Implementation of RDMA sender and receiver for NVIDIA DOCA.
Compatible with ConnectX network cards and BlueField DPUs.

- Leverages NVIDIA DOCA SDK.
- Assumes RoCEv2.

## Building

### Prerequisites

- NVIDIA DOCA SDK (tested with DOCA 3.1.0)
- Meson build system
- C++20 compatible compiler
- NVIDIA ConnectX network card or BlueField DPU

### Standard Build

```bash
# Setup the build directory
meson setup builddir

# Compile
meson compile -C builddir

# The binary will be at builddir/rdma-container
```

### Docker Build

Build using the provided Dockerfile which uses the NVIDIA DOCA 3.1.0 development image. The Dockerfile automatically builds the application inside the container:

```bash
# Build the container (includes compiling the application)
docker build -t rdma-container .

# Run as server with default IP (192.168.200.13:5000)
# Option 1: Minimal secure approach (recommended)
docker run --rm \
    --network host \
    --cap-add=IPC_LOCK \
    --device /dev/infiniband/uverbs0 \
    --device /dev/infiniband/rdma_cm \
    rdma-container

# Option 2: With --privileged (simpler but less secure)
docker run --rm \
    --privileged \
    --network host \
    rdma-container

# Run as server with custom IP
docker run --rm \
    --network host \
    --cap-add=IPC_LOCK \
    --device /dev/infiniband/uverbs0 \
    --device /dev/infiniband/rdma_cm \
    rdma-container \
    ./builddir/rdma-container --server 192.168.1.100:5000

# Run as client
docker run --rm \
    --network host \
    --cap-add=IPC_LOCK \
    --device /dev/infiniband/uverbs0 \
    --device /dev/infiniband/rdma_cm \
    rdma-container \
    ./builddir/rdma-container --client 192.168.200.13:5000
```

**Important**: RDMA in containers requires:
- `--cap-add=IPC_LOCK` for memory pinning (allows unlimited memory locking, bypassing ulimits)
- `--network host` for direct network access
- `--device /dev/infiniband/*` for InfiniBand device access

**Note**: `--privileged` works but is less secure - it grants all capabilities. The recommended approach uses only the specific capability and devices needed. The `--ulimit memlock=-1:-1` flag is not needed because `CAP_IPC_LOCK` bypasses the memory lock limit entirely.

## How it works

This is a pair of sender/receiver.
- The class `RdmaSink` can **send** data (via `send()` method).
- The class `RdmaSrc` can **receive** data (via `recv()` method).

To have a full duplex connection, just create both instances on both endpoints.

The connection is bootstrapped with TCP. By default, the network interface used for the TCP bootstrapping is the same device that is used for the RoCEv2 RDMA connection. Do not use an out-of-band IP, otherwise the RDMA device will not be detected.


## How to use

A simple API is exposed:

- A single method `RdmaSink::send()` to send data.
- A single method `RdmaSrc::recv()` to receive data.

## Example: `main.cpp`

The example demonstrates a simple RDMA client-server application:

### Features

- **Automatic device discovery**: Uses `ibw::find_iface_by_route()` and `ibw::find_rocev2_dev_from_ipv4()` to automatically detect the appropriate RDMA device based on the destination IP address.

- **Command-line interface**: Uses `argparse` for easy configuration:
  - `-c/--client`: Run as client (sender)
  - `-s/--server`: Run as server (receiver)
  - `address`: Server address in `IP:port` format

### Usage

**Start the server (receiver):**
```bash
./rdma-container --server 192.168.1.100:5000
```

**Start the client (sender):**
```bash
./rdma-container --client 192.168.1.100:5000
```

The client will send 10,000 messages (strings "0" through "9999") to the server, which will receive and log each message. The server automatically detects end-of-stream when the client disconnects.

## Notes

To know:

- Calling `send()` or `recv()` is blocking. The function will not return until the peer endpoint matches the operation. 
- Each time you call `send()` with a different buffer, a costly memory registration is done. To avoid this, always call it with the same buffer (and keep the count of buffers small).
- The received buffer is valid until the next call to `recv()` is done.
- The sent buffer can be modified immediately after being sent.
- The maximum message size should be known, because the buffer should be preallocated on the receiving side.
- By default, there is a buffering of two messages (`RdmaSrc::m_peer_maxcredits = 2`). Meaning one message can be sent while the other one is being processed.