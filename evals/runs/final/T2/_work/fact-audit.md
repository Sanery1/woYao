# T2 独立事实抽查

抽查日期：2026-11-26。抽样 10 条不同的关键断言；支持 9，不支持 0，无法核实 1；严重错误 0，轻微错误 0。

范围：仅报告、对应证据台账、共享原文缓存和引用的官方原页；未读取 topics 金标或评分。证据台账用于定位，不能单独证明断言。报告原文未修改。

判定规则：严重错误会导致错误技术判断；轻微错误为局部术语或规范强度不准确。无法核实不算通过，不能由未知反推断言为假。共享缓存保留真实 web 工具原文、URL 和原页面行号；本次额外打开的网页按官方 URL 与具体段落定位。教学数字由独立 Python 标准库运算复算，未用台账复述作为数值证明。

## T2-F01：支持（严重度：无）

位置：[report.md:23](D:/Code/Project/woYao/evals/runs/final/T2/report.md:23)；台账定位：E1。

原句/原文片段：模型不会隔着网络直接执行你的 Python。

核查来源：https://developers.openai.com/api/docs/guides/function-calling；evals/source-cache/agents-details.txt 原文 L2936–2949

具体支持段及核对：示例由应用遍历 tool_calls、解析参数、调用本地分发函数，再追加工具结果；宿主执行边界与报告一致。

建议：无需修改

## T2-F02：支持（严重度：无）

位置：[report.md:41](D:/Code/Project/woYao/evals/runs/final/T2/report.md:41)；台账定位：E1。

原句/原文片段：注意 `arguments` 本身是字符串。

核查来源：https://developers.openai.com/api/docs/guides/function-calling；evals/source-cache/agents-details.txt 原文 L2875–2886、L2940

具体支持段及核对：工具调用样本的 arguments 为 JSON 编码字符串，Python 示例再次 json.loads。

建议：无需修改

## T2-F03：支持（严重度：无）

位置：[report.md:43](D:/Code/Project/woYao/evals/runs/final/T2/report.md:43)；台账定位：E1。

原句/原文片段：先把模型的 `assistant` 消息放回历史，再执行工具

核查来源：https://developers.openai.com/api/docs/guides/function-calling；evals/source-cache/agents-details.txt 原文 L2936–2949

具体支持段及核对：官方示例先追加 completion 的 message，随后遍历调用；工具结果使用对应 tool_call_id。

建议：无需修改

## T2-F04：支持（严重度：无）

位置：[report.md:212](D:/Code/Project/woYao/evals/runs/final/T2/report.md:212)；台账定位：E1/内嵌代码。

原句/原文片段：Python 中 `bool` 是 `int` 的子类

核查来源：独立 Python 运行；报告 §4 内嵌 execute 代码

具体支持段及核对：实测 issubclass(bool,int)=True，type(True) is not int=True。execute 使用 type(unit) is not int / type(qty) is not int，确实拒绝布尔值。

建议：无需修改

## T2-F05：支持（严重度：无）

位置：[report.md:216](D:/Code/Project/woYao/evals/runs/final/T2/report.md:216)；台账定位：E1/内嵌代码。

原句/原文片段：代码先验证整批调用的基本结构及标识唯一，再开始执行

核查来源：报告 §4 内嵌完整代码 run()

具体支持段及核对：第一个 for call in calls 仅验证并收集 ID，len(ids)!=len(set(ids)) 在执行循环之前报错；随后才追加 assistant 并进入 execute 循环。静态核查足以支持流程顺序，不证明原始测试已运行。

建议：无需修改

## T2-F06：支持（严重度：无）

位置：[report.md:242](D:/Code/Project/woYao/evals/runs/final/T2/report.md:242)；台账定位：E1/内嵌代码。

原句/原文片段：`max_turns=6` 让程序最多请求模型六次

核查来源：报告 §4 内嵌 run()

具体支持段及核对：for turn in range(1,max_turns+1) 的每次循环恰调用一次 request_model，耗尽后 RuntimeError；tool_calls 的数量没有被这个参数计数。

建议：无需修改

## T2-F07：支持（严重度：无）

位置：[report.md:244](D:/Code/Project/woYao/evals/runs/final/T2/report.md:244)；台账定位：E1/内嵌代码。

原句/原文片段：本例只有 `quote`，因此模型即使请求 `shell` 也只得到 `unknown_tool`。

核查来源：报告 §4 内嵌 execute()

具体支持段及核对：对通过协议验证且 name 为 shell 的函数请求，首个 fn[name]!=quote 分支直接返回 unknown_tool；不存在动态导入或 eval。

建议：无需修改

## T2-F08：支持（严重度：无）

位置：[report.md:250](D:/Code/Project/woYao/evals/runs/final/T2/report.md:250)；台账定位：E4。

原句/原文片段：你应检查两个报价结果及最终和是否为 4897 分

核查来源：独立 Python 整数运算

具体支持段及核对：1299*3=3897；3897+500*2=4897。报告将其标注示意，没有把模型输出当算术证据。

建议：无需修改

## T2-F09：支持（严重度：无）

位置：[report.md:80](D:/Code/Project/woYao/evals/runs/final/T2/report.md:80)；台账定位：E1。

原句/原文片段：流式工具参数会分片到达，需要先完整拼接

核查来源：https://developers.openai.com/api/docs/guides/function-calling；evals/source-cache/agents-details.txt 原文 L4788–4795、L4852–4860

具体支持段及核对：官方 streaming 样本把同一个参数字符串拆成多个 delta；示例按 index 累积 arguments，支持完整汇总后处理的要求。

建议：无需修改

## T2-F10：无法核实（严重度：待定）

位置：[report.md:230](D:/Code/Project/woYao/evals/runs/final/T2/report.md:230)；台账定位：E2。

原句/原文片段：本次实际输出为 `Ran 5 tests`、`OK`。

核查来源：T2/_work/evidence.md E2；本次授权读取范围

具体支持段及核对：台账仅转述 test_local.out 与测试方法名；共享原文是 API 文档，无法证明一次本地测试运行。按只读 report/evidence/source-cache 的本次范围，未读取日志或重跑测试，故未知而非通过。

建议：由有权读取日志的验证环节核对 test_local.out 或实际重跑 5 个测试；未知不记为事实通过。
