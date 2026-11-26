# T4 独立事实抽查

抽查日期：2026-11-26。抽样 10 条不同的关键断言；支持 10，不支持 0，无法核实 0；严重错误 0，轻微错误 0。

范围：仅报告、对应证据台账、共享原文缓存和引用的官方原页；未读取 topics 金标或评分。证据台账用于定位，不能单独证明断言。报告原文未修改。

判定规则：严重错误会导致错误技术判断；轻微错误为局部术语或规范强度不准确。无法核实不算通过，不能由未知反推断言为假。共享缓存保留真实 web 工具原文、URL 和原页面行号；本次额外打开的网页按官方 URL 与具体段落定位。教学数字由独立 Python 标准库运算复算，未用台账复述作为数值证明。

## T4-F01：支持（严重度：无）

位置：[report.md:23](D:/Code/Project/woYao/evals/runs/final/T4/report.md:23)；台账定位：E1。

原句/原文片段：当前token产生 **Q（查询向量）**

核查来源：https://huggingface.co/docs/transformers/v4.57.1/en/cache_explanation 原文 L118–126（本审计 web 实际打开）

具体支持段及核对：注意力公式由 QK 转置计算权重，再乘 V；Q/K/V 是输入表示的投影。报告的查询、匹配和加权汇集说明是可接受的教学解释。

建议：无需修改

## T4-F02：支持（严重度：无）

位置：[report.md:25](D:/Code/Project/woYao/evals/runs/final/T4/report.md:25)；台账定位：E1。

原句/原文片段：后面新生成一个词不会反过来改变旧位置的K、V。

核查来源：https://huggingface.co/docs/transformers/v4.57.1/en/cache_explanation 原文 L122–127

具体支持段及核对：因果掩码阻止访问未来 token，旧 token 表示不随未来 token 改变，历史 K/V 可缓存；报告限定模型、前缀和位置等条件相同。

建议：无需修改

## T4-F03：支持（严重度：无）

位置：[report.md:27](D:/Code/Project/woYao/evals/runs/final/T4/report.md:27)；台账定位：E1。

原句/原文片段：对历史的读取和注意力计算仍然存在。

核查来源：https://huggingface.co/docs/transformers/v4.57.1/en/cache_explanation 原文 L123–127

具体支持段及核对：增量注意力显式读取缓存的 k1..kt-1 和 v1..vt-1，仍计算当前 q_t 的注意力；复用 KV 不消除此项工作。

建议：无需修改

## T4-F04：支持（严重度：无）

位置：[report.md:51](D:/Code/Project/woYao/evals/runs/final/T4/report.md:51)；台账定位：E1/E6。

原句/原文片段：KV字节数 ≈ 2 × L × H × D × S × T。

核查来源：https://huggingface.co/docs/transformers/v4.57.1/en/cache_explanation 原文 L122–127；独立张量计数推导

具体支持段及核对：每层 K、V 两份，形状按请求、KV头、token、头维度计数；对全注意力、无共享、等配置各层可相乘。GQA 按 KV 头计数。报告已排除滑窗、混合架构及管理开销。

建议：无需修改

## T4-F05：支持（严重度：无）

位置：[report.md:56](D:/Code/Project/woYao/evals/runs/final/T4/report.md:56)；台账定位：E6。

原句/原文片段：每个缓存token占128 KiB。一条请求保留8192个token时，KV数据为1 GiB；32条同样长度的活跃请求就是32 GiB。

核查来源：独立 Python 整数运算

具体支持段及核对：2*32*8*128*2=131072 字节/token=128 KiB；乘 8192 为 2^30 字节；再乘 32 为 32 GiB。

建议：无需修改

## T4-F06：支持（严重度：无）

位置：[report.md:63](D:/Code/Project/woYao/evals/runs/final/T4/report.md:63)；台账定位：E6。

原句/原文片段：两项同时翻倍，缓存数据变成原来的四倍。

核查来源：独立乘法推导与正文表格

具体支持段及核对：固定每 token 大小，长度 8192→16384、活跃请求 32→64，总 token 数乘四，32 GiB→128 GiB；无共享等前提正文明确。

建议：无需修改

## T4-F07：支持（严重度：无）

位置：[report.md:53](D:/Code/Project/woYao/evals/runs/final/T4/report.md:53)；台账定位：E2。

原句/原文片段：**GQA（分组查询注意力）**允许多个查询头共用一组KV头

核查来源：https://arxiv.org/abs/2305.13245 原文摘要 L16–17（本审计 web 实际打开）

具体支持段及核对：v3 摘要规定 KV 头数多于 1 且少于查询头，区别 MQA 单 KV 头。共享使需存的 KV 头少于查询头；不是随意修改既有模型服务参数。

建议：无需修改

## T4-F08：支持（严重度：无）

位置：[report.md:80](D:/Code/Project/woYao/evals/runs/final/T4/report.md:80)；台账定位：E3。

原句/原文片段：它改善物理分配效率，不会凭空减小每个逻辑token的KV。

核查来源：https://arxiv.org/abs/2309.06180 原文摘要 L16–17（本审计 web 实际打开）

具体支持段及核对：论文定位动态 KV 的碎片和冗余复制浪费，并采用操作系统分页式管理与共享。报告未移植论文吞吐数字；物理管理不改变单份 KV 数值维度是机制推断。

建议：无需修改

## T4-F09：支持（严重度：无）

位置：[report.md:84](D:/Code/Project/woYao/evals/runs/final/T4/report.md:84)；台账定位：E4。

原句/原文片段：vLLM文档明确把收益限定在预填充

核查来源：https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/ 原文 L568–570、L576–577（本审计 web 实际打开）

具体支持段及核对：latest Limits 明确 APC 减少 prefill 而非 decode；相同历史 token 的前缀可复用，新增 token 仍生成。报告正确保留动态版本边界。

建议：无需修改

## T4-F10：支持（严重度：无）

位置：[report.md:86](D:/Code/Project/woYao/evals/runs/final/T4/report.md:86)；台账定位：E5。

原句/原文片段：短上下文且显存充足时，量化缓存可能损害延迟。

核查来源：https://huggingface.co/docs/transformers/v4.57.1/en/kv_cache 原文 L217–224（本审计 web 实际打开）

具体支持段及核对：量化缓存节以更低精度降低内存需求，并明确该上下文/显存条件下延迟可能变差。

建议：无需修改
