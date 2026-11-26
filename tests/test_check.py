"""Behavioral fixtures are generated in a temporary topic directory."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check.py"
spec = importlib.util.spec_from_file_location("woyao_check", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class TopicChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.version = check.VERSION_FILE.read_text(encoding="utf-8").strip()
        self.report = f"""---
title: 临时合格报告
date: 2026-11-25
skill: woyao v{self.version}
reader: B
purpose: 理解原理
depth: 速览
---
# 一次查询怎样排序

文档库的查询返回一篇周报。读完可以解释排序原因。

## 1 排序为何变化

**词频**表示同一词出现的次数，增加次数的收益逐渐变小。〔官方〕[来源](https://example.com/a#section)

换成长文档时，同样的次数会按长度调整。〔论文〕[论文](https://example.com/b/)

## 回到开头

周报靠重复词命中，因此要先检查查询条件。

## 自测题

为什么增加次数的收益会变小？

<details><summary>答案要点</summary>隐藏答案：饱和。</details>

## 证据边界

两篇资料讨论的是示例模型。

## 参考来源

[来源](https://example.com/a) 和 [论文](https://example.com/b)。
"""
        goals = "# 学习目标题\n"
        for number in range(1, 6):
            kind = "为什么" if number < 3 else "迁移/判断" if number == 3 else "解释"
            goals += f"### G{number}〔{kind}〕问题{number}\n- 负责节：§1\n- 答案要点：\n  - 要点甲\n  - 要点乙\n"
        self.map = goals
        self.evidence = "# 证据台账\n"
        for number, tag, suffix in [(1, "官方", "a"), (2, "论文", "b")]:
            self.evidence += f"## E{number}\n- 断言：词频增长有饱和。\n- 标签：{tag}\n- 来源：https://example.com/{suffix}（访问 2026-11-25）\n- 摘录：frequency saturation\n- 用于：§1\n"
        self.write("report.md", self.report)
        self.write("_work/brief.md", "---\ndepth: 速览\nreader: B\n---\n范围：词频。\n")
        self.write("_work/map.md", self.map)
        self.write("_work/evidence.md", self.evidence)

    def write(self, path, text):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding="utf-8")

    def result(self, **kwargs):
        return check.check_topic(self.root, **kwargs)

    def assertCode(self, code, level="ERROR", **kwargs):
        result = self.result(**kwargs)
        self.assertTrue(any(issue["code"] == code and issue["level"] == level for issue in result["diagnostics"]), result)
        return result

    def assertNoCode(self, code, **kwargs):
        result = self.result(**kwargs)
        self.assertFalse(any(issue["code"] == code for issue in result["diagnostics"]), result)
        return result

    def test_good_topic_c01_to_c18(self):
        result = self.result()
        self.assertEqual(result["errors"], 0, result)
        self.assertEqual(result["warnings"], 0, result)
        self.assertEqual([issue["code"] for issue in result["diagnostics"]], ["C19"])

    def test_c01_missing_artifact(self):
        (self.root / "_work/map.md").unlink()
        self.assertCode("C01")

    def test_c02_missing_and_invalid_fields(self):
        for report in [self.report.replace("title: 临时合格报告\n", ""), self.report.replace(self.version, "0.0.0"), self.report.replace("date: 2026-11-25", "date: 2026-02-30"), self.report.replace("reader: B", "reader: D")]:
            with self.subTest(report=report[:80]):
                self.write("report.md", report)
                self.assertCode("C02")

    def test_c02_flat_scalar_parser(self):
        fields, body, errors = check.frontmatter('---\ntitle: "a: b # value" # comment\nreader: \'B\'\ndepth: 标准 # note\n---\n正文')
        self.assertEqual(errors, [])
        self.assertEqual(fields, {"title": "a: b # value", "reader": "B", "depth": "标准"})
        self.assertTrue(body.endswith("正文"))
        self.assertEqual(check.frontmatter("---\ntitle: # pending\ndate: null\n---\n")[0], {"title": "", "date": ""})
        for text in ['---\ntitle: |\n  nested\n---\n', '---\ntitle: one\ntitle: two\n---\n', '---\ntitle: "unclosed\n---\n']:
            self.assertTrue(check.frontmatter(text)[2])

    def test_c03_missing_goal(self):
        self.write("_work/map.md", self.map[:self.map.index("### G5")])
        self.assertCode("C03")

    def test_c03_goal_requirements(self):
        for data in [self.map.replace("〔为什么〕", "〔解释〕"), self.map.replace("〔迁移/判断〕", "〔解释〕"), self.map.replace("- 负责节：§1\n", ""), self.map.replace("  - 要点乙\n", "")]:
            with self.subTest(data=data[:60]):
                self.write("_work/map.md", data)
                self.assertCode("C03")

    def test_c03_extension_explicit_and_ordered(self):
        extension = "### G6〔为什么〕扩展题\n- 负责节：§2\n- 答案要点：\n  - 一\n  - 二\n"
        self.write("_work/map.md", self.map + extension)
        self.assertCode("C03")
        self.write("_work/map.md", self.map + "# 扩展学习目标题\n" + extension)
        self.assertNoCode("C03")

    def test_c04_over_budget(self):
        self.write("report.md", self.report.replace("## 1 排序为何变化", "汉" * 1501 + "\n\n## 1 排序为何变化"))
        self.assertCode("C04")

    def test_c04_under_budget_and_mismatched_depth(self):
        self.write("_work/brief.md", "---\ndepth: 标准\n---\n")
        self.write("report.md", self.report.replace("depth: 速览", "depth: 标准"))
        self.assertCode("C04", "WARN")
        self.write("report.md", self.report)
        self.assertCode("C04")

    def test_c04_explicit_budget_override(self):
        self.write("_work/brief.md", "---\ndepth: 标准\nbudget_chars: 500\n---\n")
        self.write("report.md", self.report.replace("depth: 速览", "depth: 标准"))
        self.assertNoCode("C04")
        self.assertEqual(self.result()["stats"]["budget"], 500)
        self.write("report.md", self.report.replace("## 1 排序为何变化", "汉" * 1600 + "\n\n## 1 排序为何变化"))
        self.write("_work/brief.md", "---\ndepth: 速览\nbudget_chars: 2000\n---\n")
        self.assertNoCode("C04")
        self.write("_work/brief.md", "---\ndepth: 速览\nbudget_chars: -1\n---\n")
        self.assertCode("C04")

    def test_c02_brief_metadata_consistency(self):
        for fields in ["reader: C", "purpose: 动手实现", "skill_version: 0.0.0"]:
            with self.subTest(fields=fields):
                self.write("_work/brief.md", "---\ndepth: 速览\n" + fields + "\n---\n")
                self.assertCode("C02")
        self.write("_work/brief.md", "---\ndepth: 速览\n---\n")
        self.write("report.md", self.report.replace("title: 临时合格报告", "skill_version: 0.0.0\ntitle: 临时合格报告"))
        self.assertCode("C02")

    def test_c04_count_excludes_code_and_tail(self):
        report = "---\ntitle: x\n---\n你好 hello world\n\n```python\n" + "汉" * 4000 + "\n```\n\n## 自测题\n" + "汉" * 4000
        self.assertEqual(check.prose_count(report), 4)

    def test_c05_unaccounted_link(self):
        self.write("report.md", self.report.replace("https://example.com/a#section", "https://example.com/unlogged"))
        self.assertCode("C05")

    def test_c05_reference_links_and_code(self):
        extra = "\n[x][source]\n[source]: https://example.com/new\n"
        self.write("report.md", self.report + extra)
        self.assertCode("C05")
        self.write("report.md", self.report + "\n```text\nhttps://example.com/new\n```\n<!-- https://example.com/private -->\n")
        self.assertNoCode("C05")

    def test_c05_balanced_parentheses_and_inline_code(self):
        self.write("report.md", self.report.replace("https://example.com/a", "https://example.com/a(b)") + "\n`https://example.com/private`\n")
        self.write("_work/evidence.md", self.evidence.replace("https://example.com/a", "https://example.com/a(b)"))
        self.assertNoCode("C05")

    def test_c06_missing_fields_and_illegal_label(self):
        for field in ["断言", "标签", "来源", "摘录"]:
            with self.subTest(field=field):
                self.write("_work/evidence.md", self.evidence.replace("- " + field + "：", "- 其他："))
                self.assertCode("C06")
        self.write("_work/evidence.md", self.evidence.replace("标签：官方", "标签：传闻"))
        self.assertCode("C06")

    def add_calc(self, script="print('结果 2')\n", expected="结果 2\n"):
        self.write("report.md", self.report.replace("## 1 排序为何变化", "<!-- calc: score -->\n\n## 1 排序为何变化"))
        self.write("_work/calc/score.py", script)
        self.write("_work/calc/score.out", expected)

    def test_c07_reproducible_utf8(self):
        self.add_calc(expected="结果 2  \n\n")
        self.assertNoCode("C07")
        self.assertEqual(self.result()["stats"]["calc"], 1)

    def test_c07_missing_and_mismatched_output(self):
        self.add_calc(expected="3\n")
        self.assertCode("C07")
        (self.root / "_work/calc/score.py").unlink()
        self.assertCode("C07")

    def test_c07_failed_and_timed_out_script(self):
        self.add_calc("raise ValueError('bad')\n")
        self.assertCode("C07")
        self.add_calc("import time\ntime.sleep(2)\n")
        self.assertCode("C07", calc_timeout=0.05)

    def test_c07_path_traversal_never_runs(self):
        self.write("report.md", self.report + "\n<!-- calc: ../outside -->\n")
        with patch.object(check.subprocess, "run") as run:
            self.assertCode("C07")
            run.assert_not_called()

    def test_c07_script_and_output_symlink_escape(self):
        self.add_calc()
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "outside.py"
            target.write_text("print('result')", encoding="utf-8")
            script = self.root / "_work/calc/score.py"
            script.unlink()
            try:
                script.symlink_to(target)
            except OSError:
                self.skipTest("当前 Windows 用户不能创建符号链接")
            with patch.object(check.subprocess, "run") as run:
                self.assertCode("C07")
                run.assert_not_called()

    def test_c08_labels(self):
        self.write("report.md", self.report.replace("〔官方〕", "〔官方·推断〕"))
        self.assertNoCode("C08")
        self.write("report.md", self.report.replace("〔官方〕", "〔可信〕"))
        self.assertCode("C08")
        self.write("report.md", self.report + "\n```text\n〔不是标签〕\n```\n<!-- 〔不是标签〕 -->")
        self.assertNoCode("C08")

    def test_c09_required_sections_not_code_or_comments(self):
        self.write("report.md", self.report.replace("## 回到开头", "<!-- ## 回到开头 -->"))
        self.assertCode("C09")
        self.write("report.md", self.report.replace("## 回到开头", "```text\n## 回到开头\n```"))
        self.assertCode("C09")

    def test_c10_local_image_valid_missing_and_escape(self):
        self.write("figures/a.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.write("report.md", self.report + "\n![图](figures/a.svg)\n")
        self.assertNoCode("C10")
        for image in ["figures/missing.svg", "../outside.svg", "https://example.com/a.svg", "%2e%2e/outside.svg"]:
            with self.subTest(image=image):
                self.write("report.md", self.report + f"\n![图]({image})\n")
                self.assertCode("C10")

    def test_c11_definition_and_c_reader_exception(self):
        report = self.report.replace("文档库的查询返回一篇周报。", "排序是一种计算过程。")
        self.write("report.md", report)
        self.assertCode("C11", "WARN")
        self.write("report.md", report.replace("reader: B", "reader: C"))
        self.assertNoCode("C11")

    def test_c12_term_precedes_definition(self):
        self.write("report.md", self.report.replace("文档库的查询返回一篇周报。", "词频让周报排到了第一。"))
        self.assertCode("C12", "WARN")
        self.write("report.md", self.report.replace("# 一次查询怎样排序", "# 词频"))
        self.assertNoCode("C12")
        self.write("report.md", self.report.replace("文档库的查询返回一篇周报。", "示例配置 `词频` 在代码里。"))
        self.assertNoCode("C12")

    def test_c13_hedge_density(self):
        self.write("report.md", self.report.replace("周报靠重复词命中", "不代表，不意味着，不构成，不等于。周报靠重复词命中"))
        self.assertCode("C13", "WARN")
        self.assertAlmostEqual(check.hedge_density("不代表\n" + "汉" * 997), 1.0)

    def test_c14_empty_phrases(self):
        self.write("report.md", self.report.replace("换成长文档时", "值得注意的是，换成长文档时"))
        self.assertCode("C14", "WARN")

    def test_c15_list_heavy_section(self):
        self.write("report.md", self.report.replace("## 回到开头", "## 2 步骤\n\n- 一\n- 二\n- 三\n\n## 回到开头"))
        self.assertCode("C15", "WARN")

    def test_c16_table_missing_following_conclusion(self):
        table = "| 输入 | 输出 |\n| --- | --- |\n| 1 | 2 |\n\n"
        self.write("report.md", self.report.replace("## 回到开头", table + "## 回到开头"))
        self.assertCode("C16", "WARN")
        self.write("report.md", self.report.replace("## 回到开头", table + "所以输出随输入变化。\n\n## 回到开头"))
        self.assertNoCode("C16")

    def test_c17_large_mermaid(self):
        graph = "```mermaid\nflowchart TD\n" + "\n".join(f"N{i} --> N{i+1}" for i in range(12)) + "\n```\n"
        self.write("report.md", self.report + graph)
        self.assertCode("C17", "WARN")
        self.write("report.md", self.report + "\n```mermaid\nflowchart TD\nA --> B\n```\n")
        self.assertNoCode("C17")

    def test_c18_primary_source_minimum(self):
        self.write("_work/evidence.md", self.evidence.replace("标签：论文", "标签：推断"))
        self.assertCode("C18", "WARN")

    def test_reader_copy_removes_selftest_details_frontmatter_and_comments(self):
        copy = check.reader_copy(self.report + "\n<!-- secret -->\n")
        self.assertNotIn("隐藏答案", copy)
        self.assertNotIn("自测题", copy)
        self.assertNotIn("secret", copy)
        self.assertNotIn("title:", copy)
        self.assertIn("证据边界", copy)
        setext = self.report.replace("## 自测题", "  自测题\n  ------")
        self.assertNotIn("隐藏答案", check.reader_copy(setext))

    def test_reader_copy_does_not_confuse_code_heading(self):
        report = self.report.replace("## 1 排序为何变化", "```text\n## 自测题\n```\n\n## 1 排序为何变化")
        copy = check.reader_copy(report)
        self.assertIn("词频", copy)

    def test_variant_uses_own_brief_map(self):
        self.write("report.A.md", self.report.replace("reader: B", "reader: A"))
        self.write("_work/variants/report.A/brief.md", "---\ndepth: 速览\nreader: A\n---\n")
        self.write("_work/variants/report.A/map.md", self.map)
        original = (self.root / "_work/brief.md").read_bytes()
        self.assertEqual(self.result(report="report.A.md")["errors"], 0)
        self.assertEqual((self.root / "_work/brief.md").read_bytes(), original)

    def test_report_path_cannot_escape(self):
        self.assertCode("C01", report="../report.md")

    def test_cli_json_and_reader_copy_preserves_existing_work(self):
        args = [sys.executable, "-X", "utf8", str(SCRIPT), str(self.root), "--json", "--reader-copy"]
        first = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(first.returncode, 0, first.stderr + first.stdout)
        self.assertEqual(json.loads(first.stdout)["errors"], 0)
        second = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(second.returncode, 0)
        self.write("_work/reader-copy.md", "用户自己的内容")
        third = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(third.returncode, 1)
        self.assertEqual((self.root / "_work/reader-copy.md").read_text(encoding="utf-8"), "用户自己的内容")


if __name__ == "__main__":
    unittest.main()
