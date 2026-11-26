N, D = 20_000_000, 768
raw = N * D * 4
pg_value = N * (D * 4 + 8)
print(f'raw_bytes={raw},GB={raw / 10**9:.2f},GiB={raw / 2**30:.2f}')
print(f'pg_vector_values_bytes={pg_value},GB={pg_value / 10**9:.2f},GiB={pg_value / 2**30:.2f}')
passed = 0.01
print(f'candidates=100,pass_rate={passed:.2f},expected_pass={100 * passed:.0f}')
print(f'target=10,expectation_candidates={10 / passed:.0f}')
