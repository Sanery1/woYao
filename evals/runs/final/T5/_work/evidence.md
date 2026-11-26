# 证据台账

获取链：本代理web连接失败、PowerShell/curl经升级仍TLS失败；协调代理2026-11-25实际打开官方页面，原始工具输出共享到evals/source-cache/official-opened.txt及official-details.txt。本代理读取上述原文片段核对，下列摘录来自该原文；并非声称本代理直接网页访问。每来源总摘录少于25英文词。

## E1

- 断言：授权请求保留挑战值，兑换提交验证串并比较；每次请求生成随机串
- 标签：官方
- 来源：https://www.rfc-editor.org/rfc/rfc7636.html
- 访问日期：2026-11-25
- 版本与定位：RFC7636 §1.1、§3、§4.1–4.6
- 摘录：A cryptographically random string that is used to correlate the authorization request to the token request.
- 用于：§1–§3
- 限制：仅约束兑换绑定，不代替其他授权校验

## E2

- 断言：OAuth提供有限访问，客户端类型与标识性质不同，回调需校验
- 标签：官方
- 来源：https://www.rfc-editor.org/rfc/rfc6749.html
- 访问日期：2026-11-25
- 版本与定位：RFC6749 Abstract、§2、§10.6
- 摘录：The client identifier is not a secret
- 用于：§1、§4
- 限制：基础规范需连同RFC9700理解

## E3

- 断言：原生应用回调可被同机应用截获，PKCE保护兑换；回环有专门传输规则
- 标签：官方
- 来源：https://www.rfc-editor.org/rfc/rfc8252.html
- 访问日期：2026-11-25
- 版本与定位：RFC8252 §8.1、§8.3
- 摘录：code interception by a different native app running on the same device may be possible.
- 用于：§1、§3、§4
- 限制：只说明原生应用威胁和特定回环，不豁免远程HTTPS

## E4

- 断言：S256不在授权请求暴露验证串，服务器必须落实校验及降级保护
- 标签：官方
- 来源：https://www.rfc-editor.org/rfc/rfc9700.html
- 访问日期：2026-11-25
- 版本与定位：RFC9700 §2.1.1；§2.2标题
- 摘录：Authorization servers MUST support PKCE
- 用于：§2–§4
- 限制：本次共享片段含2.1.1细节；2.2仅作为独立令牌保护议题的结构证据

## E5

- 断言：泄露原始验证串会破坏PKCE门槛；验收应测试缺失/错误验证串被拒绝
- 标签：推断
- 来源：https://www.rfc-editor.org/rfc/rfc7636.html
- 访问日期：2026-11-25
- 版本与定位：§4.6，依据E1的校验条件推出，不增加原文摘录
- 摘录：见E1；本条不追加引文
- 用于：§3、§4
- 限制：没有实际执行任何平台测试；能否兑换仍受其他条件限制
