# 原版 woYao PKCE 基线：执行记录

- 请求：使用 woYao 研究 OAuth 2.0 的 PKCE，我不写代码，是做产品的，想理解它防的是什么，只要 Markdown。
- Skill：0.19.0-preview.5；读取 git commit d9d8776 的 SKILL.md、research-workflow.md、evidence-policy.md、writing-modes.md、output-contract.md、validation.md。
- 研究日期：2026-11-25。
- 读者假设：不写代码的产品经理，需要理解威胁与验收思路，不需要手写 HTTP 接入。
- 本文是本次按原版生成的基线，未使用新版规划模板、证据标签或字数预算，未读金标准问题。
- 实际操作：使用 web 工具打开六份原始资料，定位规范相关段落；未连接 OAuth 服务，未执行真实授权、攻击或 SDK，未生成 HTML/PDF。

## 问题地图与依据

| 核心问题 | 实际核对位置 | 研究判断 |
| --- | --- | --- |
| 授权码在哪一步可能被截获 | RFC 7636 §1 | 原生应用回跳通道与 TLS 保护的请求通道不同 |
| 为什么共享应用秘密不可靠 | RFC 8252 §8.5；Auth0 native/SPA 说明 | 分发应用里的相同秘密可被用户检查得到 |
| verifier 和 challenge 怎样关联 | RFC 7636 §4.1–4.6 | 每次请求创建随机 verifier，发 challenge，服务端绑定到 code，兑换时再检查 |
| S256 为什么更合适 | RFC 7636 §4.2；RFC 9700 §2.1.1 | plain 暴露原始值，S256 不在授权请求中暴露 verifier |
| 能防什么、留下什么 | RFC 8252 §8.6；RFC 9700 §2.1、§4.9 | PKCE 不能证明应用可信或保护已发放令牌；状态绑定仍要正确实现 |
| 如何验收 | 上述绑定关系的教学推导 | 正常兑换、缺失/错误证明、并行交易交换证明与失败重试；均未实际执行 |

## 实际打开来源

- https://www.rfc-editor.org/rfc/rfc6749.html — 打开文档，正文采用 §4.1 的授权码流程。
- https://www.rfc-editor.org/rfc/rfc7636.html — 打开并 find 定位 §4.1、§4.2、§4.4、§4.6。
- https://www.rfc-editor.org/rfc/rfc8252.html — 打开并 find 定位 §8.5。
- https://www.rfc-editor.org/rfc/rfc9700.html — 打开并 find 定位 §2.1、§2.1.1 及 CSRF 相关段落。
- https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-pkce — 打开全文。
- https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow — 打开全文；页面包含通用授权提示，但主要协议与配置内容可见。

## 自查记录

按原版 validation.md 检查：已解释授权码→令牌主线，再展开固定秘密、交易随机值、S256、攻击结果和产品验收；专有名词就近解释；结尾返回相册 App。本文没有数值算例，无复算脚本。没有执行独立读者测验，也未进行自评分。

执行起止（UTC）：2026-11-25 14:33:35 至 14:36:09，约 154 秒，包含读取原版规则、研究、写作及检查。无宿主 token 计数可用，token 为未知。

机械统计：report.md 去除空白后的全文件字符数 6,342；按施工计划的正则匹配限制措辞 4 处，密度 0.631/千字符。该口径包含 Markdown 链接及参考资料，和纯正文中文计数不同。执行 `git diff --check -- evals/baseline/T5` 无输出（当时文件为未跟踪，故该命令不覆盖新文件本身）。
