L, H, D, S = 32, 8, 128, 2
per_token = 2 * L * H * D * S
print(f'per_token_KiB={per_token / 1024:.0f}')
print(f'single_8192_GiB={per_token * 8192 / 2**30:.0f}')
for length, concurrent in [(8192, 32), (16384, 32), (16384, 64)]:
    print(f'length={length},concurrent={concurrent},KV_GiB={per_token * length * concurrent / 2**30:.0f}')

print(f"length_and_concurrency_doubled_ratio={(2 * 8192) * (2 * 32) / (8192 * 32):.0f}")
