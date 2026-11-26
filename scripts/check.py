#!/usr/bin/env python3
"""Check woYao topic artifacts using only the Python standard library.

Front matter supports flat YAML scalars (plain, single or double quoted).
Calc checks execute trusted local Python; Python -I is not a sandbox.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urldefrag, urlsplit

TAGS = {"官方", "论文", "源码", "实测", "示意", "推断", "未知"}
BUDGETS = {"速览": (0, 1500, 2), "标准": (3000, 6000, 4), "完整": (8000, 15000, 8)}
TAIL = {"自测题", "证据边界", "参考来源"}
HEDGES = re.compile(r"不代表|不意味着|不能推广|并不|不构成|不是.{0,12}也不是|仅为示意|未实测|不等于")
EMPTY = re.compile(r"值得注意的是|众所周知|本文将|总的来说|让我们来看看|不难发现")
VERSION_FILE = Path(__file__).resolve().parents[1] / "VERSION"


def blank(text):
    return re.sub(r"[^\n]", " ", text)


def frontmatter(text):
    """Return flat scalar fields, position-preserving body and parse errors."""
    text = text.lstrip("\ufeff")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text, ["缺少 YAML front matter"]
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return {}, text, ["front matter 没有结束分隔符"]
    fields, errors = {}, []
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z_][\w-]*):[ \t]*(.*?)[\r\n]*", line)
        if not match:
            errors.append("只支持平铺的 key: scalar front matter")
            continue
        key, value = match.groups()
        if key in fields:
            errors.append(f"front matter 字段重复：{key}")
            continue
        try:
            if value.startswith('"'):
                decoder = json.JSONDecoder()
                value, consumed = decoder.raw_decode(value)
                rest = match.group(2)[consumed:].strip()
                if rest and not rest.startswith("#"):
                    raise ValueError("双引号值之后只能有注释")
            elif value.startswith("'"):
                quoted = re.fullmatch(r"'((?:[^']|'')*)'[ \t]*(?:#.*)?", value)
                if not quoted:
                    raise ValueError("单引号值未闭合")
                value = quoted[1].replace("''", "'")
            else:
                value = "" if value.startswith("#") else re.split(r"\s+#", value, maxsplit=1)[0].strip()
                if value in {"null", "Null", "NULL", "~"}:
                    value = ""
                if value and value[0] in "|>{[&*!":
                    raise ValueError("仅支持平铺标量；复杂值请写为引号字符串")
            fields[key] = str(value).strip()
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{key}: {exc}")
    return fields, blank("".join(lines[:end + 1])) + "".join(lines[end + 1:]), errors


def mask_code(text, comments=True):
    """Mask fenced/indented code without changing offsets or line numbers."""
    lines, fence, out = text.splitlines(keepends=True), None, []
    for line in lines:
        opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)", line)
        if fence:
            out.append(blank(line))
            if re.match(r"^ {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}\s*$", line):
                fence = None
        elif opening:
            fence = (opening[1][0], len(opening[1]))
            out.append(blank(line))
        elif re.match(r"^(?: {4}|\t)\S", line):
            out.append(blank(line))
        else:
            out.append(line)
    result = "".join(out)
    if comments:
        result = re.sub(r"<!--[\s\S]*?-->", lambda m: blank(m[0]), result)
    result = re.sub(r"(?<!`)(`+)(?!`)([\s\S]*?)\1(?!`)", lambda m: blank(m[0]), result)
    return result


def headings(text):
    """ATX and setext headings, including start/end offsets."""
    result, lines, offset = [], text.splitlines(keepends=True), 0
    for i, line in enumerate(lines):
        match = re.match(r"^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*\r?\n?$", line)
        if match:
            result.append((len(match[1]), match[2].strip(), offset, offset + len(line)))
        elif i + 1 < len(lines) and line.strip() and re.match(r"^ {0,3}(=+|-+)[ \t]*\r?\n?$", lines[i + 1]):
            result.append((1 if lines[i + 1].lstrip().startswith("=") else 2, line.strip(), offset, offset + len(line) + len(lines[i + 1])))
        offset += len(line)
    return result


def section_name(title):
    return re.sub(r"^\d+[.、． ]*", "", title).strip()


def without_sections(text, names):
    masked = mask_code(text)
    hs = headings(masked)
    spans = []
    for i, (level, title, start, _) in enumerate(hs):
        if section_name(title) in names:
            end = next((h[2] for h in hs[i + 1:] if h[0] <= level), len(text))
            spans.append((start, end))
    for start, end in reversed(spans):
        text = text[:start] + blank(text[start:end]) + text[end:]
    return text


def reader_copy(text):
    _, body, _ = frontmatter(text)
    body = without_sections(body, {"自测题"})
    return re.sub(r"<!--[\s\S]*?-->", "", body).strip() + "\n"


def prose_count(text):
    _, body, _ = frontmatter(text)
    body = mask_code(without_sections(body, TAIL))
    # Link destinations and formatting are not words in the reader's prose.
    body = re.sub(r"!?\[([^\]]*)\]\([^\n]*?\)", r"\1", body)
    body = re.sub(r"https?://[^\s<>]+", "", body)
    return len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff\U00020000-\U0002fa1f]|[A-Za-z0-9]+(?:['’_-][A-Za-z0-9]+)*", body))


def normalize_url(value):
    return urldefrag(value)[0].rstrip("/")


def markdown_links(text):
    """Yield (destination, offset, image), supporting reference links."""
    refs = {}
    for match in re.finditer(r"^ {0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+))", text, re.M):
        refs[match[1].casefold()] = match[2] or match[3]
    pattern = r"(!?)\[([^\]\n]*)\](?:\(\s*(?:<([^>\n]+)>|([^\s()]+(?:\([^()]*\)[^\s()]*)*))(?:\s+[\"'][^\n]*?[\"'])?\s*\)|\[([^\]\n]*)\])"
    used = []
    for match in re.finditer(pattern, text):
        destination = match[3] or match[4] or refs.get((match[5] or match[2]).casefold())
        if destination:
            used.append((match.start(), match.end()))
            yield destination, match.start(), bool(match[1])
    for match in re.finditer(r"(!?)\[([^\]\n]+)\](?![:\[(])", text):
        if any(start <= match.start() < end for start, end in used):
            continue
        if match[2].casefold() in refs:
            yield refs[match[2].casefold()], match.start(), bool(match[1])
    for match in re.finditer(r"https?://[^\s<>\]\"'（）]+", text):
        if any(start <= match.start() < end for start, end in used):
            continue
        value = match[0].rstrip(".,;，。；")
        while value.endswith(")") and value.count(")") > value.count("("):
            value = value[:-1]
        yield value, match.start(), False


def inside(root, candidate):
    path = candidate.resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"路径越出报告目录：{candidate}")
    return path


def normalize_output(text):
    return "\n".join(line.rstrip() for line in text.splitlines()).rstrip("\n")


def hedge_density(text):
    """P0 evaluation metric: regex hits per 1,000 non-whitespace characters."""
    return len(HEDGES.findall(text)) / max(len(re.sub(r"\s", "", text)) / 1000, 0.001)


def check_topic(topic_dir, report="report.md", calc_timeout=30):
    root = Path(topic_dir).resolve()
    issues, stats = [], {}

    def add(level, code, message, file=report, line=1):
        issues.append({"level": level, "code": code, "file": file, "line": line, "message": message})

    try:
        source = inside(root, root / report)
        if source.parent != root or source.suffix != ".md":
            raise ValueError("--report 只能选择报告目录内的 .md 文件")
    except ValueError as exc:
        add("ERROR", "C01", str(exc))
        return {"diagnostics": issues, "stats": stats, "errors": 1, "warnings": 0}
    sidecar = root / "_work" if report == "report.md" else root / "_work" / "variants" / source.stem
    files = {"report": source, "brief": sidecar / "brief.md", "map": sidecar / "map.md", "evidence": root / "_work" / "evidence.md"}
    texts = {}
    for name, file in files.items():
        try:
            texts[name] = inside(root, file).read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError, ValueError) as exc:
            add("ERROR", "C01", f"无法读取 {file.relative_to(root)}：{exc}", str(file.relative_to(root)))
            texts[name] = ""
    metadata, body, errors = frontmatter(texts["report"])
    for message in errors:
        add("ERROR", "C02", message)
    for field in ("title", "date", "skill", "reader", "purpose", "depth"):
        if not metadata.get(field):
            add("ERROR", "C02", f"缺少非空字段：{field}")
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    if metadata.get("skill") != f"woyao v{version}":
        add("ERROR", "C02", f"skill 应为 woyao v{version}")
    if "skill_version" in metadata and metadata["skill_version"] != version:
        add("ERROR", "C02", f"skill_version 应为 {version}")
    if metadata.get("reader") and not re.match(r"^[ABC](?:$|[ （(])", metadata["reader"]):
        add("ERROR", "C02", "reader 须以 A、B 或 C 档位开头")
    if metadata.get("date"):
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", metadata["date"]):
                raise ValueError("date format")
            dt.date.fromisoformat(metadata["date"])
        except ValueError:
            add("ERROR", "C02", "date 应为有效 YYYY-MM-DD 日期")
    brief, _, brief_errors = frontmatter(texts["brief"])
    for error in brief_errors:
        add("ERROR", "C04", f"brief: {error}", str(files["brief"].relative_to(root)))
    depth = brief.get("depth", "")
    if depth not in BUDGETS:
        add("ERROR", "C04", "brief.depth 必须为 速览 / 标准 / 完整")
    if metadata.get("depth") != depth:
        add("ERROR", "C04", "报告 depth 与 brief.depth 不一致")
    if brief.get("reader") and metadata.get("reader", "")[:1] != brief["reader"][:1]:
        add("ERROR", "C02", "报告 reader 与 brief.reader 不一致")
    if brief.get("purpose") and metadata.get("purpose") != brief["purpose"]:
        add("ERROR", "C02", "报告 purpose 与 brief.purpose 不一致")
    if "skill_version" in brief and brief["skill_version"] != version:
        add("ERROR", "C02", f"brief.skill_version 应为 {version}", str(files["brief"].relative_to(root)))
    low, high, minimum_sources = BUDGETS.get(depth, BUDGETS["标准"])
    if "budget_chars" in brief:
        if not re.fullmatch(r"[1-9]\d*", brief["budget_chars"]):
            add("ERROR", "C04", "brief.budget_chars 须为正整数")
        else:
            high = int(brief["budget_chars"])
            if high < low:
                low = 0
    count = prose_count(texts["report"])
    if count > high:
        add("ERROR", "C04", f"正文 {count} 字，超过上限 {high}")
    elif count < low:
        add("WARN", "C04", f"正文 {count} 字，低于参考下限 {low}")
    clean = mask_code(body)
    line_at = lambda offset: body.count("\n", 0, offset) + 1
    map_text = mask_code(texts["map"])
    goals = list(re.finditer(r"^ {0,3}###\s+G(\d+)\b([^\n]*)", map_text, re.M))
    ids = [int(goal[1]) for goal in goals]
    extension = re.search(r"^#\s+扩展学习目标题\s*$", map_text, re.M)
    base = [goal for goal in goals if int(goal[1]) <= 5]
    if ids[:5] != [1, 2, 3, 4, 5] or len(set(ids)) != len(ids) or (len(ids) != 5 and not (extension and ids == list(range(1, len(ids) + 1)) and all(g.start() > extension.start() for g in goals[5:]))):
        add("ERROR", "C03", "基础题须为 G1–G5；扩展题须放在 # 扩展学习目标题 下从 G6 连续编号", str(files["map"].relative_to(root)))
    if sum("〔为什么〕" in goal[2] for goal in base) < 2 or not any("〔迁移/判断〕" in goal[2] for goal in base):
        add("ERROR", "C03", "基础题至少 2 道〔为什么〕和 1 道〔迁移/判断〕", str(files["map"].relative_to(root)))
    for index, goal in enumerate(goals):
        content = map_text[goal.end():goals[index + 1].start() if index + 1 < len(goals) else len(map_text)]
        responsible = re.search(r"负责节[：:]\s*(\S[^\n]*)", content)
        answer = re.search(r"答案要点[：:]([^\n]*)\n((?:[ \t]+[-*+]\s+[^\n]+\n?)+)", content)
        points = re.findall(r"^[ \t]+[-*+]\s+\S", answer[2], re.M) if answer else []
        if not responsible or len(points) < 2:
            add("ERROR", "C03", f"G{goal[1]} 需要负责节和至少 2 条缩进答案要点", str(files["map"].relative_to(root)), map_text.count("\n", 0, goal.start()) + 1)
    entries = list(re.finditer(r"^ {0,3}##\s+E\d+\b[^\n]*", texts["evidence"], re.M))
    if not entries:
        add("ERROR", "C06", "证据台账至少需要一个 ## E1 条目", "_work/evidence.md")
    ledger_urls, primary_urls = set(), set()
    for index, entry in enumerate(entries):
        content = texts["evidence"][entry.end():entries[index + 1].start() if index + 1 < len(entries) else len(texts["evidence"])]
        fields = {}
        for field in ("断言", "标签", "来源", "摘录"):
            match = re.search(r"^\s*[-*]?\s*" + field + r"[：:][ \t]*(\S[^\n]*)", content, re.M)
            if not match:
                add("ERROR", "C06", f"{entry[0].strip()} 缺少非空{field}", "_work/evidence.md")
            else:
                fields[field] = match[1].strip()
        tag = fields.get("标签", "").strip("〔〕")
        if tag and tag not in TAGS:
            add("ERROR", "C06", f"台账标签非法：{tag}", "_work/evidence.md")
        urls = {normalize_url(url) for url, _, _ in markdown_links(fields.get("来源", "")) if url.startswith(("http://", "https://"))}
        ledger_urls.update(urls)
        if tag in {"官方", "论文", "源码"}:
            primary_urls.update(urls)
        if fields.get("来源") and not urls and tag not in {"实测", "示意", "未知"}:
            add("ERROR", "C06", "远程证据来源缺少 http(s) URL", "_work/evidence.md")
    seen_links = set()
    image_count = 0
    for url, offset, image in markdown_links(clean):
        if image:
            image_count += 1
            try:
                parsed = urlsplit(url)
                if parsed.scheme or parsed.netloc or re.match(r"^[\\/]", url):
                    raise ValueError("图片须为报告目录内的相对路径")
                target = inside(root, root / unquote(parsed.path))
                if not target.is_file():
                    raise ValueError("图片文件不存在")
            except (ValueError, OSError) as exc:
                add("ERROR", "C10", f"{url}：{exc}", line=line_at(offset))
        if url.startswith(("https://", "http://")) and not image and normalize_url(url) not in ledger_urls and url not in seen_links:
            seen_links.add(url)
            add("ERROR", "C05", f"外链未入账：{url}", line=line_at(offset))
    markers = re.findall(r"<!--\s*calc:\s*(.*?)\s*-->", mask_code(body, comments=False))
    for name in sorted(set(markers)):
        try:
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", name):
                raise ValueError("calc 名称仅允许字母、数字、下划线和短横线")
            calc_dir = inside(root, root / "_work" / "calc")
            script = inside(calc_dir, calc_dir / (name + ".py"))
            expected = inside(calc_dir, calc_dir / (name + ".out"))
            if not script.is_file() or not expected.is_file():
                raise ValueError("缺少同名 .py 或 .out")
            result = subprocess.run([sys.executable, "-I", "-X", "utf8", str(script)], cwd=calc_dir, capture_output=True, encoding="utf-8", timeout=calc_timeout)
            if result.returncode:
                raise ValueError(f"脚本退出 {result.returncode}：{result.stderr.strip()[:200]}")
            if normalize_output(result.stdout) != normalize_output(expected.read_text(encoding="utf-8-sig")):
                raise ValueError("脚本 stdout 与 .out 不一致")
        except (ValueError, OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
            add("ERROR", "C07", f"{name}: {exc}")
    tag_counts = Counter()
    for match in re.finditer(r"〔([^〕]+)〕", clean):
        labels = [label.strip() for label in match[1].split("·")]
        if not labels or any(label not in TAGS for label in labels):
            add("ERROR", "C08", f"证据标签非法：{match[0]}", line=line_at(match.start()))
        else:
            tag_counts.update(labels)
    hs = headings(clean)
    names = {section_name(title) for level, title, _, _ in hs if level == 2}
    for title in ("回到开头", "自测题", "证据边界", "参考来源"):
        if title not in names:
            add("ERROR", "C09", f"缺少 ## {title}")
    first_h2 = next((start for level, _, start, _ in hs if level == 2), len(clean))
    opening = re.sub(r"^\s*#.*$", "", clean[:first_h2], flags=re.M)
    if not metadata.get("reader", "").startswith("C") and re.search(r"是一种|是一个|指的是|是指|\bis a\b", opening, re.I):
        add("WARN", "C11", "开头包含定义句；检查是否先建立了读者问题")
    prose = clean
    for _, _, start, end in reversed(hs):
        prose = prose[:start] + blank(prose[start:end]) + prose[end:]
    defined = set()
    for match in re.finditer(r"\*\*([^*\n]{2,20})\*\*", prose):
        term = match[1]
        if term in defined:
            continue
        defined.add(term)
        previous = prose[:match.start()].find(term)
        if previous >= 0:
            add("WARN", "C12", f"“{term}”第 {line_at(previous)} 行先出现，第 {line_at(match.start())} 行才加粗", line=line_at(previous))
    core = mask_code(without_sections(body, TAIL))
    density = hedge_density(texts["report"])
    if density > 3:
        sections = []
        core_hs = [(2, "开场", 0, 0)] + [h for h in headings(core) if h[0] == 2]
        for index, (_, title, start, _) in enumerate(core_hs):
            section = core[start:core_hs[index + 1][2] if index + 1 < len(core_hs) else len(core)]
            sections.append((len(HEDGES.findall(section)), title))
        dense = "、".join(title for hits, title in sorted(sections, reverse=True)[:3] if hits)
        add("WARN", "C13", f"限制措辞 {density:.2f}/千字；最多出现于：{dense}")
    for match in EMPTY.finditer(core):
        add("WARN", "C14", f"空话：{match[0]}", line=line_at(match.start()))
    core_hs = [h for h in headings(core) if h[0] == 2]
    for index, (_, title, start, end) in enumerate(core_hs):
        section = core[end:core_hs[index + 1][2] if index + 1 < len(core_hs) else len(core)]
        nonempty = [line for line in section.splitlines() if line.strip()]
        lists = sum(bool(re.match(r"\s*(?:[-*+]|\d+[.)])\s+", line)) for line in nonempty)
        if nonempty and lists / len(nonempty) > 0.5:
            add("WARN", "C15", f"“{title}”列表行占比超过 50%", line=line_at(start))
    lines = core.splitlines()
    for i, line in enumerate(lines):
        if "|" not in line or not re.match(r"\s*\|?\s*:?-{3,}", line):
            continue
        end = i + 1
        while end < len(lines) and lines[end].strip() and "|" in lines[end]:
            end += 1
        after = next((item for item in lines[end:] if item.strip()), "")
        if not after or re.match(r"\s*#", after):
            add("WARN", "C16", "表格后缺少解释结论段落", line=i + 1)
    diagrams = re.findall(r"^ {0,3}(`{3,}|~{3,})mermaid[^\n]*\n([\s\S]*?)^ {0,3}\1\s*$", body, re.M)
    for _, diagram in diagrams:
        nodes = set(re.findall(r"\b([A-Za-z_][\w-]*)\s*(?:\[|\(|\{|-->|==>|-\.->)", diagram))
        nodes.update(re.findall(r"(?:-->|==>|-\.->)\s*(?:\|[^|]*\|\s*)?([A-Za-z_][\w-]*)", diagram))
        nodes.update(re.findall(r"^\s*(?:participant|actor|state)\s+(\w+)", diagram, re.M))
        if len(nodes) > 12:
            add("WARN", "C17", f"Mermaid 含 {len(nodes)} 个节点，建议拆图")
    if len(primary_urls) < minimum_sources:
        add("WARN", "C18", f"一手来源 {len(primary_urls)}，该深度参考下限 {minimum_sources}", "_work/evidence.md")
    stats.update(chars=count, budget=high, tags=dict(tag_counts), figures=image_count + len(diagrams), sources=len(ledger_urls), primary_sources=len(primary_urls), calc=len(set(markers)), hedge_density=round(density, 3))
    add("INFO", "C19", f"字数 {count}/{high}｜标签 {dict(tag_counts)}｜图 {stats['figures']}｜来源 {len(ledger_urls)}｜calc {stats['calc']}")
    return {"diagnostics": issues, "stats": stats, "errors": sum(i["level"] == "ERROR" for i in issues), "warnings": sum(i["level"] == "WARN" for i in issues)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic_dir", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--reader-copy", action="store_true", help="生成去掉自测题的读者副本，已有不同内容文件会保留")
    parser.add_argument("--report", default="report.md", help="报告变体，如 report.A.md（使用自己的 brief/map sidecar）")
    args = parser.parse_args(argv)
    result = check_topic(args.topic_dir, args.report)
    if args.reader_copy:
        try:
            root = args.topic_dir.resolve()
            source = inside(root, root / args.report)
            destination = inside(root, root / "_work" / ("reader-copy.md" if args.report == "report.md" else source.stem + ".reader-copy.md"))
            content = reader_copy(source.read_text(encoding="utf-8-sig"))
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                if destination.read_text(encoding="utf-8") != content:
                    raise ValueError(f"已有读者副本保留：{destination}；移到修订档案后再生成")
            else:
                with destination.open("x", encoding="utf-8", newline="\n") as output:
                    output.write(content)
            result["reader_copy"] = str(destination)
        except (OSError, UnicodeError, ValueError) as exc:
            result["diagnostics"].append({"level": "ERROR", "code": "C01", "file": args.report, "line": 1, "message": str(exc)})
            result["errors"] += 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for issue in result["diagnostics"]:
            print(f"{issue['level']:<5} {issue['code']} {issue['file']}:{issue['line']} {issue['message']}")
        print(f"结果：{result['errors']} ERROR，{result['warnings']} WARN")
        if result.get("reader_copy"):
            print(f"读者副本：{result['reader_copy']}")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
