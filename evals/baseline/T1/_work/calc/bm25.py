"""Synthetic, single-field BM25 arithmetic; Python standard library only."""
import math

DOCS = {
    "D1": (4, 1, 1),
    "D2": (8, 3, 0),
    "D3": (16, 3, 2),
    "D4": (4, 1, 0),
    "D5": (8, 1, 0),
    "D6": (8, 0, 0),
}
N = len(DOCS)
AVGDL = sum(row[0] for row in DOCS.values()) / N
DF = [sum(row[i] > 0 for row in DOCS.values()) for i in (1, 2)]
IDF = [math.log(1 + (N - df + 0.5) / (df + 0.5)) for df in DF]


def factor(freq, length, k1=1.2, b=0.75):
    return freq * (k1 + 1) / (freq + k1 * (1 - b + b * length / AVGDL))


print(f"N={N} avgdl={AVGDL:.6f} df={DF} idf={[round(x, 6) for x in IDF]}")
scores = {}
for name, (length, cache, invalid) in DOCS.items():
    parts = [IDF[0] * factor(cache, length), IDF[1] * factor(invalid, length)]
    scores[name] = sum(parts)
    print(f"{name} cache={parts[0]:.6f} invalid={parts[1]:.6f} total={sum(parts):.6f}")
print("rank=" + ">".join(sorted(scores, key=scores.get, reverse=True)))
for freq in (1, 2, 4, 8):
    print(f"tf={freq} length=8 factor={factor(freq, 8):.6f}")
for length in (4, 8, 16):
    print(f"tf=3 length={length} factor={factor(3, length):.6f}")
for k1 in (0, 0.6, 1.2, 2.0):
    print(f"k1={k1} factor(tf1)={factor(1, 8, k1):.6f} factor(tf4)={factor(4, 8, k1):.6f}")
for b in (0, 0.75, 1):
    print(f"b={b} tf=3 short={factor(3, 4, b=b):.6f} long={factor(3, 16, b=b):.6f}")
