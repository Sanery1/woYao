# T5 独立事实抽查

抽查日期：2026-11-26。抽样 10 条不同的关键断言；支持 9，不支持 1，无法核实 0；严重错误 0，轻微错误 1。

范围：仅报告、对应证据台账、共享原文缓存和引用的官方原页；未读取 topics 金标或评分。证据台账用于定位，不能单独证明断言。报告原文未修改。

判定规则：严重错误会导致错误技术判断；轻微错误为局部术语或规范强度不准确。无法核实不算通过，不能由未知反推断言为假。共享缓存保留真实 web 工具原文、URL 和原页面行号；本次额外打开的网页按官方 URL 与具体段落定位。教学数字由独立 Python 标准库运算复算，未用台账复述作为数值证明。

## T5-F01：支持（严重度：无）

位置：[report.md:31](D:/Code/Project/woYao/evals/runs/final/T5/report.md:31)；台账定位：E1。

原句/原文片段：每次新授权都重新准备

核查来源：evals/source-cache/official-details.txt；RFC7636 原文 L381–387

具体支持段及核对：每次授权请求生成高熵密码学随机 code_verifier。报告将其与用户密码、固定安装秘密区分正确。

建议：无需修改

## T5-F02：支持（严重度：无）

位置：[report.md:33](D:/Code/Project/woYao/evals/runs/final/T5/report.md:33)；台账定位：E1。

原句/原文片段：用SHA-256生成摘要后按规定编码

核查来源：evals/source-cache/official-details.txt；RFC7636 原文 L408–414、L510–514

具体支持段及核对：S256 为对 verifier 的 ASCII 字节做 SHA256 再 base64url 编码，正文概述与公式一致。

建议：无需修改

## T5-F03：支持（严重度：无）

位置：[report.md:37](D:/Code/Project/woYao/evals/runs/final/T5/report.md:37)；台账定位：E1。

原句/原文片段：相同才继续其他必要检查并发令牌；对不上则拒绝。

核查来源：evals/source-cache/official-details.txt；RFC7636 原文 L502–523

具体支持段及核对：令牌端按绑定方法计算 challenge 并比较，相等继续常规处理，不等返回 invalid_grant；报告未将 PKCE 成功当作跳过其他检查。

建议：无需修改

## T5-F04：支持（严重度：无）

位置：[report.md:25](D:/Code/Project/woYao/evals/runs/final/T5/report.md:25)；台账定位：E3。

原句/原文片段：某些自定义链接形式可能被多个应用注册

核查来源：evals/source-cache/official-details.txt；RFC8252 原文 L520–530

具体支持段及核对：同机原生应用可能拦截，私有 URI scheme 可被多个应用注册，接收者不确定；与报告攻击条件一致。

建议：无需修改

## T5-F05：支持（严重度：无）

位置：[report.md:63](D:/Code/Project/woYao/evals/runs/final/T5/report.md:63)；台账定位：E1/E4。

原句/原文片段：plain方式，这时挑战值就是验证串本身。

核查来源：evals/source-cache/official-details.txt；RFC7636 原文 L408、L515–518；RFC9700 L255

具体支持段及核对：plain 定义为 verifier 原值；RFC9700 说明能读授权请求的攻击者可破坏暴露 verifier 的方式。

建议：无需修改

## T5-F06：不支持（严重度：轻微）

位置：[report.md:63](D:/Code/Project/woYao/evals/runs/final/T5/report.md:63)；台账定位：E4。

原句/原文片段：2025年RFC 9700要求选择不在授权请求暴露验证串的挑战方式

核查来源：evals/source-cache/official-details.txt；RFC9700 原文 L255

具体支持段及核对：该条规范强度为 SHOULD，正文“要求选择”容易被读成无例外的强制 MUST。原文同时指出 S256 是当时唯一满足条件的方法；建议 S256 的工程结论正确。

建议：将“要求选择”改为“建议（SHOULD）选择”，保留 S256 建议；不要把 SHOULD 写成 MUST。

## T5-F07：支持（严重度：无）

位置：[report.md:75](D:/Code/Project/woYao/evals/runs/final/T5/report.md:75)；台账定位：E5。

原句/原文片段：攻击者同时拿到授权码与对应验证串时，就有了满足这项校验的材料。

核查来源：evals/source-cache/official-details.txt；RFC7636 原文 L502–523；机制推断

具体支持段及核对：PKCE 比对的输入即对应 verifier，持有原值可满足该校验；正文同时强调其他兑换条件仍须成立，没有声称能绕过客户端认证。

建议：无需修改

## T5-F08：支持（严重度：无）

位置：[report.md:77](D:/Code/Project/woYao/evals/runs/final/T5/report.md:77)；台账定位：E4/E5。

原句/原文片段：PKCE已经完成使命，无法在每次日历访问时再次要求验证串。

核查来源：evals/source-cache/official-details.txt；RFC7636 原文 L278–296、L502–523；official-opened.txt RFC9700 目录 L70

具体支持段及核对：RFC7636 机制绑定授权请求与令牌兑换，不定义资源 API 每次访问的 verifier 校验；RFC9700 将令牌重放列为另一个主题。访问令牌的其他约束正文另行保留。

建议：无需修改

## T5-F09：支持（严重度：无）

位置：[report.md:87](D:/Code/Project/woYao/evals/runs/final/T5/report.md:87)；台账定位：E2。

原句/原文片段：回调校验限定授权结果送向哪里，PKCE限定谁能兑换

核查来源：evals/source-cache/official-details.txt；RFC6749 原文 L3049–3052；RFC7636 L502–523

具体支持段及核对：公开客户端必须注册 redirect URI，提供 URI 时必须匹配注册值；PKCE 的另一个校验在 token 端。二者分工的归纳有直接规范依据。

建议：无需修改

## T5-F10：支持（严重度：无）

位置：[report.md:91](D:/Code/Project/woYao/evals/runs/final/T5/report.md:91)；台账定位：E2。

原句/原文片段：应用标识是公开信息，不能拿它当秘密。

核查来源：evals/source-cache/official-details.txt；RFC6749 原文 L792–799、L779–784、L816–830

具体支持段及核对：client identifier 不是秘密且不能单独充当客户端认证；原生安装应用中认证凭据可提取；confidential client 的独立认证契约仍存在。

建议：无需修改
