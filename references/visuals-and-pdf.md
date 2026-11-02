# 图、数学与 PDF 导出

## 正文资源

Markdown 是唯一正文源。原图需有解释价值和可用许可；无合适图时保留可编辑 Mermaid 围栏。图题解释节点/箭头和假设，复杂图拆开，避免缩成不可读文字。

公式使用 `$...$` 或 `$$...$$`，就近定义符号、单位与条件。代码美元保持代码；普通美元转义。图片先保存到报告目录内，Markdown 使用相对路径；联网取图属于研究准备，不由转换阶段隐式下载。

## 按需 PDF 导出入口

```text
node <skill-dir>/scripts/export_pdf.cjs <report.md> --output-dir <新报告目录>
```

用户要求 PDF 时使用 md-to-pdf＋本地 MathJax/Mermaid 配置，同源生成 PDF 并复制必要正文/图片。已有同名文件默认保留；更新时优先新修订目录，明确授权覆盖才处理旧目标。导出失败保留源 Markdown，不把部分构建当成功。

首次 PDF 需要 Node 22.12+、Chrome/Chromium 和合适中文字体；优先复用宿主已有能力。缺 npm 依赖时在 Skill 根目录运行 `npm ci --prefix scripts --ignore-scripts --no-audit --no-fund`。脚本优先 `WOYAO_BROWSER_PATH` 指定路径，然后本机 Chrome，再尝试 Puppeteer 已下载浏览器；均缺失时按错误提示补充。Linux 缺系统库按浏览器实际错误处理。后续复用，不每次重装。日常导出无需 Python/虚拟环境。

`--work <新目录>` 可保留 HTML、公式/图 SVG 与构建记录以排查问题。旧 `render_knowledge.cjs source.md --work build` 接口仍能构建候选；`--relaxed` 作为兼容参数保留，不再强制文章章节。

## 版式与页面复核

沿用浅色 A4 单栏、清晰中文字体、约 20 mm 页边距；固定模板由 assets/notes-light.css 管理。表头跨页重复、代码换行、图题尽量同页；公式完整，宽图/式拆分，不靠缩小正文凑页数。

实际查看每页，发现问题再调整。可使用宿主现有 PDF 查看/渲染能力；Poppler 仅是页面转图工具，不是导出前置依赖。没有 PDF 执行能力时交付完整 Markdown，并准确说明 PDF 尚未完成。
