"""Reproduce the introductory BM25 walkthrough; no external dependencies."""
from collections import Counter
from math import log


DOCUMENTS = {
    "甲": "苹果 手机 手机 推荐".split(),
    "乙": "苹果 苹果 苹果 推荐".split(),
    "丙": "苹果 手机 价格 推荐".split(),
}
QUERY = ["苹果", "手机"]


def calculate(documents):
    average_length = sum(map(len, documents.values())) / len(documents)
    idf = {
        term: log(1 + (len(documents) - sum(term in doc for doc in documents.values()) + 0.5)
                  / (sum(term in doc for doc in documents.values()) + 0.5))
        for term in QUERY
    }
    rows = {}
    for name, tokens in documents.items():
        tf = Counter(tokens)
        length_factor = 1.2 * (1 - 0.75 + 0.75 * len(tokens) / average_length)
        contributions = {
            term: idf[term] * tf[term] * 2.2 / (tf[term] + length_factor)
            for term in QUERY
        }
        rows[name] = {"length": len(tokens), "K": length_factor,
                      "contributions": contributions, "score": sum(contributions.values())}
    return {"average_length": average_length, "idf": idf, "documents": rows}


if __name__ == "__main__":
    import json

    original = calculate(DOCUMENTS)
    extended = dict(DOCUMENTS)
    extended["乙"] = DOCUMENTS["乙"] + "评测 使用 体验 分享".split()
    changed = calculate(extended)
    assert [round(original["documents"][name]["score"], 3) for name in ["甲", "丙", "乙"]] == [0.780, 0.604, 0.210]
    assert changed["documents"]["乙"]["score"] < original["documents"]["乙"]["score"]
    assert changed["documents"]["甲"]["score"] > original["documents"]["甲"]["score"]
    print(json.dumps({"original": original, "longer_second_document": changed}, ensure_ascii=False, indent=2))
