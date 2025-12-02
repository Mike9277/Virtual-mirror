#include "rdma.hpp"
#include <cassert>
#include <cstddef>
#include <doca_pe.h>
#include <doka/core/error.hpp>
#include <doka/mem/buf_inventory.hpp>
#include <doka/nocm/nocm.hpp>
#include <ibw/utility/int.hpp>
#include <ibw/utility/tcp.hpp>
#include <spdlog/spdlog.h>

static ibw::fd rdma_connect_tcp(const RdmaArgs &args) {

    ibw::fd ret;

    if(args.is_client) {
        ret = ibw::tcp::connect(args.ip.c_str(), args.port);
    } else {
        const ibw::fd tcp_server = ibw::tcp::listen(args.ip.c_str(), args.port);
        ret = ibw::tcp::accept(tcp_server.get());

        // TCP server is destroyed here, but p2p connection to client is kept.
        // We don't care to listen to new clients.
    }

    return ret;
}

//
// ------------- RdmaSink
//

RdmaSink::RdmaSink(const RdmaArgs &args)
    : m_dev(doka::dev::open(args.dev.c_str())), m_cm(m_dev.get()),
      m_tcp(rdma_connect_tcp(args)), m_pe_notif(m_cm.pe().get()) {
    // TCP protocol:
    // - rdmasrc sends to rdmasink max credits as uint64_t.

    m_maxcredits = ibw::recv_full<uint64_t>(m_tcp.get());
    m_credits = m_maxcredits;
    m_recv_tasks.resize(m_maxcredits);

    DOKA_CHECK(doca_rdma_set_gid_index(m_cm.rdma(), args.gid_idx));

    m_cm.set_user_data(this);
    bind_rdma_send_callbacks_type<RdmaSink>(m_cm.rdma(), 1);
    bind_rdma_recv_callbacks_type<RdmaSink>(m_cm.rdma(), m_maxcredits);

    m_cm.connect(m_tcp.get());

    m_inv = doka::buf_inventory(1);
    m_inv.start();

    // Fill all RDMA Recvs.

    for(size_t i = 0; i < m_maxcredits; i++) {
        auto &recv_task = m_recv_tasks[i];
        DOKA_CHECK(doca_rdma_task_receive_allocate_init(m_cm.rdma(), nullptr,
                                                        {}, &recv_task));
        DOKA_CHECK(doca_task_submit(doca_rdma_task_receive_as_task(recv_task)));
    }
}

static int eos_tag = 0;

RdmaSink::~RdmaSink() {
    ensure_mem_registered(&eos_tag, &eos_tag, sizeof(eos_tag));
    send(&eos_tag, &eos_tag, 0);
}

auto RdmaSink::register_mem(const void *tag, void *data,
                            size_t size) -> const PinnedMem & {
    // Register the memory to be pinned for RDMA.
    // Should not be already in the cache.

    spdlog::info("register_mem(tag={}, data={}, size={})", fmt::ptr(tag),
                 fmt::ptr(data), size);

    doca_mmap *mmap = {};

    assert(m_memcache.find(tag) == m_memcache.end());

    DOKA_CHECK(doca_mmap_create(&mmap));
    DOKA_CHECK(doca_mmap_add_dev(mmap, m_dev));
    DOKA_CHECK(
        doca_mmap_set_permissions(mmap, DOCA_ACCESS_FLAG_LOCAL_READ_WRITE));
    DOKA_CHECK(doca_mmap_set_memrange(mmap, data, size));

    PinnedMem pin;
    pin.data = data;
    pin.size = size;
    pin.mmap = doka::mmap(mmap, m_dev);

    pin.mmap.start();
    m_memcache[tag] = std::move(pin);
    return m_memcache[tag];
}

auto RdmaSink::ensure_mem_registered(const void *tag, void *data,
                                     size_t size) -> const PinnedMem & {
    // Register memory if tag does not exist.
    // Otherwise, ensure [data; data + size] is in range of registration.

    const auto it = m_memcache.find(tag);
    if(it == m_memcache.end()) {
        return register_mem(tag, data, size);
    }

    PinnedMem &pin = it->second;
    const uint64_t cur_start = ibw::as_u64(pin.data);
    const uint64_t cur_end = cur_start + pin.size;

    const uint64_t req_start = ibw::as_u64(data);
    const uint64_t req_end = req_start + size;

    const bool in_range = (cur_start <= req_start && cur_end >= req_end);

    if(in_range) {
        return pin;
    }

    spdlog::info("Extending registered memory");

    const uint64_t next_start = std::min(cur_start, req_start);
    const uint64_t next_end = std::max(cur_end, req_end);

    // TODO Maybe possible to re-register for better perf, but anyway this
    // should not happen often.
    m_memcache.erase(tag);

    return register_mem(tag, ibw::as_ptr(next_start), next_end - next_start);
}

