# 证据台账

实际通过web打开原页面，搜索摘要未作原文。访问日期统一2026-11-25。

## E1

- 断言：历史K/V可复用，当前查询仍读取历史
- 标签：官方
- 来源：https://huggingface.co/docs/transformers/v4.57.1/en/cache_explanation
- 访问日期：2026-11-25
- 版本与定位：v4.57.1，Attention matrices；访问行122–124
- 摘录：the mask prevents the model from attending to future tokens
- 用于：§1–2
- 限制：普通因果注意力，不泛化所有架构

## E2

- 断言：GQA的KV头数介于MQA和MHA之间
- 标签：论文
- 来源：https://arxiv.org/abs/2305.13245
- 访问日期：2026-11-25
- 版本与定位：arXiv:2305.13245v3，摘要；2023-12-23
- 摘录：uses an intermediate (more than one, less than number of query heads) number of key-value heads
- 用于：§2
- 限制：采用结构定义，不外推论文质量速度

## E3

- 断言：分页旨在缓解碎片与重复复制的缓存浪费
- 标签：论文
- 来源：https://arxiv.org/abs/2309.06180
- 访问日期：2026-11-25
- 版本与定位：arXiv:2309.06180v1，摘要；2023-09-12
- 摘录：wasted by fragmentation and redundant duplication
- 用于：§4
- 限制：不将论文吞吐倍数当本次测量

## E4

- 断言：前缀缓存节省预填充而非新token解码时间
- 标签：官方
- 来源：https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/
- 访问日期：2026-11-25
- 版本与定位：latest访问快照，Limits，行577
- 摘录：does not reduce the time of generating new tokens
- 用于：§4
- 限制：动态文档，未锁定服务安装版本

## E5

- 断言：KV量化降低保存精度，但可能损害短上下文延迟
- 标签：官方
- 来源：https://huggingface.co/docs/transformers/v4.57.1/en/kv_cache
- 访问日期：2026-11-25
- 版本与定位：v4.57.1，Quantized cache，行219–223
- 摘录：Quantizing the cache can harm latency
- 用于：§4
- 限制：实际支持后端、质量与速度需测

## E6

- 断言：教学算术与正文表格一致
- 标签：示意
- 来源：本目录calc脚本和同名.out
- 访问日期：2026-11-25
- 版本与定位：Python标准库脚本
- 摘录：详见真实执行的.out，不是数据库或GPU性能实测
- 用于：容量与比例算例
- 限制：构造数据；忽略的开销在正文注明


## E7

- 断言：常规因果解码只需新位置的查询，不复用历史Q；减少T/H/S与分页、前缀和迁移节省不同预算
- 标签：推断
- 来源：https://huggingface.co/docs/transformers/v4.57.1/en/cache_explanation
- 访问日期：2026-11-26
- 版本与定位：v4.57.1，Attention matrices，最后token查询与追加KV段
- 摘录：you only need the last token’s query
- 用于：§1、§4
- 限制：预算分解由正文公式及E2–E5推出；前缀物理共享须由部署实现确认，没有GPU性能或质量测量
