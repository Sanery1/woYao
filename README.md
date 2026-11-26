# woYao

把技术主题研究清楚，按你的基础写成能读懂、能复核、能继续追问的中文学习报告。

开发版本：**[0.20.0-preview.1](VERSION)**。默认 Markdown，HTML 可选，PDF 用浏览器打印。实际验收见 [评测](evals/results.md) 与 [施工状态](evals/implementation.md)。

## 用法

```text
使用 woYao 速览 BM25，我是后端开发，只要 Markdown
使用 woYao 研究 KV cache，我不写代码，想理解显存和成本，标准深度
使用 woYao 帮我做向量数据库选型，我会后端，标准深度，直接写
```

缺少关键参数时一次问齐，已有信息直接采用。标准/完整先看大纲与五道目标题，可回复“直接写”。速览≤1500字，标准3000–6000，完整8000–15000；用户明确预算优先。

正文为 `report.md`，`_work/` 保存 brief、问题地图、证据摘录、复算和测验。标准/完整用独立模拟读者作答、另一个代理判分；不支持代理时记“未测”。模型测验提供质量线索，实际理解仍以读者反馈为准。

可追问“第3节没懂”“继续深入X”“换成给产品经理看的版本”。定点修订先留快照，换档位生成新文件。

## 安装

根目录是标准 Skill，入口 [SKILL.md](SKILL.md)。宿主提供研究、文件和代理能力；检查器只用 Python 3.10+ 标准库。

精简包按明确清单构建（输出路径须不存在）：

```sh
python scripts/package_skill.py
npx skills add ./build/woyao --skill woyao
```

也可把 `build/woyao` 复制到宿主 skills 目录。包排除评测、完整样例、测试与 node_modules，构建时检查小于200KB。安装不依赖未经验证的 `.skillignore`。

当前重构在本地 `rebuild` 分支。直接 `npx skills add Sanery1/woYao --skill woyao` 安装的是远端版本，且可能复制开发资料；新版未发布前不会自动安装本地改动。

## HTML 与 PDF

Markdown 无需 Node。可选 HTML 使用 Node 22.12+（Node20未测）：

```sh
npm ci --prefix scripts/html --ignore-scripts --no-audit --no-fund
node scripts/html/export.cjs path/to/report.md
node scripts/html/export.cjs path/to/report.md --output path/to/report-v2.html
```

HTML 自包含图片、数学和 Mermaid，无图时不嵌图形库。已有文件拒绝覆盖；原始 HTML 按文本处理，仅允许模板的受限 details/summary。PDF：浏览器打开 HTML，等图渲染后打印、另存为PDF；检查长表、公式、图和代码。打印采用A4、20mm页边距并隐藏侧栏。

## 维护与样例

试跑报告在 `evals/runs/final/`，达到发布门槛后才晋升为 `docs/examples/` 展示样例。原样例保留在本地 `legacy-examples` 分支及提交 `d9d8776`。

```sh
python scripts/check.py path/to/topic-dir --json
python -m unittest discover -s tests -p "test_*.py" -v
node tests/test_html.cjs
```

检查器重跑可信本地calc，Python `-I` 不是沙箱。来源支持、正文数字、读者测验、视觉和跨宿主验收分别记录。见 [评测规程](evals/rubric.md)、[历史与破坏性变更](CHANGELOG.md)。[MIT License](LICENSE)。
