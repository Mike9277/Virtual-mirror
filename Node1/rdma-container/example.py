#!/usr/bin/env python3
"""
RDMA Example using Python bindings

This example demonstrates how to use the RDMA Python module for
high-performance zero-copy data transfer between client and server.

The connection uses TCP for initial handshake, then switches to RDMA.
- address: Server IP and TCP port for handshake (IP:TCP_PORT)
- RDMA device is automatically discovered from the server IP's network route

Usage:
    # Server (receiver) - listens on 192.168.1.100:5555
    python3 example.py --server 192.168.1.100:5555

    # Client (sender) - connects to server at 192.168.1.100:5555
    python3 example.py --client 192.168.1.100:5555
"""

import sys
import argparse
from pathlib import Path
import numpy as np
import time

# Add build directory to Python path
# In production you would want to update PYTHONPATH
build_dir = Path(__file__).parent / 'builddir-release'
sys.path.insert(0, str(build_dir))

try:
    import rdma
except ImportError as e:
    print(f"Error: Could not import rdma module from {build_dir}")
    print(f"Make sure you've built the project with: meson compile -C builddir-release")
    print(f"Import error: {e}")
    sys.exit(1)


def parse_address(tcp_addr_port: str) -> tuple[str, int]:
    """Parse address string in format IP:TCP_PORT"""
    parts = tcp_addr_port.split(':')
    if len(parts) != 2:
        raise ValueError("Address must be in format IP:TCP_PORT")
    
    ip = parts[0]
    tcp_port = int(parts[1])
    
    return ip, tcp_port


def run_server(ip, tcp_port):
    """Run RDMA server (receiver)"""
    print(f"Starting RDMA server")
    print(f"TCP handshake: {ip}:{tcp_port}")
    
    # Discover RDMA device from local IP
    dev, rdma_port, gid_idx = rdma.find_device(ip)
    print(f"Found RDMA device: {dev}, port: {rdma_port}, GID index: {gid_idx}")
    
    # Configure RDMA arguments
    args = rdma.RdmaArgs()
    args.dev = dev                          # RDMA device name (e.g., "mlx5_0")
    args.ip = ip                            # Server IP for TCP handshake
    args.port = tcp_port                    # TCP port for connection setup
    args.gid_idx = gid_idx                  # RDMA GID index (from find_device)
    args.is_client = False                  # Server mode
    args.max_msg_bytes = 10 * 1024 * 1024  # 10 MiB max message size
    
    # Create receiver
    print("Creating RdmaSrc...")
    src = rdma.RdmaSrc(args)
    print("Server ready, waiting for messages...")
    
    count = 0
    total_bytes = 0
    start_time = time.time()
    
    try:
        while True:
            # Receive data (zero-copy, blocks until data arrives)
            data = src.recv()
            
            # Check for end-of-stream (size = 0)
            if len(data) == 0:
                print("\nReceived end-of-stream signal")
                break
            
            total_bytes += len(data)
            
            # Process data immediately (it's a numpy array of uint8)
            # If you need to keep it, make a copy: saved = data.copy()
            
            # Try to decode as string for display
            try:
                message = bytes(data).decode('utf-8')
                print(f"Message #{count}: '{message}' ({len(data)} bytes)")
            except UnicodeDecodeError:
                print(f"Message #{count}: <binary data> ({len(data)} bytes)")
            
            count += 1
            
            # Example: show some stats every 1000 messages
            if count % 1000 == 0:
                elapsed = time.time() - start_time
                throughput_mbps = (total_bytes * 8) / (elapsed * 1_000_000)
                msg_rate = count / elapsed
                print(f"Stats: {count} messages, {total_bytes:,} bytes, "
                      f"{throughput_mbps:.2f} Mbps, {msg_rate:.2f} msg/s")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        raise
    
    elapsed = time.time() - start_time
    print(f"\nReceived {count} messages, {total_bytes:,} bytes in {elapsed:.2f}s")
    if elapsed > 0:
        print(f"Average throughput: {(total_bytes * 8) / (elapsed * 1_000_000):.2f} Mbps")
        print(f"Average message rate: {count / elapsed:.2f} msg/s")


