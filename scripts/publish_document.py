#!/usr/bin/env python3
"""Publish an approved Markdown/PDF pair and its referenced images, with rollback."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

from check_document import resource_path, sha256, validate


def publish(source, build, output_dir, replace=False):
    source = Path(source).resolve(strict=True)
    build = Path(build).resolve(strict=True)
    output = Path(output_dir).resolve()
    info = json.loads((build / "build-manifest.json").read_text(encoding="utf-8"))
    pdf = resource_path(build, info["pdf"]["file"])
    validate(source, build / "build-manifest.json", relaxed=info.get("structure_relaxed", False))
    if source.suffix.lower() != ".md" or not source.stem or source.stem in {".", ".."}:
        raise ValueError("Source must have a valid .md filename")
    entries = [(source, Path(source.name)), (pdf, Path(source.with_suffix(".pdf").name))]
    for image in info["images"]:
        original = resource_path(source.parent, image["source"])
        entries.append((original, original.relative_to(source.parent)))
    unique = {}
    for original, relative in entries:
        key = str(relative).casefold() if os.name == "nt" else str(relative)
        if key in unique and unique[key][0] != original:
            raise ValueError(f"Output name collision: {relative}")
        unique[key] = (original, relative)
    entries = list(unique.values())
    output.mkdir(parents=True, exist_ok=True)
    for original, relative in entries:
        target = output / relative
        if not target.resolve().is_relative_to(output):
            raise ValueError(f"Output escapes destination: {relative}")
        if target.exists() and (target.is_dir() or target.is_symlink()):
            raise ValueError(f"Output is not a regular file: {relative}")
        if target.exists() and not replace:
            raise FileExistsError(f"Existing file preserved: {target}; use --replace only for an authorized update")
        if original == target.resolve():
            raise ValueError("Publish from a separate candidate directory to preserve existing files")
    # Staging shares the destination filesystem so each individual replace is
    # atomic. A multi-file pair cannot be crash-atomic; backups remain on failure.
    transaction = Path(tempfile.mkdtemp(prefix=".woyao-publish-", dir=output))
    snapshots, done = {}, []
    try:
        for index, (original, relative) in enumerate(entries):
            target = output / relative
            snapshots[relative] = sha256(target) if target.exists() else None
            shutil.copy2(original, transaction / f"new-{index}")
            if target.exists():
                shutil.copy2(target, transaction / f"old-{index}")
        # Recheck candidates after staging, and reject concurrent target edits.
        validate(source, build / "build-manifest.json", relaxed=info.get("structure_relaxed", False))
        for index, (original, relative) in enumerate(entries):
            if sha256(original) != sha256(transaction / f"new-{index}"):
                raise ValueError("Candidate changed during staging")
            target = output / relative
            current = sha256(target) if target.exists() else None
            if current != snapshots[relative]:
                raise ValueError(f"Target changed during publishing: {relative}")
        journal = {"state": "staged", "entries": [{"target": str(relative), "backup": f"old-{i}" if snapshots[relative] is not None else None} for i, (_, relative) in enumerate(entries)]}
        (transaction / "recovery.json").write_text(json.dumps(journal, ensure_ascii=False, indent=2), encoding="utf-8")
        for index, (_, relative) in enumerate(entries):
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(transaction / f"new-{index}", target)
            done.append((index, relative))
    except BaseException:
        rollback_errors = []
        for index, relative in reversed(done):
            target = output / relative
            try:
                backup = transaction / f"old-{index}"
                if backup.exists():
                    os.replace(backup, target)
                else:
                    target.unlink()
            except OSError as error:
                rollback_errors.append(str(error))
        if rollback_errors:
            raise RuntimeError(f"Rollback incomplete; recovery files: {transaction}; {rollback_errors}")
        # Keep recovery artifacts for inspection, even after a successful rollback.
        print(f"Publishing failed; original files restored/preserved. Staging: {transaction}", file=sys.stderr)
        raise
    else:
        if transaction.resolve().parent != output:
            raise RuntimeError(f"Unexpected staging directory; preserved for inspection: {transaction}")
        shutil.rmtree(transaction)
    return {"status": "PUBLISHED", "files": [str(output / relative) for _, relative in entries]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("--build", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--replace", action="store_true", help="Only for a user-authorized update")
    args = parser.parse_args()
    try:
        print(json.dumps(publish(args.source, args.build, args.output_dir, args.replace), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
