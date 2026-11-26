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


## E6

- 断言：浏览器代码和凭据交付到用户设备，无法保密时是公开客户端；受控后端是不同部署
- 标签：推断
- 来源：https://www.rfc-editor.org/rfc/rfc6749.html#section-2.1
- 访问日期：2026-11-26
- 版本与定位：RFC6749 §2.1，public及user-agent-based application
- 摘录：credentials are easily accessible
- 用于：§1公开客户端、§4截码成功的其他条件
- 限制：不能把有后端的网站一律叫公开客户端；混淆成本解释为本条部署模型的推断

## E7

- 断言：原生App共享固定秘密可被提取，不应作为可靠的客户端身份凭据
- 标签：官方
- 来源：https://www.rfc-editor.org/rfc/rfc8252.html#section-8.5
- 访问日期：2026-11-26
- 版本与定位：RFC8252 §8.5，Client Authentication
- 摘录：statically included
- 用于：§1
- 限制：不声称设备安全存储对本次验证串没有价值；批量分发固定秘密与短期秘密分开

## E8

- 断言：不暴露验证串的挑战方式是SHOULD，公开客户端PKCE及服务端相关校验是MUST
- 标签：官方
- 来源：https://www.rfc-editor.org/rfc/rfc9700.html#section-2.1.1
- 访问日期：2026-11-26
- 版本与定位：RFC9700 §2.1.1，PKCE挑战方式与客户端/服务端要求
- 摘录：clients SHOULD use PKCE code challenge methods
- 用于：§2规范力度修正
- 限制：保留SHOULD原本力度；本文验收选S256。E4原有断言改按本条理解，不将建议误写强制

## E9

- 断言：PKCE核验本次兑换持有证明，不辨别假授权页；终端受控可破坏验证串保密，已发令牌另行保护
- 标签：推断
- 来源：https://www.rfc-editor.org/rfc/rfc7636.html#section-4.6
- 访问日期：2026-11-26
- 版本与定位：复用E1校验机制并结合E4所述RFC9700 §2.2
- 摘录：见E1，不增加引文
- 用于：§3边界
- 限制：威胁边界的机制推断，不是特定平台渗透测试；无PKCE时仍须满足其余兑换条件
