# T3 独立事实抽查

抽查日期：2026-11-26。抽样 10 条不同的关键断言；支持 10，不支持 0，无法核实 0；严重错误 0，轻微错误 0。

范围：仅报告、对应证据台账、共享原文缓存和引用的官方原页；未读取 topics 金标或评分。证据台账用于定位，不能单独证明断言。报告原文未修改。

判定规则：严重错误会导致错误技术判断；轻微错误为局部术语或规范强度不准确。无法核实不算通过，不能由未知反推断言为假。共享缓存保留真实 web 工具原文、URL 和原页面行号；本次额外打开的网页按官方 URL 与具体段落定位。教学数字由独立 Python 标准库运算复算，未用台账复述作为数值证明。

## T3-F01：支持（严重度：无）

位置：[report.md:25](D:/Code/Project/woYao/evals/runs/final/T3/report.md:25)；台账定位：E1。

原句/原文片段：跨 thread 的长期知识则是另一类 store。

核查来源：https://docs.langchain.com/oss/python/langgraph/persistence 原文 L83–86（本审计 web 实际打开）

具体支持段及核对：原文明确 checkpointer 保存 thread 图状态，store 保存图状态外的跨 thread 数据。

建议：无需修改

## T3-F02：支持（严重度：无）

位置：[report.md:112](D:/Code/Project/woYao/evals/runs/final/T3/report.md:112)；台账定位：E2。

原句/原文片段：checkpoint 按 thread 组织，在 **super-step** 边界保存

核查来源：https://docs.langchain.com/oss/python/langgraph/checkpointers 原文 L127、L160–164（本审计 web 实际打开）

具体支持段及核对：原文按 super-step 保存状态，并说明同一 tick 可并行执行节点；单节点 writes 另有保存机制，报告后文已有区分。

建议：无需修改

## T3-F03：支持（严重度：无）

位置：[report.md:116](D:/Code/Project/woYao/evals/runs/final/T3/report.md:116)；台账定位：E2。

原句/原文片段：`graph.invoke(input, config)`、`graph.invoke(None, config)` 和 `graph.invoke(Command(resume=answer), config)`

核查来源：https://docs.langchain.com/oss/python/langgraph/checkpointers 原文 L148–157（本审计 web 实际打开）

具体支持段及核对：入口表分别对应提交新输入、错误后继续、回答 interrupt；仅重用 thread_id 不足以表示恢复。

建议：无需修改

## T3-F04：支持（严重度：无）

位置：[report.md:132](D:/Code/Project/woYao/evals/runs/final/T3/report.md:132)；台账定位：E2。

原句/原文片段：恢复时可避免重跑这些成功节点。

核查来源：https://docs.langchain.com/oss/python/langgraph/checkpointers 原文 L138、L163–164（本审计 web 实际打开）

具体支持段及核对：pending writes 保存同一步其他成功节点输出，失败恢复不重算成功节点；报告正确限于节点级结果。

建议：无需修改

## T3-F05：支持（严重度：无）

位置：[report.md:156](D:/Code/Project/woYao/evals/runs/final/T3/report.md:156)；台账定位：E7。

原句/原文片段：`sync` 在继续下一步前等待 checkpoint 写入；`async` 允许推进与写入重叠；`exit` 仅在图执行成功结束、因错误退出或人工中断退出时持久化。

核查来源：evals/source-cache/agents-durability-determinism.txt；Checkpointers 原文 L332–345

具体支持段及核对：原文三种 durability 模式的提交时点与正文一致；正文没有将 sync 扩为外部订单事务。

建议：无需修改

## T3-F06：支持（严重度：无）

位置：[report.md:160](D:/Code/Project/woYao/evals/runs/final/T3/report.md:160)；台账定位：E7。

原句/原文片段：`sync`会在第一个用户节点前提交输入与初始循环checkpoint。

核查来源：evals/source-cache/agents-durability-determinism.txt；Checkpointers 原文 L346–352

具体支持段及核对：原文 sync 在首个用户节点前提交输入 step -1 与 step 0，async 不等待首写，exit 退出前无 checkpoint；正文保留首次真正落盘前崩溃的边界。

建议：无需修改

## T3-F07：支持（严重度：无）

位置：[report.md:168](D:/Code/Project/woYao/evals/runs/final/T3/report.md:168)；台账定位：E8。

原句/原文片段：必要时根据历史重放，即重新执行编排逻辑、核对已知事件以恢复推进。

核查来源：evals/source-cache/agents-details.txt；Temporal Workflow Execution 原文 L123–129

具体支持段及核对：Replays 段定义恢复推进时校验新生成 Commands 与已有 Event History。

建议：无需修改

## T3-F08：支持（严重度：无）

位置：[report.md:182](D:/Code/Project/woYao/evals/runs/final/T3/report.md:182)；台账定位：E9。

原句/原文片段：已经由历史确认完成的 Activity 可以提供保存结果

核查来源：evals/source-cache/agents-details.txt；Temporal Activity Definition 原文 L263；agents-durability-determinism.txt Workflow Definition L315–320

具体支持段及核对：完成 Activity 不在 Workflow Replay 重执行，Workflow 获取历史保存结果；未完成确认的 Activity 仍可能重试，正文随后明确说明。

建议：无需修改

## T3-F09：支持（严重度：无）

位置：[report.md:210](D:/Code/Project/woYao/evals/runs/final/T3/report.md:210)；台账定位：E4。

原句/原文片段：外部 I/O、模型推理和现实随机性，放在合适的 Activity 或受支持的记录机制中。

核查来源：evals/source-cache/agents-durability-determinism.txt；Temporal Workflow Definition 原文 L280–307

具体支持段及核对：原文将 API、LLM、数据库等非确定操作放 Activity；兼容命令序列是重放确定性边界。报告也承认框架提供专门时间或随机 API。

建议：无需修改

## T3-F10：支持（严重度：无）

位置：[report.md:270](D:/Code/Project/woYao/evals/runs/final/T3/report.md:270)；台账定位：E10。

原句/原文片段：中断后的节点可能从节点开头重新执行

核查来源：evals/source-cache/agents-details.txt；Interrupts 原文 L833–840

具体支持段及核对：原文说明 interrupt 通过重跑所在节点实现，中断前副作用应幂等或拆节点；批准后的副作用也有失败重试风险。

建议：无需修改