void RdmaSink::on_send_completed(doca_rdma_task_send *const send_task,
                                 const doca_data task_user_data,
                                 const doca_data ctx_user_data) {
    // Triggered when ACK is received (but credit is not replenished yet).
    // Don't free the task and buffer here, we do it after polling (easier, we
    // have reference to `pin`).

    m_send_count++;
}

void RdmaSink::on_send_error(doca_rdma_task_send *const task,
                             const doca_data task_user_data,
                             const doca_data ctx_user_data) {
    spdlog::error("ERROR: send error");
    std::exit(1);
}

void RdmaSink::on_recv_completed(doca_rdma_task_receive *task,
                                 doca_data task_user_data,
                                 doca_data ctx_user_data) {
    // The only reason to have a receive completion is
    // to notify credits have been replenished by one.
    // Not real data is received.
    // Also resubmit receive task here.

    assert(m_credits < m_maxcredits);

    m_credits++;
    doca_task_submit(doca_rdma_task_receive_as_task(task));
}

void RdmaSink::on_recv_error(doca_rdma_task_receive *task,
                             doca_data task_user_data,
                             doca_data ctx_user_data) {
    spdlog::error("ERROR: recv error");
    std::exit(1);
}

void RdmaSink::send(const void *tag, const void *const data,
                    const size_t size) {
    spdlog::info("Going to send {} bytes", size);
    spdlog::info("cache_size={}", m_memcache.size());

    // TODO without const_cast? But doca memrange needs non-const anyway.
    const PinnedMem &pin =
        ensure_mem_registered(tag, const_cast<void *>(data), size);

    // Blocks until we have at least one credit.
    // We never poll more than one credit,
    // even if there are multiple completion in the queue,
    // because there is no need to flush the queue,
    // and the queue cannot be overflowed.
    while(m_credits == 0) {
        if(doca_pe_progress(m_cm.pe().get()) == 0) {
            m_pe_notif.wait();
        }
    }

    // Sends data and waits ACK, so that buffer can be used freely afterwards.
    // We also may replenish credits in this polling loop: it's ok.
    const SendInfo info = push_one_send(pin, data, size);
    const uint64_t target_count = m_send_count + 1;
    while(m_send_count != target_count) {
        if(doca_pe_progress(m_cm.pe().get()) == 0) {
            m_pe_notif.wait();
        }
    }

    // Free the task and the buf allocated in the previous lines.
    DOKA_CHECK(doca_buf_dec_refcount(info.buf, nullptr));
    doca_task_free(doca_rdma_task_send_as_task(info.task));
}

auto RdmaSink::push_one_send(const PinnedMem &pin, const void *const data,
                             const size_t size) -> SendInfo {
    // There should be only one in-flight task at a time (either no task sent
    // yet, or completion is polled).

    SendInfo ret;
    assert(m_credits > 0);

    // Consume one credit to send the data in the next lines.
    m_credits--;

    // const_cast: for an unknown reason, data is not taken by const pointer.
    DOKA_CHECK(doca_buf_inventory_buf_get_by_data(
        m_inv, pin.mmap, const_cast<void *>(data), size, &ret.buf));
    DOKA_CHECK(doca_rdma_task_send_allocate_init(m_cm.rdma(), m_cm.connection(),
                                                 ret.buf, {}, &ret.task));
    DOKA_CHECK(doca_task_submit(doca_rdma_task_send_as_task(ret.task)));

    return ret;
}

//
// ------------- RdmaSrc
//

