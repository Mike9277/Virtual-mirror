#pragma once

#include <doca_dma.h>
#include <doka/core/dev.hpp>
#include <doka/core/pe.hpp>
#include <doka/mem/buf_inventory.hpp>
#include <doka/mem/mmap.hpp>
#include <doka/nocm/nocm.hpp>
#include <doka/rdma/recv_callbacks.hpp>
#include <doka/rdma/send_callbacks.hpp>
#include <ibw/utility/socket.hpp>
#include <ibw/utility/tcp.hpp>
#include <unordered_map>

struct RdmaArgs {
    std::string dev;   ///< Which RDMA device, eg. 'mlx5_0'.
    std::string ip;    ///< Server IP.
    uint16_t port{};   ///< Server listening port.
    uint8_t gid_idx{}; ///< <RDMA GID>, used for RDMA communication.
    bool is_client{}; ///< If true, acts as a client and tries to connect to the
                      ///< server. Otherwise, acts as a server.
    size_t max_msg_bytes{}; ///< Maximum message size in bytes.
};

struct RdmaSlot {
    void *data{};  ///< Pointer to data buffer.
    size_t size{}; ///< Size of the buffer in bytes.
};

class RdmaSrc final : public doka::rdma_send_callbacks,
                      public doka::rdma_recv_callbacks {
public:
    RdmaSrc(const RdmaArgs &args);

    /// @note Blocking.
    /// @return Pointer to data received, count of bytes received.
    ///         The pointer to the data is always one of the slot.
    std::pair<void *, size_t> recv();

private:
    struct Slot {
        doka::mmap mmap;
        doca_buf *recv_buf{};

        // Size of the message just received, if any.
        size_t recv_size;

        // Task to receive the data.
        doca_rdma_task_receive *recv_task;

        // Task to replenish one credit.
        doca_rdma_task_send *send_task;
    };

    void on_send_completed(doca_rdma_task_send *task, doca_data task_user_data,
                           doca_data ctx_user_data) override;
    void on_send_error(doca_rdma_task_send *task, doca_data task_user_data,
                       doca_data ctx_user_data) override;
    void on_recv_completed(doca_rdma_task_receive *task,
                           doca_data task_user_data,
                           doca_data ctx_user_data) override;
    void on_recv_error(doca_rdma_task_receive *task, doca_data task_user_data,
                       doca_data ctx_user_data) override;

    // ---- RDMA Connection.

    doka::dev m_dev;
    doka::nocm m_cm;
    ibw::fd m_tcp;

    // Max credits of the peer rdmasink.
    size_t m_peer_maxcredits{};

    // Count of polled Recvs.
    size_t m_recv_count{};

    // Pool for send tasks.
    std::vector<doca_rdma_task_send *> m_send_task_pool;

    // ---- Data buffers.

    // One slot per credit.
    std::vector<Slot> m_slots;
    doka::buf_inventory m_inv;

    doka::pe_notif m_pe_notif;

    bool m_error{};
};

class RdmaSink final : public doka::rdma_send_callbacks,
                       public doka::rdma_recv_callbacks {
public:
    RdmaSink(const RdmaArgs &args);
    ~RdmaSink();

    /// @note Blocking.
    /// @param tag A unique identifier for the buffer. When sending from the
    /// start of the buffer, `tag == data`.
    void send(const void *tag, const void *data, size_t size);

private:
    struct PinnedMem {
        void *data;
        size_t size;
        doka::mmap mmap;
    };

    struct SendInfo {
        doca_buf *buf;
        doca_rdma_task_send *task;
    };

    void on_send_completed(doca_rdma_task_send *task, doca_data task_user_data,
                           doca_data ctx_user_data) override;
    void on_send_error(doca_rdma_task_send *task, doca_data task_user_data,
                       doca_data ctx_user_data) override;
    void on_recv_completed(doca_rdma_task_receive *task,
                           doca_data task_user_data,
                           doca_data ctx_user_data) override;
    void on_recv_error(doca_rdma_task_receive *task, doca_data task_user_data,
                       doca_data ctx_user_data) override;

    SendInfo push_one_send(const PinnedMem &pin, const void *const data,
                           const size_t size);

    /// Register or re-register pinned memory.
    const PinnedMem &ensure_mem_registered(const void *tag, void *data,
                                           size_t size);
    const PinnedMem &register_mem(const void *tag, void *data, size_t size);

    // ---- RDMA Connection.

    doka::dev m_dev;
    doka::nocm m_cm;
    ibw::fd m_tcp;

    /// Each frame sent consumes one credit, each ACK restores one.
    size_t m_maxcredits{};
    size_t m_credits{};

    /// ---- Pinned memory buffers.

    /// Key: Memory buffer tag/identifier.
    std::unordered_map<const void *, PinnedMem> m_memcache;

    // ---- In-flight buffers.

    doka::buf_inventory m_inv;
    doka::pe_notif m_pe_notif;

    std::vector<doca_rdma_task_receive *> m_recv_tasks{};

    /// Total count of messages succesfully sent.
    size_t m_send_count{};
};