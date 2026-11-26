# P9真实追问执行记录

执行日期：2026-11-26。只使用本仓库0.20.0-preview.1的SKILL/VERSION、references与templates指导行为，未加载全局安装版，未读金标或评分；未修改技能代码。

首步行为记录在`evals/behavior.md`：Raft缺读者/深度，一次问齐并等待；后端BM25速览直接继续；产品经理KV cache标准版先展示大纲与五题等确认；单问k1直接短答，不启动研究流程。四项均未运行完整研究。

## 隔离与复制

从`evals/runs/final/T1`只复制report.md、_work/brief.md、map.md、evidence.md及calc脚本/输出到`evals/followup/T1`。不复制reader、grades、fact-audit与历史review评分。新reader-copy均由对应最新正文生成；review统一记录“待独立测验”。

原主评测report.md与初始快照逐字节相同，SHA256为`f40e59412eb416880e7ca8175a0aa0339fdadee633b2af50ae1e62334b399479`。本任务不向主评测报告写回改动。

## ① 第3节没看懂

卡点已知，不重复询问。先保存`T1/_work/report.v1.md`，再只替换第3节。改写先把词频除以长度调整量，再进入饱和曲线，沿同一组四文档展示共同作用；新增真正追加三个查询词时词频、文档长度、平均长度联动的算例。

本地实际执行`bm25_joint.py`，追加后tf=6、长度303、平均长度150.75、调整后次数3.414013、单词贡献0.580606；正文与.out逐项核对。未运行搜索引擎或宣称真实效果。

`step1-integrity.json`及最终`integrity.json`确认第3节前缀、后缀原字节完全相同；第1步结束快照`report.v2.md`的SHA256为`342335dfc281ec4dd586a2c51d682d0c2ac5d9972e6f2e697ed600d11f7e94ac`。`step1.diff`保留实际差异。

实际check：0 ERROR、3 WARN，3515/6000字。仅针对原G3准备独立测验，原题与答案要点未降低。独立测验待协调，不自评分；第1步读者副本为`_work/step1-reader-copy.md`。

## ② 继续深入BM25F

先在map的扩展学习目标题固定G6/G7，原G1–G5不变。实际web打开并定位Microsoft作者两份论文：TREC-2004在线修正版§4.1（PDF第5页）与CIKM 2006多参数优化论文§3.2（PDF第5页），原文短摘录、日期与支持范围写入E8/E9。没有用搜索摘要替代正文。

补证据后，在`回到开头`前追加第5节，讲各字段按各自长度调整、加权合并词频、统一饱和，以及为何不同于各字段先评分再相加。新增`bm25f_demo.py/.out`实际复算。证据边界同步限定为“其他BM25变体”未展开，来源列表新增两篇论文；没有替换前四节。

第一次带`--reader-copy`的check因旧副本存在而拒绝覆盖。将旧副本移至`reader-copy.step1.md`保留后重试：0 ERROR、4 WARN，4238/6000字，未突破预算。此拒绝覆盖是真实观察。新正文存为`report.v3.md`，SHA256为`f265f5c9d23aa165360e0b9751a54ab11e04cdd9288ef51f09f08e14ee446a00`，差异见`step2.diff`。

本步只为G6/G7准备独立测验，满分4分、80%门槛；没有沿用或改动原五题分。测验待协调，无新分数。

## ③ 换给产品经理看的版本

新建`T1/report.A.md`及`_work/variants/report.A/brief.md`、`map.md`。A版沿用理解原理、标准深度，新五题先于写作固定。以业务失败、候选/排序、三种证据、联动变化和验收讨论推进；去掉公式推导与代码。证据与calc复用，读者成绩重新等待独立测验。

实际执行`python scripts/check.py evals/followup/T1 --report report.A.md --json --reader-copy`。首轮0 ERROR、3 WARN，修复新版本的两处术语先出现后定义，再保留初次副本、重新生成。最终0 ERROR、1 WARN，3100/6000字；C11已人工查看，实际开头两段建立处境、问题和读后能力，原因写review。

A版SHA256为`a8fc2541d38e37f4b61d52fe420cc6895c43eccb3a1e556ed8ebf6ba3ece0abe`。原report.md与第2步快照report.v3.md原字节相同；原brief与主评测来源相同；原map只包含第2步已追加的扩展题，原内容前缀/G1–G5相同。另实际对A版check前后记录原report/brief/map三个hash，全部不变。创建A版之前未另存map快照，因此对map的创建过程使用最终内容比较，而不冒称有未采集的事前hash；详情见`integrity.json`。

## 实际执行的验证与边界

- `python scripts/check.py evals/followup/T1 --json --reader-copy`，第1步及第2步运行；第2步拒绝覆盖后保留旧副本重试成功。
- `python scripts/check.py evals/followup/T1 --report report.A.md --json --reader-copy`，A版术语修订后重试成功。
- `python evals/followup/T1/_work/verify_integrity.py`：原主评测正文保持、①只改第3节、②保留原G1–G5且新节位置正确、③check不修改原三个文件均通过assert；输出hash/diff证据。
- 检查器重新运行全部被引用的本地calc并对比.out；无第三方测试框架。
- `git diff --check -- evals/behavior.md evals/followup`运行通过。两处均为新文件/目录，另以字节与diff证据完成内容范围检查，未改动既有脏工作区。

三组独立读者/判分测验仍待协调，本次没有分数、没有学习验收通过声明。根代理已明确让独立测验待协调；不能以机械检查替代读者理解。正文与工作产物已经完成，测验所需副本和题目均保留。