RdmaSrc::RdmaSrc(const RdmaArgs &args)
    : m_dev(doka::dev::open(args.dev.c_str())), m_cm(m_dev.get()),
      m_tcp(rdma_connect_tcp(args)), m_pe_notif(m_cm.pe().get()) {
    DOKA_CHECK(doca_rdma_set_gid_index(m_cm.rdma(), args.gid_idx));
    m_cm.set_user_data(this);

    m_peer_maxcredits = 2;

    bind_rdma_recv_callbacks_type<RdmaSrc>(m_cm.rdma(), m_peer_maxcredits);

    // We don't poll completion immediately when replenishing credits.
    // In practice, one should suffice, but technically we never check it,
    // so in unbelieavable latency scenario we could need it.
    bind_rdma_send_callbacks_type<RdmaSrc>(m_cm.rdma(), m_peer_maxcredits);

    ibw::send_full(m_tcp.get(), static_cast<uint64_t>(m_peer_maxcredits));
    m_cm.connect(m_tcp.get());

    m_inv = doka::buf_inventory(m_peer_maxcredits);
    m_inv.start();

    // Push receive tasks before syncing with the peer.
    for(size_t i = 0; i < m_peer_maxcredits; i++) {
        Slot slot = {};
        slot.mmap = doka::mmap::create_host(m_dev, args.max_msg_bytes);

        DOKA_CHECK(doca_buf_inventory_buf_get_by_addr(
            m_inv.get(), slot.mmap, slot.mmap.host_data(), slot.mmap.size(),
            &slot.recv_buf));

        slot.mmap.start();

        DOKA_CHECK(doca_rdma_task_receive_allocate_init(
            m_cm.rdma(), slot.recv_buf, {}, &slot.recv_task));
        DOKA_CHECK(
            doca_task_submit(doca_rdma_task_receive_as_task(slot.recv_task)));

        m_slots.push_back(std::move(slot));
    }

    // Fill the send task pool.
    for(size_t i = 0; i < m_peer_maxcredits; i++) {
        doca_rdma_task_send *task = {};
        DOKA_CHECK(doca_rdma_task_send_allocate_init(
            m_cm.rdma(), m_cm.connection(), nullptr, {}, &task));
        m_send_task_pool.push_back(task);
    }
}

void RdmaSrc::on_send_completed(doca_rdma_task_send *const send_task,
                                const doca_data task_user_data,
                                const doca_data ctx_user_data) {
    // Nothing to do, we just replenished one credit to the peer,
    // allowing him to send more frames.

    m_send_task_pool.push_back(send_task);
}

void RdmaSrc::on_send_error(doca_rdma_task_send *const task,
                            const doca_data task_user_data,
                            const doca_data ctx_user_data) {
    spdlog::error("ERROR: send error");
    std::exit(1);
}

void RdmaSrc::on_recv_completed(doca_rdma_task_receive *const recv_task,
                                const doca_data task_user_data,
                                const doca_data ctx_user_data) {
    const size_t slot_id = (m_recv_count % m_slots.size());
    Slot &slot = m_slots.at(slot_id);
    assert(recv_task == slot.recv_task);
    m_recv_count++;

    DOKA_CHECK(doca_buf_get_data_len(slot.recv_buf, &slot.recv_size));

    spdlog::info("Received {} bytes", slot.recv_size);

    // Submit a new receive task by recycling it (re-submit the same task)
    // We need to reset the buffer data size to zero, because receiving appends
    // at the end.

    DOKA_CHECK(doca_buf_set_data_len(slot.recv_buf, 0));
    DOKA_CHECK(doca_task_submit(doca_rdma_task_receive_as_task(recv_task)));
}

void RdmaSrc::on_recv_error(doca_rdma_task_receive *const recv_task,
                            const doca_data task_user_data,
                            const doca_data ctx_user_data) {
    spdlog::error("ERROR: receive error");
    m_error = true;
}

std::pair<void *, size_t> RdmaSrc::recv() {
    if(m_error) {
        return {};
    }

    // If it's not the first recv(), replenish one credit.
    if(m_recv_count != 0) {
        doca_rdma_task_send *const task = m_send_task_pool.back();
        m_send_task_pool.pop_back();
        DOKA_CHECK(doca_task_submit(doca_rdma_task_send_as_task(task)));
    }

    const Slot &target_slot = m_slots.at(m_recv_count % m_slots.size());
    const size_t target_count = m_recv_count + 1;

    // Poll one receive task.
    while(m_recv_count != target_count && !m_error) {
        if(doca_pe_progress(m_cm.pe().get()) == 0) {
            m_pe_notif.wait();
        }
    }

    if(m_error) {
        return {};
    }

    return {target_slot.mmap.host_data(), target_slot.recv_size};
}