from math import log

idf = log(1 + (4 - 3 + 0.5) / (3 + 0.5))
k1, b = 1.2, 0.75
for label, tf, length, average in [
    ("short", 1, 50, 150),
    ("ordinary", 3, 150, 150),
    ("long", 3, 300, 150),
    ("long_plus_3_matches", 6, 303, 150.75),
]:
    ratio = length / average
    adjustment = 1 - b + b * ratio
    effective_tf = tf / adjustment
    score = idf * (k1 + 1) * effective_tf / (effective_tf + k1)
    print(f"{label}: tf={tf}, length={length}, avgdl={average}, ratio={ratio:.6f}, L={adjustment:.6f}, effective_tf={effective_tf:.6f}, score={score:.6f}")
