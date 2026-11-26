# 复核记录

## 过程与版本

五项能力目标先固定于goals.md；误读安装目录0.19后，改读当前仓库0.20.0-preview.1及必要references/templates，再按当前版补齐工作文件。题面正式格式化晚于正文的偏差保留于map，未通过降低难度追求过测。

## 实际验证

- `python scripts/check.py evals/runs/final/T3 --json --reader-copy`：首次0 ERROR，正文9739字（微调后以最终check结果为准）。
- 本文仅官方资料研究与教学推导，没有执行LangGraph/Temporal、订单接口、集群或故障注入实验。
- 3000元是案例直接给定常数，没有产品性能或成本计算，不需要calc；公式是教学关系式。

## 机械WARN处理

- C12 checkpoint先出现：同句较早的checkpointer包含checkpoint子串，后面的checkpoint同时给出加粗与定义；这是字符串检查误判，保留易读表述。
- C18一手来源5，低于参考8：已有官方页面覆盖主要契约；额外URL与关键段读取因网络失败，未伪造已读来源。来源数量低于参考的限制如实保留。

最终机械检查：`python -X utf8 scripts/check.py evals/runs/final/T3 --json --reader-copy`，0 ERROR、2 WARN，9739字；WARN为上述子串误判与来源参考数。最新reader-copy.md已生成，旧副本保存在reader-copy.initial.md。`git diff --check -- evals/runs/final/T2 evals/runs/final/T3`退出0；目录为新增文件，命令不替代新增文件的内容复核。

## 内容顺读复核

先走完整订单崩溃，再推导恢复信息和提交窗口，随后分别解释两框架，再连接业务幂等、人审、并发、升级与验证。案例稳定使用purchase-42/quote-v1/order-900。核心反例保留：保存前执行可重复、保存后执行可漏执行；远端不支持幂等时保留未知；重放不是重试。此为作者复核，不替代独立读者测验。

## 独立测验

状态：pending，由主代理安排独立无历史读者和另一个判分代理；未自评分，尚无原始回答、分数或通过结论。最新reader-copy将在最终check后生成。

## 证据未完成项

初次LangGraph durability、Temporal replay/确定性/版本段补读遇connection/SSL/transport失败。主代理后实际定向打开并共享agents-details.txt与agents-durability-determinism.txt，本代理已阅读并补齐E4/E7–E10：durability332–352、确定性280–307、Activity参数315–321、升级322–395、replay123–129、Activity幂等256–280、interrupt833–840。原缺口已解决。正文修正exit的成功/错误/人工中断退出语义，补首个checkpoint前无记录窗口，新增目标服务去重与长审批后重查外部事实。

## 冻结状态

2026-11-25补证后冻结：正文9988字、8条一手来源，`python -X utf8 scripts/check.py evals/runs/final/T3 --json --reader-copy`为0 ERROR、1 WARN，仅保留同句checkpointer/checkpoint子串误判。旧副本归档为reader-copy.before-source-verification.md，最新reader-copy.md已从当前正文生成。`git diff --check`退出0。独立读者状态仍为pending，交主代理执行。

因为误读旧安装版及题面后补，该轮归类为集成试跑，不视作完全干净的新版发布评测；保留原过程记录。
