# BM25 旧版基线研究笔记

运行环境：Codex 子 agent，任务开始后先读取 `git show d9d8776:SKILL.md` 及该提交的 research-workflow、evidence-policy、writing-modes、output-contract、validation。未读取新规划或金标准题。

日期：2026-11-25。宿主时间/token 统计未暴露，耗时、token 记未知。

研究问题：从一次排序讲清词频、IDF、长度调整；用同一语料复算完整分数；解释参数、中文分析输入、查询资格与排序职责以及语义边界。

实际打开的一手来源：

- https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf ：2009 原作者综述，重点 §3.4.5—3.5 与公式变体；核对长度来源、饱和、常数缩放。
- https://lucene.apache.org/core/9_12_3/core/org/apache/lucene/search/similarities/BM25Similarity.html ：固定版本 API，核对 IDF、默认参数、平均字段长度。
- https://raw.githubusercontent.com/apache/lucene/releases/lucene/9.12.3/lucene/core/src/java/org/apache/lucene/search/similarities/BM25Similarity.java ：固定版本源码，核对实际 scorer。
- https://www.elastic.co/docs/reference/elasticsearch/index-settings/similarity ：默认 k1/b 与含义。
- https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-match-query ：text 查询分析和默认 OR。
- https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-match-query-phrase ：分析后位置匹配和 slop。
- https://www.elastic.co/docs/api/elasticsearch/operation/operation-indices-analyze ：分析器输出和字段参数。
- https://www.elastic.co/docs/reference/elasticsearch/plugins/analysis-smartcn ：中文分词能力。
- https://www.elastic.co/docs/api/elasticsearch/operation/operation-explain ：单文档匹配与打分解释。
- https://www.elastic.co/docs/solutions/search/hybrid-search ：词法/向量组合能力。

一次打开错误路径 https://www.elastic.co/docs/reference/text-analysis/analysis-smartcn 返回 404，随后找到并打开正确的插件路径；错误页面未作为证据。

算例：`calc/bm25.py`，Python 3.14.0 标准库，真实执行；输出存同名 .out。教学公式包含共同常数 k1+1，解释其与 Lucene 固定版本实现差别。

自查：人工逐节核对输入/概念/变换/结果/边界与章节衔接。没有独立读者测验，没有搜索引擎执行或检索质量评测。
