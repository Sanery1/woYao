# 证据台账

## E1

- 断言：工具调用中模型表达请求，应用执行工具并回传结果；实现采用Chat Completions方言。
- 标签：官方
- 来源：https://developers.openai.com/api/docs/guides/function-calling
- 访问日期：2026-11-25
- 版本与定位：在线文档；Chat Completions示例2936–2949行及2875–2886行；主代理实际打开的原始返回共享于evals/source-cache/agents-details.txt，本代理已逐段阅读。
- 摘录：`args = json.loads(tool_call.function.arguments)`；`"tool_call_id": tool_call.id`
- 用于：§1–2、§4、参考来源
- 限制：本代理初次打开仅取得导航，后续网络补读失败；后经主代理定向获取并共享原文，已核对arguments字符串解析、保存assistant请求及按ID回传tool结果。兼容provider自身支持情况仍待实测。

## E2

- 断言：本次标准库HTTP mock的5个测试方法通过；覆盖正常、双调用、5类工具错误、预算、重复ID。
- 标签：实测
- 来源：本目录 agent.py、test_local.py；_work/test_local.out
- 访问日期：2026-11-25
- 版本与定位：Python 3.14.0；python -m unittest -v test_local
- 摘录：Ran 5 tests；OK
- 用于：§5、证据边界
- 限制：脚本响应不是模型，不证明provider兼容、语义理解或最终答复准确。

## E3

- 断言：未指定的兼容provider支持哪些字段、模型能否正确完成任务，仍需具体服务文档与实测。
- 标签：未知
- 来源：https://developers.openai.com/api/docs/guides/function-calling
- 访问日期：2026-11-25
- 版本与定位：OpenAI基础协议已补核，第三方provider尚未指定和调用。
- 摘录：未取得特定provider原文（本任务没有选定provider）。
- 用于：§3、证据边界
- 限制：不能把OpenAI协议与本地mock验证泛化为任意兼容provider可用。

## E4

- 断言：报价3897分及双商品总和4897分是教学算术值。
- 标签：示意
- 来源：_work/calc/quote.py、_work/calc/quote.out
- 访问日期：2026-11-25
- 版本与定位：Python标准库整数运算。
- 摘录：1299 * 3 = 3897 cents；3897 + 500 * 2 = 4897 cents
- 用于：§1/§2/§5/§7、自测
- 限制：教学复算，不是模型或provider性能结果。
