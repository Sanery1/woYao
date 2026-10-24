#!/usr/bin/env python3
"""Check document structure, local resources, build provenance and PDF headings."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def resource_path(root, uri):
    value = unquote(uri)
    if re.match(r"^(?:[a-z][a-z0-9+.-]*:|[\\/])", value, re.I):
        raise ValueError(f"Image must be relative: {uri}")
    root = Path(root).resolve()
    target = (root / value).resolve(strict=True)
    if not target.is_relative_to(root) or not target.is_file():
        raise ValueError(f"Invalid image path: {uri}")
    return target


def prose_and_headings(text):
    text = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", text, count=1, flags=re.S)
    prose, headings = [], []
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            token, rest = marker.groups()
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not rest.strip():
                fence = None
            continue
        if fence is not None:
            continue
        prose.append(line)
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if heading:
            headings.append({"level": len(heading[1]), "text": heading[2], "line": number})
    if fence:
        raise ValueError("Unclosed code fence")
    return "\n".join(prose), headings


def image_paths(source, text):
    prose, _ = prose_and_headings(text)
    prose = re.sub(r"`[^`\n]*`", "", prose)
    # Marked resolves reference-style image links; their authoritative list is
    # checked through the build manifest. Direct images are checked before build.
    uris = re.findall(r'!\[[^\]]*\]\(<?([^\s)>]+)>?(?:\s+["\'][^\n]*?["\'])?\)', prose)
    return [resource_path(Path(source).parent, uri) for uri in uris]


def report_skill_version(text):
    opening = re.split(r"^## ", text, maxsplit=1, flags=re.M)[0]
    versions = re.findall(r"^- \*\*Skill 版本[：:]\*\* woYao v([^\s]+)\s*$", opening, re.M)
    if len(versions) != 1:
        raise ValueError("Expected one Skill 版本: woYao vVERSION before the first H2")
    return versions[0]


def validate(source, manifest=None, pdf=None, relaxed=False):
    source = Path(source).resolve(strict=True)
    text = source.read_text(encoding="utf-8-sig")
    prose, headings = prose_and_headings(text)
    warnings = []
    version = report_skill_version(text)
    if not manifest:
        installed = (Path(__file__).resolve().parents[1] / "VERSION").read_text(encoding="utf-8").strip()
        if version != installed:
            raise ValueError("Report Skill version differs from installed Skill")
    if not relaxed:
        if sum(h["level"] == 1 for h in headings) != 1:
            raise ValueError("Expected exactly one H1 title")
        h2 = [h["text"] for h in headings if h["level"] == 2]
        if h2[-2:] != ["oOO!", "参考资料与证据级别"]:
            raise ValueError("Last two H2 chapters must be oOO! then 参考资料与证据级别")
        metadata = re.search(r"<!-- woyao:metadata -->(.*?)<!-- /woyao:metadata -->", text, re.S)
        if not metadata:
            raise ValueError("Document metadata list is missing")
        for field in ["研究日期", "读者", "证据范围", "文档版本", "生成者"]:
            if not re.search(rf"^- \*\*{field}[：:]\*\*\s+\S", metadata[1], re.M):
                raise ValueError(f"Missing metadata field: {field}")
        if not re.search(r"^- \*\*生成者[：:]\*\* woYao skill by saneryi\s*$", metadata[1], re.M):
            raise ValueError("Generator credit differs from document contract")
        date = re.search(r"研究日期[：:]\*\*\s+(\d{4}-\d{2}-\d{2})", metadata[1])
        if not date:
            raise ValueError("Research date must be YYYY-MM-DD")
        from datetime import date as calendar_date
        calendar_date.fromisoformat(date[1])
        questions = next((i for i, h in enumerate(headings) if h["level"] == 2 and "读完以后，你应该能回答这些问题" in h["text"]), None)
        if questions is None:
            raise ValueError("Missing macro learning questions section")
        q_heading = headings[questions]["text"]
        q_start = prose.index(q_heading) + len(q_heading)
        q_end = prose.find("\n## ", q_start)
        question_count = len(re.findall(r"^\s*\d+[.)、]\s+", prose[q_start:q_end if q_end >= 0 else None], re.M))
        if not 4 <= question_count <= 6:
            warnings.append(f"Learning question count is {question_count}; review appropriateness, not a mandatory quota")
    resources = image_paths(source, text)
    if manifest:
        manifest = Path(manifest).resolve(strict=True)
        info = json.loads(manifest.read_text(encoding="utf-8"))
        if info.get("skill_version") != version:
            raise ValueError("Report Skill version differs from build manifest")
        if info["source_sha256"] != sha256(source):
            raise ValueError("Markdown changed since build")
        if info["source"] != source.name:
            raise ValueError("Manifest source name differs")
        if [h["text"] for h in headings] != [h["text"] for h in info["headings"]]:
            raise ValueError("Markdown parser heading disagreement")
        for image in info["images"]:
            target = resource_path(source.parent, image["source"])
            if sha256(target) != image["sha256"]:
                raise ValueError(f"Image changed since build: {image['source']}")
        built_pdf = resource_path(manifest.parent, info["pdf"]["file"])
        if sha256(built_pdf) != info["pdf"]["sha256"]:
            raise ValueError("PDF changed since build")
        if pdf and sha256(pdf) != info["pdf"]["sha256"]:
            raise ValueError("Supplied PDF does not match build")
        for diagram in info.get("diagrams", []):
            if diagram.get("min_label_pt") is not None and diagram["min_label_pt"] < 7.5:
                warnings.append(f"Figure {diagram['index']} labels scale to about {diagram['min_label_pt']} pt; reflow or split and inspect before publishing")
    pages = None
    if pdf:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf))
        pages = len(reader.pages)
        if not pages:
            raise ValueError("PDF has no pages")
        contents = [page.extract_text() or "" for page in reader.pages]
        if any(not content.strip() for content in contents):
            raise ValueError("PDF contains an empty or non-searchable page")
        normalized = lambda value: re.sub(r"[^\w]", "", value, flags=re.UNICODE)
        all_text = normalized("\n".join(contents))
        if normalized(f"woYao v{version}") not in normalized(contents[0]):
            raise ValueError("Skill version missing from first PDF page")
        cursor = 0
        for heading in headings:
            if heading["level"] > 2:
                continue
            expected = normalized(heading["text"])
            position = all_text.find(expected, cursor)
            if position < 0:
                raise ValueError(f"Missing or reordered PDF heading: {heading['text']}")
            cursor = position + len(expected)
        if len(contents[-1].strip()) < 120:
            warnings.append("Near-empty final PDF page; inspect layout")
    return {"status": "PASS", "headings": len(headings), "direct_images": len(resources), "pdf_pages": pages, "warnings": warnings, "external_claims_verified": False, "visual_review": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("--manifest")
    parser.add_argument("--pdf")
    parser.add_argument("--relaxed", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.source, args.manifest, args.pdf, args.relaxed), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, ImportError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
