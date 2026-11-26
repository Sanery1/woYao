# 检查记录

## 机械检查与事实复核

- 版本：0.20.0-preview.1；仅交付Markdown。
- 首轮check.py：2736正文计数；已补充“验证的对象到底是谁”，解释持有证明、并发尝试与授权身份的区别。
- 首轮C08：图注把依据写入标签内部；已改为独立合法示意标签。
- 修订后正文：3009（中文字符加英文词，排除元数据、代码及文末辅助章节）。
- C12两项WARN：PKCE与授权码首先在读者范围行/场景中出现，然后正文就近定义；属于场景先建立对象，定义未跨节，不影响解释。标题不算定义。
- 原始来源由协调代理联网打开后共享，本代理核对原文片段；每来源摘录合计少于25英文词。RFC9700§2.2仅用目录作为独立令牌保护议题的证据，实际令牌泄漏分析从流程作推断。
- 没有外部系统接入实验；所有示例为教学情境，没有伪称实测。

## 独立读者测验

待独立读者测验；按主代理分工由独立代理执行，不由作者自评分。G1–G5已在研究与写作之前固定，未降低题目难度。

## 变更范围

仅evals/runs/final/T5；旧读者副本已移到_work/revisions/reader-copy.pre-expansion.md。正式交付以report.md与最新reader-copy.md为准。

## 最终机械结果

实际执行 `python scripts/check.py evals/runs/final/T5 --reader-copy`：0 ERROR、2 WARN；最新副本已生成。又执行JSON格式检查并保存_work/check.json，同样0 ERROR、2 WARN。`git diff --check -- evals/runs/final/T1 evals/runs/final/T5`实际运行无空白错误；产物为未跟踪新增文件，完整内容由check.py检查。状态只检查自身目录，没有提交。
