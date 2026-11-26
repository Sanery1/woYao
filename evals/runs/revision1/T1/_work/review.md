# 定点修订记录

- 日期：2026-11-26
- 原稿目录：evals/runs/final/T1（保留）
- 修订目录：evals/runs/revision1/T1
- 性质：已观察读者卡点后的定点修订，不是干净独立生成评测；未读取金标topics.yaml、grades或其他评分。
- 依据：原稿reader-1.md、reader-2.md及父任务指定缺口。原五目标题及答案要点未改。
- 变动节：§2.2补饱和目的、k₁及上限；§2.3补相对平均长度；§4补混合候选、分数尺度、RRF和校准/重排取舍；末尾来源与证据边界同步。
- 补证：新增evidence条目记录来源及适用范围。T1打开Elastic RRF；T4核对Transformers v4.57.1；T5打开RFC6749/8252/9700；T6打开pgvector v0.8.0。原证据链保留。

## 实际检查

- python -X utf8 scripts/check.py evals/runs/revision1/T1 --json --reader-copy：exit 0，ERROR=0，WARN=3，字数=3782/6000；输出保存check.json。
- 检查器重新执行已审读的calc并对比同名.out；输入、期望输出及正文原教学数据未改。T5无calc。
- brief、map及已有calc与原稿逐字节相同。
- git diff --no-index --check 原稿report与本稿report：exit 1，无空白错误诊断（内容差异存在）；另运行git diff --check -- evals/runs/revision1无诊断。
- 初次工具读取Python子进程输出时编码不匹配，使用UTF-8模式后成功。初次T4/T5/T6新增台账组合标签被checker报C06，已改为合法单标签“推断”，保留官方依据与推导边界，复查0 ERROR。

## WARN处理

- C11: 开头包含定义句；检查是否先建立了读者问题
- C12: “词项”第 13 行先出现，第 21 行才加粗
- C12: “排序”第 17 行先出现，第 112 行才加粗

C11若出现：原稿先建立售后接口的处境和问题，再给定义，保留有效开头。C12若出现：启发式命中元数据范围或普通用词；正式术语在负责节加粗并就近解释，不为消除告警扩大改写。

## 未测与冻结

本作者不打分、不自评。独立读者及判分由协调代理另做，本稿尚不宣称通过。未运行搜索/混合检索、GPU性能质量测试、OAuth接入或数据库压测；正文保留适用条件和未知。不用旧评分替新稿验收，也未为降低限制密度而删除关键安全或正确性条件。

- report SHA256：e7fe588e68caf29de5ad08e34ac0b248553cad5b506ff7ab38c4278e8bc934e3
- reader-copy SHA256：e5f4490beef5e9b41ca2ed201a9819d062cb54158f4b3bf2c2462d950d51bed9
- 状态：正文冻结，供一次独立复测；后续结果不由本作者预填。
