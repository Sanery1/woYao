#!/usr/bin/env python3
"""Measure a saved report; never invent reader scores or fact-audit results."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("woyao_check", ROOT / "scripts/check.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def measure(topic):
    topic = Path(topic)
    report = (topic / "report.md").read_text(encoding="utf-8-sig")
    result = checker.check_topic(topic)
    return {"path": str(topic), "prose_chars": checker.prose_count(report),
            "nonwhitespace_chars": len("".join(report.split())),
            "hedge_density": checker.hedge_density(report),
            "check_errors": result["errors"], "check_warnings": result["warnings"],
            "stats": result["stats"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic", nargs="+", type=Path)
    args = parser.parse_args()
    print(json.dumps([measure(topic) for topic in args.topic], ensure_ascii=False, indent=2))
