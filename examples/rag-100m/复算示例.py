"""Reproduce teaching arithmetic; this does not benchmark a retrieval system."""
import json

N, D = 100_000_000, 768
capacity_gb = {
    'float32': N * D * 4 / 1e9,
    'float16': N * D * 2 / 1e9,
    'int8': N * D / 1e9,
    'pq_96_bytes': N * 96 / 1e9,
    'graph_edges_64x4_bytes': N * 64 * 4 / 1e9,
    'three_copies_float32': N * D * 4 * 3 / 1e9,
}


def trace_total(queue, embed, dense, lexical, fuse, fetch, rerank):
    return queue + embed + max(dense, lexical) + fuse + fetch + rerank


result = {
    'raw_capacity_decimal_GB': capacity_gb,
    'fanout_within_deadline_iid': {s: 0.99 ** s for s in [1, 8, 32, 64]},
    'physical_requests_at_200qps': {'64_shards': 200 * 64, '8_shards': 200 * 8},
    'ivf_balanced_list_scans': N * 32 / 65536,
    'postfilter_expected_candidates_for_20_at_0_1_percent': 20 / 0.001,
    'raw_vector_network_MB_per_query_for_1000': 1000 * D * 4 / 1e6,
    'raw_vector_network_MB_per_second_at_200qps': 1000 * D * 4 * 200 / 1e6,
    'mean_concurrency_at_200qps_100ms': 200 * 0.1,
    'original_single_trace_ms': trace_total(25, 30, 130, 55, 5, 25, 80),
    'ann_only_improved_trace_ms': trace_total(25, 30, 55, 55, 5, 25, 80),
    'multi_stage_improved_trace_ms': trace_total(8, 25, 55, 35, 4, 15, 35),
}

assert result['original_single_trace_ms'] == 295
assert result['ann_only_improved_trace_ms'] == 220
assert result['multi_stage_improved_trace_ms'] == 142
assert abs(capacity_gb['float32'] - 307.2) < 1e-9

if __name__ == '__main__':
    print(json.dumps(result, ensure_ascii=False, indent=2))
