# Changelog

## 0.20.0-preview.1 — 2026-11-25

本地重构候选，正式发布门槛尚未全过。

- 默认仅Markdown；HTML入口迁到 `scripts/html/export.cjs`，PDF改浏览器打印。移除md-to-pdf/Puppeteer和内部接口、旧发布/清单工具、字体。
- 新增参数规划、三种骨架、`_work/`、证据标签台账、calc复算、C01–C19检查器及独立读者/判分。
- 结尾从 `oOO!` 改为“回到开头”；追问保存快照，读者变体使用独立brief/map。
- 六题固定评测和原始测验记录保留在evals；实际结果与依赖体积见 [施工状态](evals/implementation.md)。
- [Skills安装器](https://github.com/vercel-labs/skills/blob/main/src/installer.ts)与[排除规则](https://github.com/vercel-labs/skills/blob/main/src/skill-hash.ts)没有提供本计划假定的.skillignore保证，改用明确清单构建精简安装目录；仓库直装与精简包大小分别记录。
- 原样例保留本地 `legacy-examples`（`d9d8776`），不随精简包分发。

## 历史来源与维护记录

原版 `d9d8776` / 0.19.0-preview.5 默认MD+HTML，PDF走md-to-pdf5.2.5内部接口、MathJax、Mermaid、Puppeteer，HTML间接取marked且要求Mermaid预转SVG。

原README记载preview.3发布前21项Python回归和HTML/Skill校验；这是原版记录，本次不沿用为重构后的PASS。历史BM25、亿级RAG、恢复图样例保留生成版本。

Skill起源于用户提供的v0.15完整修订包，曾引用其中计划第17–18节；原包的数字和PASS仅作历史记录，不是运行依赖。图型规则曾参考Paper Framework Figure Studio Pro；新版按教学问题选Mermaid、数据表或状态对比，旧漫画与字体许可可从原提交回查。
