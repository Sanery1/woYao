# 证据台账

实际通过web打开原页面，搜索摘要未作原文。访问日期统一2026-11-25。

## E1

- 断言：pgvector近似索引后过滤可能返回不足，0.8.0有迭代扫描
- 标签：官方
- 来源：https://github.com/pgvector/pgvector/blob/v0.8.0/README.md
- 访问日期：2026-11-25
- 版本与定位：v0.8.0，Filtering/Iterative Index Scans/Vector Type，行492、510、861
- 摘录：filtering is applied after the index is scanned
- 用于：§1–2、3、5
- 限制：类型大小4*dimensions+8已核对；严格排序不等于精确全局召回

## E2

- 断言：Milvus标准过滤先限制集合；迭代过滤逐个处理向量候选
- 标签：官方
- 来源：https://milvus.io/docs/v2.6.x/filtered-search.md
- 访问日期：2026-11-25
- 版本与定位：v2.6.x，Standard filtering / Iterative filtering，行125、140
- 摘录：Each entity returned by the iterator undergoes scalar filtering
- 用于：§2–3
- 限制：过滤之后ANN仍可能漏近邻

## E3

- 断言：Milvus有多种内部一致性，默认Bounded
- 标签：官方
- 来源：https://milvus.io/docs/v2.6.x/consistency.md
- 访问日期：2026-11-25
- 版本与定位：v2.6.x，Overview/Consistency Levels，行72、91
- 摘录：with Bounded being the default level of consistency used
- 用于：§4
- 限制：内部保证不替代外部同步契约

## E4

- 断言：PG分区剪枝由边界和条件证明驱动
- 标签：官方
- 来源：https://www.postgresql.org/docs/17/ddl-partitioning.html
- 访问日期：2026-11-25
- 版本与定位：PostgreSQL 17，5.12.4，行375、404
- 摘录：partition pruning is driven only by the constraints defined implicitly by the partition keys
- 用于：§3
- 限制：不等于所有时间查询都能剪枝

## E5

- 断言：教学算术与正文表格一致
- 标签：示意
- 来源：本目录calc脚本和同名.out
- 访问日期：2026-11-25
- 版本与定位：Python标准库脚本
- 摘录：详见真实执行的.out，不是数据库或GPU性能实测
- 用于：容量与比例算例
- 限制：构造数据；忽略的开销在正文注明
