# T6 独立事实抽查

抽查日期：2026-11-26。抽样 10 条不同的关键断言；支持 10，不支持 0，无法核实 0；严重错误 0，轻微错误 0。

范围：仅报告、对应证据台账、共享原文缓存和引用的官方原页；未读取 topics 金标或评分。证据台账用于定位，不能单独证明断言。报告原文未修改。

判定规则：严重错误会导致错误技术判断；轻微错误为局部术语或规范强度不准确。无法核实不算通过，不能由未知反推断言为假。共享缓存保留真实 web 工具原文、URL 和原页面行号；本次额外打开的网页按官方 URL 与具体段落定位。教学数字由独立 Python 标准库运算复算，未用台账复述作为数值证明。

## T6-F01：支持（严重度：无）

位置：[report.md:24](D:/Code/Project/woYao/evals/runs/final/T6/report.md:24)；台账定位：E5。

原句/原文片段：得到61.44 GB，约57.22 GiB。

核查来源：独立 Python 整数运算

具体支持段及核对：20000000*768*4=61440000000 字节；除 10^9=61.44，除 2^30=57.220458984375。

建议：无需修改

## T6-F02：支持（严重度：无）

位置：[report.md:24](D:/Code/Project/woYao/evals/runs/final/T6/report.md:24)；台账定位：E1/E5。

原句/原文片段：pgvector v0.8.0的vector值还包含每条8字节开销

核查来源：https://raw.githubusercontent.com/pgvector/pgvector/v0.8.0/README.md 原文 L885–887（本审计 web 实际打开）；独立复算

具体支持段及核对：Vector Type 大小为 4*dimensions+8 字节。20M*(768*4+8)=61600000000，61.60 GB，57.36947059631348 GiB。正文排除了整表及索引开销。

建议：无需修改

## T6-F03：支持（严重度：无）

位置：[report.md:36](D:/Code/Project/woYao/evals/runs/final/T6/report.md:36)；台账定位：E1。

原句/原文片段：**HNSW**通过分层邻居图寻找相近区域；**IVFFlat**先将空间分成若干列表

核查来源：https://raw.githubusercontent.com/pgvector/pgvector/v0.8.0/README.md 原文 HNSW L197–199、IVFFlat 原文 L313–315（本审计 web 实际打开）

具体支持段及核对：HNSW 描述 multilayer graph；IVFFlat 描述将向量分成列表再检索靠近查询的部分列表。正文不把产品名当业务性能测量。

建议：无需修改

## T6-F04：支持（严重度：无）

位置：[report.md:38](D:/Code/Project/woYao/evals/runs/final/T6/report.md:38)；台账定位：E1。

原句/原文片段：SQL里写了WHERE和LIMIT，也不意味着索引先在合格集合上完整找到了k条。

核查来源：https://raw.githubusercontent.com/pgvector/pgvector/v0.8.0/README.md 原文 L420、L442–446

具体支持段及核对：近似索引先扫描后过滤，可能返回不足；候选丢失更近的合格行也不因 LIMIT 条数够而自动恢复，是 ANN 机制的正确推断。

建议：无需修改

## T6-F05：支持（严重度：无）

位置：[report.md:41](D:/Code/Project/woYao/evals/runs/final/T6/report.md:41)；台账定位：E5。

原句/原文片段：平均只留下1条；若目标为10条，按比例反推需要1000个候选

核查来源：独立 Python 运算；正文显式教学假设

具体支持段及核对：100*.01=1，10/.01=1000。只是代表性通过比例下期望计数，正文明确非召回保证；不依赖一个未经测量的数据库参数。

建议：无需修改

## T6-F06：支持（严重度：无）

位置：[report.md:43](D:/Code/Project/woYao/evals/runs/final/T6/report.md:43)；台账定位：E1。

原句/原文片段：pgvector v0.8.0加入迭代索引扫描

核查来源：https://raw.githubusercontent.com/pgvector/pgvector/v0.8.0/README.md 原文 L442–455、L480–497

具体支持段及核对：原文标 Added in 0.8.0，自动多扫直到足够或触达 hnsw.max_scan_tuples / ivfflat.max_probes；strict 只保证结果距离顺序。报告正确没有推成精确全局召回。

建议：无需修改

## T6-F07：支持（严重度：无）

位置：[report.md:45](D:/Code/Project/woYao/evals/runs/final/T6/report.md:45)；台账定位：E2。

原句/原文片段：标准过滤先限制元数据集合，再执行向量搜索；迭代过滤则逐步取向量候选并逐个检查标量条件

核查来源：https://milvus.io/docs/v2.6.x/filtered-search.md 原文 L119–143（本审计 web 实际打开）

具体支持段及核对：Standard filtering 首先筛实体再 ANN；Iterative filtering 逐个候选检验标量条件直到 topK，复杂表达式可能受益但顺序处理也可能变慢。

建议：无需修改

## T6-F08：支持（严重度：无）

位置：[report.md:76](D:/Code/Project/woYao/evals/runs/final/T6/report.md:76)；台账定位：E4。

原句/原文片段：分区剪枝依据分区边界，而不是有无索引

核查来源：https://www.postgresql.org/docs/17/ddl-partitioning.html 原文 L375、L404–405（本审计 web 实际打开）

具体支持段及核对：规划器依据分区键隐含约束证明无法满足 WHERE 才排除分区；不由有无索引驱动，可规划时也可执行时剪枝。

建议：无需修改

## T6-F09：支持（严重度：无）

位置：[report.md:88](D:/Code/Project/woYao/evals/runs/final/T6/report.md:88)；台账定位：E3。

原句/原文片段：Strong、Bounded、Eventual、Session一致性级别，文档的默认值为Bounded。

核查来源：https://milvus.io/docs/v2.6.x/consistency.md 原文 L72、L88–104（本审计 web 实际打开）

具体支持段及核对：四种级别逐项列出，Bounded/Bounded Staleness 为默认；Eventual 与简介 Eventually 用词差异不影响该结论。

建议：无需修改

## T6-F10：支持（严重度：无）

位置：[report.md:88](D:/Code/Project/woYao/evals/runs/final/T6/report.md:88)；台账定位：E3。

原句/原文片段：不能消除PostgreSQL到Milvus之间尚未投递的延迟。

核查来源：https://milvus.io/docs/v2.6.x/consistency.md 原文 L79–91；应用架构推断

具体支持段及核对：Strong 等待 Milvus QueryNode 的 ServiceTime 达到 GuaranteeTs，契约作用于 Milvus 接收的数据流；外部尚未送达的数据无法由内部读一致性制造出来。

建议：无需修改
