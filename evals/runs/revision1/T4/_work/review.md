# 定点修订记录

- 日期：2026-11-26
- 原稿目录：evals/runs/final/T4（保留）
- 修订目录：evals/runs/revision1/T4
- 性质：已观察读者卡点后的定点修订，不是干净独立生成评测；未读取金标topics.yaml、grades或其他评分。
- 依据：原稿reader-1.md、reader-2.md及父任务指定缺口。原五目标题及答案要点未改。
- 变动节：§1补历史Q不再被下一步使用；§4将缩短上下文/并发、GQA、量化、分页、前缀和迁移对应T/H/S、计算、分配与设备容量。
- 补证：新增evidence条目记录来源及适用范围。T1打开Elastic RRF；T4核对Transformers v4.57.1；T5打开RFC6749/8252/9700；T6打开pgvector v0.8.0。原证据链保留。

## 实际检查

- python -X utf8 scripts/check.py evals/runs/revision1/T4 --json --reader-copy：exit 0，ERROR=0，WARN=0，字数=3432/6000；输出保存check.json。
- 检查器重新执行已审读的calc并对比同名.out；输入、期望输出及正文原教学数据未改。T5无calc。
- brief、map及已有calc与原稿逐字节相同。
- git diff --no-index --check 原稿report与本稿report：exit 1，无空白错误诊断（内容差异存在）；另运行git diff --check -- evals/runs/revision1无诊断。
- 初次工具读取Python子进程输出时编码不匹配，使用UTF-8模式后成功。初次T4/T5/T6新增台账组合标签被checker报C06，已改为合法单标签“推断”，保留官方依据与推导边界，复查0 ERROR。

## WARN处理

- 无WARN。

C11若出现：原稿先建立售后接口的处境和问题，再给定义，保留有效开头。C12若出现：启发式命中元数据范围或普通用词；正式术语在负责节加粗并就近解释，不为消除告警扩大改写。

## 未测与冻结

本作者不打分、不自评。独立读者及判分由协调代理另做，本稿尚不宣称通过。未运行搜索/混合检索、GPU性能质量测试、OAuth接入或数据库压测；正文保留适用条件和未知。不用旧评分替新稿验收，也未为降低限制密度而删除关键安全或正确性条件。

- report SHA256：74e9a6a2c269717eb2b4411dd686f778d8e41c796445e5772a67d1ef4d4a5447
- reader-copy SHA256：9ec7a2028ac7af95cc0b40f826f0d9645b1be01f9a27cc484abaea7ee0e53699
- 状态：正文冻结，供一次独立复测；后续结果不由本作者预填。
