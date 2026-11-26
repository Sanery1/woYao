#!/usr/bin/env python3
"""Create a small, self-contained install directory from the maintained sources."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
FILES = ("SKILL.md", "VERSION", "LICENSE", "agents/openai.yaml", "scripts/check.py",
         "scripts/html/export.cjs", "scripts/html/report.css", "scripts/html/report.js",
         "scripts/html/package.json", "scripts/html/package-lock.json", "examples/style-pairs.md")


def package(output):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError(f"Existing path preserved: {output}")
    sources = [ROOT / name for name in FILES]
    sources += sorted((ROOT / "references").glob("*.md"))
    sources += sorted((ROOT / "templates").glob("*.md"))
    for source in sources:
        if not source.is_file() or not source.resolve().is_relative_to(ROOT):
            raise ValueError(f"Missing or outside-package source: {source}")
    total = sum(source.stat().st_size for source in sources)
    if total >= 200_000:
        raise ValueError(f"Skill payload {total} bytes exceeds 200000-byte budget")
    output.mkdir(parents=True)
    for source in sources:
        target = output / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return total, len(sources)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(ROOT / "build" / "woyao"))
    args = parser.parse_args()
    try:
        total, count = package(args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")
    print(f"{Path(args.output).resolve()}: {count} files, {total} bytes (no dependencies/evals/docs/tests)")


if __name__ == "__main__":
    main()
