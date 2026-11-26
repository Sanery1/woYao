"""Produce follow-up byte/hash evidence; no score or learning judgement."""
from pathlib import Path
import difflib
import hashlib
import json
import os
import subprocess

root = Path(__file__).resolve().parent.parent
source = root.parents[1] / "runs" / "final" / "T1"
def sha(data):
    return hashlib.sha256(data).hexdigest()
def text(path):
    return path.read_text(encoding="utf-8")
v1 = (root / "_work/report.v1.md").read_bytes()
v2 = (root / "_work/report.v2.md").read_bytes()
v3 = (root / "_work/report.v3.md").read_bytes()
current = (root / "report.md").read_bytes()
start = v1.index("## 3 ".encode())
end = v1.index("## 4 ".encode(), start)
new_end = v2.index("## 4 ".encode(), start)
assert v1[:start] == v2[:start]
assert v1[end:] == v2[new_end:]
assert (source / "report.md").read_bytes() == v1
assert current == v3
assert (root / "_work/brief.md").read_bytes() == (source / "_work/brief.md").read_bytes()
source_map = text(source / "_work/map.md")
current_map = text(root / "_work/map.md")
assert current_map.startswith(source_map)
assert current_map.split("# 扩展学习目标题")[0].rstrip() == source_map.rstrip()
assert current.index("## 5 继续深入".encode()) < current.index("## 回到开头".encode())
original_paths = [root / "report.md", root / "_work/brief.md", root / "_work/map.md"]
before = {str(p.relative_to(root)): sha(p.read_bytes()) for p in original_paths}
env = dict(os.environ, PYTHONIOENCODING="utf-8")
check = subprocess.run(["python", "scripts/check.py", str(root), "--report", "report.A.md", "--json"], capture_output=True, text=True, encoding="utf-8", env=env, check=True)
(root / "_work/step3-isolation-check.json").write_text(check.stdout, encoding="utf-8")
after = {str(p.relative_to(root)): sha(p.read_bytes()) for p in original_paths}
assert before == after
proof = {
    "source_report_sha256": sha(v1),
    "source_report_still_identical_to_initial_snapshot": True,
    "step1_section3_only": {"prefix_identical": True, "suffix_identical": True, "sha256_after": sha(v2)},
    "step2_sha256_after": sha(v3),
    "step2_original_map_prefix_and_G1_G5_unchanged": True,
    "step2_extension_before_return": True,
    "step3_original_report_identical_to_v3": True,
    "step3_brief_identical_to_source": True,
    "step3_map_contains_only_step2_append_after_source_prefix": True,
    "step3_original_hashes_before_variant_check": before,
    "step3_original_hashes_after_variant_check": after,
    "variant_sha256": sha((root / "report.A.md").read_bytes()),
    "note": "Map source-prefix verification is a final content comparison; no pre-creation map snapshot was captured. The variant-check pre/post hashes are directly observed.",
}
(root / "_work/integrity.json").write_text(json.dumps(proof, indent=2, ensure_ascii=False), encoding="utf-8")
for name, a, b in [("step1", v1, v2), ("step2", v2, v3)]:
    diff = "".join(difflib.unified_diff(a.decode().splitlines(keepends=True), b.decode().splitlines(keepends=True), fromfile=f"{name}-before", tofile=f"{name}-after"))
    (root / f"_work/{name}.diff").write_text(diff, encoding="utf-8")
print(json.dumps(proof, indent=2, ensure_ascii=False))
