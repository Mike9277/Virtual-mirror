#include "rdma.hpp"
#include <arpa/inet.h>
#include <cstdlib>
#include <cstring>
#include <ibw/error.hpp>
#include <ibw/roce.hpp>
#include <ibw/utility/argparse.hpp>
#include <spdlog/spdlog.h>
#include <string>

int main(int argc, char *argv[]) {
    spdlog::set_level(spdlog::level::info);

    // Setup argument parser
    argparse::ArgumentParser program("rdma-container");

    program.add_argument("-c", "--client").help("run as client").flag();

    program.add_argument("-s", "--server").help("run as server").flag();

    program.add_argument("address").help("server address in format IP:port");

    try {
        program.parse_args(argc, argv);
    } catch(const std::exception &err) {
        spdlog::error("Argument parsing error: {}", err.what());
        std::cerr << program;
        return EXIT_FAILURE;
    }

    // Check that exactly one mode is specified
    bool is_client = program.get<bool>("--client");
    bool is_server = program.get<bool>("--server");

    if(is_client == is_server) {
        spdlog::error("Must specify exactly one of --client or --server");
        std::cerr << program;
        return EXIT_FAILURE;
    }

    // Parse address
    std::string address_str = program.get<std::string>("address");
    std::string ip;
    uint16_t port;
    try {
        std::tie(ip, port) = ibw::parse_ip_port(address_str, 5000);
    } catch(const std::exception &err) {
        spdlog::error("Failed to parse address: {}", err.what());
        return EXIT_FAILURE;
    }

    spdlog::info("Address: {}:{}", ip, port);

    // Get device from route
    in_addr server_ipv4 = ibw::parse_ipv4(ip.c_str());

    const auto [iface, local_ipv4] = ibw::find_iface_by_route(server_ipv4);

    char local_ipv4_str[INET_ADDRSTRLEN];
    if(inet_ntop(AF_INET, &local_ipv4, local_ipv4_str,
                 sizeof(local_ipv4_str)) == nullptr) {
        spdlog::error("Failed to convert local IP to string");
        return EXIT_FAILURE;
    }

    spdlog::info("Interface: {}", iface);
    spdlog::info("Local IP: {}", local_ipv4_str);

    const auto dev_addr_opt = ibw::find_rocev2_dev_from_ipv4(local_ipv4);
    if(!dev_addr_opt.has_value()) {
        spdlog::error("Failed to find RDMA device for local IP");
        return EXIT_FAILURE;
    }

    const auto dev_addr = dev_addr_opt.value();
    spdlog::info("RDMA device: (dev={}, port={}, gid={})", dev_addr.dev,
                 dev_addr.port, dev_addr.gid_idx);

    // Setup RDMA arguments
    RdmaArgs args{};
    args.dev = dev_addr.dev;
    args.ip = ip;
    args.port = port;
    args.gid_idx = dev_addr.gid_idx;
    args.is_client = is_client;
    args.max_msg_bytes = 10 * 1024 * 1024; // 10 MiB per message

    try {
        if(is_server) {
            spdlog::info("Running as server");
            RdmaSrc rdma_src(args);

            // Receive messages and print them
            size_t count = 0;
            while(true) {
                auto [data, size] = rdma_src.recv();
                if(size == 0) {
                    spdlog::info("Received end-of-stream signal");
                    break;
                }

                std::string message(static_cast<const char *>(data), size);
                spdlog::info("Received message #{}: {}", count++, message);
            }

        } else {
            spdlog::info("Running as client");
            RdmaSink rdma_sink(args);

            // Send 10000 messages
            const size_t num_messages = 10000;
            for(size_t i = 0; i < num_messages; i++) {
                std::string message = std::to_string(i);
                spdlog::info("Sending message #{}: {}", i, message);

                // Use message string itself as the tag since we're sending from
                // the start of the buffer
                rdma_sink.send(message.c_str(), message.c_str(),
                               message.size());
            }

            spdlog::info("Successfully sent {} messages", num_messages);
        }

    } catch(const std::exception &err) {
        spdlog::error("RDMA error: {}", err.what());
        return EXIT_FAILURE;
    }

    spdlog::info("Done");
    return EXIT_SUCCESS;
}
