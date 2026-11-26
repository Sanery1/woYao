# 证据台账

## E1

- 断言：LangGraph区分thread级状态checkpointer与跨thread数据store。
- 标签：官方
- 来源：https://docs.langchain.com/oss/python/langgraph/persistence
- 访问日期：2026-11-25
- 版本与定位：在线文档；Persistence，83–86行、Checkpointer vs store表。
- 摘录：Checkpointers persist a thread’s graph state as checkpoints.
- 用于：§1/§6
- 限制：说明产品契约，不证明InMemorySaver进程退出后仍可用；后者按内存生命周期推导。

## E2

- 断言：checkpoint按super-step保存并组织到thread；同一步中成功节点pending writes在恢复时可复用。
- 标签：官方
- 来源：https://docs.langchain.com/oss/python/langgraph/checkpointers
- 访问日期：2026-11-25
- 版本与定位：在线文档，127行与137–157行，Why use checkpointers与Choose how to continue a thread。
- 摘录：A checkpointer saves a snapshot of graph state at each super-step, organized into threads.
- 用于：§5/§11
- 限制：pending writes不等于保存失败节点内部任意执行位置。已读入口表明确区分input、None、Command；interrupt节点从头执行。

## E3

- 断言：节点重试可重跑整个节点，不能使外部副作用自动恰好一次。
- 标签：官方
- 来源：https://docs.langchain.com/oss/python/langgraph/fault-tolerance
- 访问日期：2026-11-25
- 版本与定位：在线文档，Retry boundaries and idempotency，214行。
- 摘录：A retry re-runs the entire node function from the start.
- 用于：§2/§4/§10
- 限制：页面注明节点超时与节点级错误处理需langgraph>=1.2；不把该版本条件泛化到全部功能。

## E4

- 断言：Temporal区分Workflow定义和实际Workflow Execution；重放要求兼容的命令序列，不可把普通外部模型I/O直接放在重放路径；代码升级应考虑历史兼容。
- 标签：官方
- 来源：https://docs.temporal.io/workflow-definition
- 访问日期：2026-11-25
- 版本与定位：在线文档，272行、Deterministic constraints 280–307、Changing Activity arguments 315–321、Code changes 322–340、Versioning 384–395。关键段由主代理定向打开并共享agents-durability-determinism.txt，本代理已实际阅读。
- 摘录：A Workflow Execution effectively executes once to completion；same Workflow API calls in the same sequence
- 用于：§7/§8/§12
- 限制：命令序列兼容不等于所有变量和参数永远不变；已完成Activity结果会复用。未运行SDK，不能据此宣称任意升级可接管旧历史。

## E5

- 断言：Activity Execution由服务管理生命周期和重试，Workflow Activity结果闭合后送回Workflow并记录相关历史事件。
- 标签：官方
- 来源：https://docs.temporal.io/activity-execution
- 访问日期：2026-11-25
- 版本与定位：在线文档，87–94行。
- 摘录：Each step is recorded in the Workflow Execution's Event History.
- 用于：§7
- 限制：其生命周期管理不等于外部订单服务的业务去重。

## E6

- 断言：案例时间线、状态结构、简化事件、幂等协议和故障注入方案属于教学构造与通用分布式系统推导。
- 标签：示意
- 来源：本报告§2–4/§7–13；无外部实测。
- 访问日期：2026-11-25
- 版本与定位：教学示意，不是框架内部数据结构。
- 摘录：purchase-42；quote-v1；order-900。
- 用于：贯穿案例、公式、表格、伪代码。
- 限制：没有运行框架、订单服务、故障测试或性能比较。

## E7

- 断言：sync在下一步前提交，async与下一步重叠，exit在成功/错误/人工中断退出时提交；新thread首个checkpoint尚未耐久时可完全无记录。
- 标签：官方
- 来源：https://docs.langchain.com/oss/python/langgraph/checkpointers
- 访问日期：2026-11-25
- 版本与定位：Durability modes 332–352行；主代理实际打开并共享agents-durability-determinism.txt，本代理已读原始片段。
- 摘录：before the next step starts
- 用于：§6。
- 限制：同步checkpoint不涵盖外部订单服务事务；未对安装版本或后端配置实测。先前本代理网络失败的补核缺口已由共享原文解决。

## E8

- 断言：Temporal通过replay恢复推进，生成的命令会与现有事件历史核对。
- 标签：官方
- 来源：https://docs.temporal.io/workflow-execution
- 访问日期：2026-11-25
- 版本与定位：Replays，123–129行；共享原文agents-details.txt。
- 摘录：Commands that are generated are checked against an existing Event History.
- 用于：§7/§8/§9。
- 限制：重放编排不代表未确认Activity不重试，更不代表外部效果自动只发生一次。

## E9

- 断言：已完成Activity不因Workflow重放再执行；未报告完成时可重试；业务幂等键由被调用服务执行。
- 标签：官方
- 来源：https://docs.temporal.io/activity-definition
- 访问日期：2026-11-25
- 版本与定位：Idempotency，256–280行；共享原文agents-details.txt。
- 摘录：completed Activities will not re-execute as part of a Workflow Replay
- 用于：§7/§8/§10。
- 限制：Activity本身不会替远端服务实现去重；节点粒度与历史大小存在取舍，不给出未经实测的性能比较。

## E10

- 断言：interrupt恢复可重跑所在节点；中断前副作用应幂等或拆节点，长等待后需重查外部事实。
- 标签：官方
- 来源：https://docs.langchain.com/oss/python/langgraph/interrupts
- 访问日期：2026-11-25
- 版本与定位：Side effects called before interrupt must be idempotent，833–840行；共享原文agents-details.txt。
- 摘录：Separate side effects into separate nodes when possible
- 用于：§11。
- 限制：把副作用放到批准后只解决批准门禁，后续节点失败重试仍可重复效果。
