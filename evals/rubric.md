# 评测规程

## 运行与隔离

1. 在新会话原样发送 topics.yaml 的 prompt；需要补参数时按 reader/purpose/depth 回答，需要确认大纲时回复“直接写”。写作者不读取金标准题和答案。
2. 保存原始报告、工作产物、宿主、Skill 版本和起止时间。宿主不提供 token 时记“未知”。
3. 新版运行 `python scripts/check.py <topic-dir> --json`，保留原始输出。旧版缺新产物导致的 ERROR 单独记录，不能作为旧版内容差的证据。
4. 每个主题做两次独立读者测验；每次读者只接收档位、去掉自测题的报告、五道金标准问题。判分再由独立代理进行，只给问题、答案要点与回答，不给写作过程。读者与判分都用无历史上下文。
5. 每题 2 分：全部命中 2，至少一半要点 1，否则 0；明确“报告未说明”为 0。保存逐题原回答、命中与缺失点、得分与卡点。两次取平均。
6. 抽查每份报告 10 条关键断言（不足 10 条则全部），记录断言、来源、支持/不支持/无法核实、严重程度。让读者做错判断的错误为严重错误。模型测验是代理指标，实际人的理解另行验证。

判分仅说明回答命中哪些要点。低分后协调者回查原文，区分“原文缺口”和“已有解释但读者回答省略”；只拿答案的判分者不得断言报告未写。保留原分数，不以回查补分，不为已有内容再加一遍解释来追分。

## 比较与发布

日常回归 T1、T5；每个阶段记录实际是否重跑，不能把最终结果回填为阶段已通过。依赖阶段中间状态不可运行时明确记“未测”，不能编造分数。

发布前六题全部运行：平均 ≥8/10 且单题主题 ≥7/10、零严重事实错误、零超预算、六份零 ERROR、免责密度 ≤各自对应旧版基线的一半；无对应旧版主题只报告原始密度。至少两个真实宿主跑通 T1。

宿主/时间/token/抽查未执行的项目如实记录，门槛未全过时保留 preview，不合并、不打正式 tag、不发布。检验器成功不能代替来源核对、读者测验或跨宿主验收。

## 金标准复核（2026-11-25）

本题库来自用户施工计划，施工前针对以下答案缩窄过强断言，保留原题意；不得为了正文得分反向修改答案。

- T1：BM25 的排序与召回区分限定为分析器/布尔条件决定的候选集合；带阈值、截断的实际检索管线另论。
- T2：可恢复的参数/工具错误可作为 tool 结果反馈；权限、预算或不可恢复的基础设施错误应停止或升级处理，不能一律吞错。
- T3：checkpoint 无法单独保证外部动作恰好一次；是否至少一次取决于重试、持久化和任务最终恢复的条件。
- T4：题干的“所有前文”限定为普通因果全注意力解码器；滑动窗口/其他注意力结构另论。
- T6：HNSW 与 IVFFlat 取舍以 pgvector v0.8.1 为参考，不能推广为所有数据库所有负载的测量结果。过滤方案按实际版本核对。

已打开的一手来源：

- [Lucene 10.3.1 BM25Similarity](https://lucene.apache.org/core/10_3_1/core/org/apache/lucene/search/similarities/BM25Similarity.html)：参数、IDF。
- [ReAct 原论文](https://arxiv.org/abs/2210.03629)：交错行动与环境反馈；接口细节以实际 API 契约核对。
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)：状态、checkpointer 与恢复。
- [Transformers cache explanation](https://huggingface.co/docs/transformers/main/cache_explanation)：缓存 K/V、当前 Q 与因果注意力。
- [RFC 7636](https://www.rfc-editor.org/rfc/rfc7636)：授权码截获与 PKCE。
- [RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html)：当前 OAuth 安全建议。
- [pgvector v0.8.1](https://github.com/pgvector/pgvector/blob/v0.8.1/README.md)：HNSW、IVFFlat、过滤与迭代扫描。
- [Milvus filtered search](https://milvus.io/docs/filtered-search.md)：standard/iterative filtering；访问时为 v3.0.x，例文须锁定自己的版本。