def run_client(ip, tcp_port, num_messages=10000):
    """Run RDMA client (sender)"""
    print(f"Starting RDMA client")
    print(f"Connecting to: {ip}:{tcp_port}")
    
    # Discover RDMA device from local IP
    dev, rdma_port, gid_idx = rdma.find_device(ip)
    print(f"Found RDMA device: {dev}, port: {rdma_port}, GID index: {gid_idx}")
    
    # Configure RDMA arguments
    args = rdma.RdmaArgs()
    args.dev = dev                          # RDMA device name (e.g., "mlx5_0")
    args.ip = ip                            # Server IP for TCP handshake
    args.port = tcp_port                    # TCP port for connection setup
    args.gid_idx = gid_idx                  # RDMA GID index (from find_device)
    args.is_client = True                   # Client mode
    args.max_msg_bytes = 10 * 1024 * 1024  # 10 MiB max message size
    
    # Create sender
    print("Creating RdmaSink...")
    sink = rdma.RdmaSink(args)
    print(f"Connected! Sending {num_messages} messages...")
    
    total_bytes = 0
    start_time = time.time()
    
    try:
        for i in range(num_messages):
            # Create message as string
            message = f"Message number {i}"
            
            # Convert to numpy array (must be C-contiguous)
            # Option 1: From string/bytes
            data = np.frombuffer(message.encode('utf-8'), dtype=np.uint8)
            
            # Option 2: Send arbitrary numpy arrays
            # data = np.array([i, i+1, i+2], dtype=np.float32)
            
            # Ensure C-contiguous (should already be, but safe to check)
            if not data.flags['C_CONTIGUOUS']:
                data = np.ascontiguousarray(data)
            
            # Send data
            sink.send(data)
            total_bytes += len(data)
            
            if (i + 1) % 1000 == 0:
                elapsed = time.time() - start_time
                throughput_mbps = (total_bytes * 8) / (elapsed * 1_000_000)
                msg_rate = (i + 1) / elapsed
                print(f"Sent {i + 1}/{num_messages} messages, "
                      f"{throughput_mbps:.2f} Mbps, {msg_rate:.2f} msg/s")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        raise
    
    elapsed = time.time() - start_time
    print(f"\nSent {num_messages} messages, {total_bytes:,} bytes in {elapsed:.2f}s")
    if elapsed > 0:
        print(f"Average throughput: {(total_bytes * 8) / (elapsed * 1_000_000):.2f} Mbps")
        print(f"Average message rate: {num_messages / elapsed:.2f} msg/s")


def example_numpy_arrays():
    """Example: Sending different types of numpy arrays"""
    print("\nExample: Different numpy array types")
    print("=" * 50)
    
    # All these arrays can be sent (must be C-contiguous):
    
    # 1. Simple array
    arr1 = np.array([1, 2, 3, 4, 5], dtype=np.int32)
    print(f"int32 array: {arr1.nbytes} bytes")
    
    # 2. Float array
    arr2 = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    print(f"float64 array: {arr2.nbytes} bytes")
    
    # 3. Multi-dimensional array (C-contiguous by default)
    arr3 = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.uint8)
    print(f"2D uint8 array: {arr3.shape}, {arr3.nbytes} bytes")
    
    # 4. Large buffer
    arr4 = np.zeros(1024*1024, dtype=np.uint8)  # 1 MiB
    print(f"1 MiB buffer: {arr4.nbytes} bytes")
    
    # 5. From bytes
    arr5 = np.frombuffer(b"Hello RDMA!", dtype=np.uint8)
    print(f"From bytes: {arr5.nbytes} bytes")
    
    print("\nAll these can be sent via: sink.send(array)")
    print("Receiver gets: data = src.recv()  # numpy array of uint8")


def main():
    parser = argparse.ArgumentParser(
        description='RDMA Example - High-performance data transfer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--server', action='store_true',
                           help='Run as server (receiver)')
    mode_group.add_argument('--client', action='store_true',
                           help='Run as client (sender)')
    mode_group.add_argument('--example', action='store_true',
                           help='Show numpy array examples')
    
    parser.add_argument('address', nargs='?',
                       help='Server address in format IP:TCP_PORT (e.g., 192.168.1.100:5555)')
    parser.add_argument('-n', '--num-messages', type=int, default=10000,
                       help='Number of messages to send (client only, default: 10000)')
    
    args = parser.parse_args()
    
    # Show examples
    if args.example:
        example_numpy_arrays()
        return 0
    
    # Parse address
    if not args.address:
        parser.error("address is required for --server or --client")
    
    try:
        ip, tcp_port = parse_address(args.address)
    except ValueError as e:
        parser.error(f"Invalid address format: {e}")
    
    # Run in appropriate mode
    try:
        if args.server:
            run_server(ip, tcp_port)
        else:  # client
            run_client(ip, tcp_port, args.num_messages)
        
        return 0
    
    except Exception as e:
        print(f"\nFatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

