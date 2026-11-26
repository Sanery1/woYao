---
topic: "Agent 工作流持久化执行 checkpoint 与崩溃恢复"
slug: "T3"
date: "2026-11-25"
skill_version: "0.20.0-preview.1"
reader: B
reader_profile: "会后端开发，不熟悉持久化 Agent 工作流"
purpose: 理解原理
depth: 完整
budget_chars: 15000
sources: 联网
formats: Markdown
---

## 用户原话

使用woYao研究Agent工作流持久化执行checkpoint和崩溃恢复，参考LangGraph/Temporal，B会后端/理解原理/完整/只要Markdown，直接写。

## 范围

- 包含：恢复信息、保存边界、LangGraph thread/checkpoint/super-step、Temporal历史/replay/Activity、幂等、未知结果、人审、并发、升级、验证。
- 旁支：集群部署、跨云容量压测、性能结论、价格、未经检查的复杂框架代码。

## 已知背景与约束

已明确参数并授权直接写。只研究和教学推导，没有运行框架或故障注入实验。最初误读安装版0.19，后读取当前仓库0.20并修订；固定五项能力目标保存在 goals.md，正式题干后补而不降低能力范围。外部文档后续关键段网络失败，由主代理定向取得并共享真实原文，补核已完成且台账记录来源定位。不读取题库、其他报告或金标。该过程作为集成试跑，不归为完全干净的新版发布评测。
