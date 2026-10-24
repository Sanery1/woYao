# 图、数学与浅色 PDF

## 选图

寻找原论文/官方/开源项目的高价值机制、比较和实验图，核查版本、出处、许可与改动。许可未知只链接或原创；合法图片本地保存，Markdown 用相对路径，图注写图源/授权。

无合适图时用 Mermaid，保留代码块。图题与正文解释节点/箭头；假设有文字标签，不只靠颜色。复杂图分全貌/局部，不整图缩到不可读。数学使用同一 `$...$`、`$$...$$` 源；代码中的美元保持代码，货币美元转义 `\$`。邻近定义符号与证据性质。

## 内置构建器

`render_knowledge.cjs` 使用 Marked、Mermaid、MathJax、Playwright Chromium，从一个 Markdown 构建候选 `document.pdf`、`rendered.html`、SVG 与 `build-manifest.json`。采用 Mermaid 引擎，不自行转译 flowchart 子集；并非所有插件/实验图均已实测。原始 HTML 按文本处理，元信息注释例外。本地图必须在文档目录内且存在。渲染禁止联网，不执行来源脚本。

依赖见 `scripts/package.json`。优先复用已有包；宿主允许安装时在 `scripts` 运行 `npm ci --no-audit --no-fund`。构建器使用已下载的 Chromium，缺失时使用本机 Chrome；两者均无时运行 `npx playwright install chromium`，不改全局配置。可通过 `NODE_PATH` 指定现有包目录；`WOYAO_BROWSER_PATH` 指定 Chrome/Chromium 可执行文件。Python 需 3.10+；PDF 文本检查依赖见 `scripts/requirements.txt`，推荐在虚拟环境内用 `python -m pip install -r scripts/requirements.txt` 安装。中文字体可使用系统 Microsoft YaHei 或 Noto Sans CJK SC；缺失时先安装字体再验证。缺少 pypdf 时不得报 PDF 验证通过。

```text
node scripts/render_knowledge.cjs topic.md --work build
python scripts/check_document.py topic.md --manifest build/build-manifest.json --pdf build/document.pdf
python scripts/publish_document.py topic.md --build build --output-dir output
```

`--work` 使用专用新目录，避免并发和旧缓存；重复构建换目录。`--relaxed` 适用于用户改结构，不放宽 Skill 版本/图片/语法/哈希。清单记录真实哈希和数量，不证明断言已复验。发布核对清单、暂存和回滚，默认拒绝覆盖；仅授权更新时用 `--replace`，不删除无关资源。失败报告真实状态并保留工作目录。

## 版式与检查

A4 纵向单栏，左右约 20 mm、上下约 19 mm，无大封面；正文 10.5–11 pt、行距约 1.7，H1 约 27 pt、H2 约 16 pt。中文现代字体回退，页眉克制/页脚页码。首屏逐行元信息；浅色纸面、灰蓝正文、少量蓝强调、浅底代码。

表头重复、长代码换行，图与图题尽量同页；公式完整，宽式拆写。不为减页数缩正文/关键图。正常留白可接受，近空白尾页检查成因。

实际渲染检查每页，尤其中文、图中文字、长表、代码、公式、标题与尾页。清单估算图中文字缩放后的字号，低于约 7.5 pt 会提示；这只是排查信号，有提示应改为纵向、给长标签换行或拆图，实际确认可读后再发布。可用 `pdftoppm -scale-to 1300 -png document.pdf preview`。文本覆盖不代替视觉检查。

依赖不可用可采用宿主已有的同源 HTML→PDF、Quarto/Typst 等路径，仍核对图、公式、引用和页序。不能用截图充当可检索 PDF。无法完成则交付 Markdown 并说明 PDF 未完成。
