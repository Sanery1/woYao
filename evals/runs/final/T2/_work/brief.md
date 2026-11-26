---
topic: "Python 与 OpenAI 兼容接口最小工具 Agent"
slug: "T2"
date: "2026-11-25"
skill_version: "0.20.0-preview.1"
reader: B
reader_profile: "会 Python，未写过 Agent"
purpose: 动手实现
depth: 标准
budget_chars: 6000
sources: 联网
formats: Markdown
---

## 用户原话

使用woYao带我用Python和OpenAI兼容接口实现最小能调用工具的Agent循环，我会Python没写过Agent，B/动手实现/标准/只要Markdown，直接写。

## 范围

- 包含：标准库 HTTP 客户端、工具 schema、分发验证、消息历史、多调用、错误与预算、本地 mock 验证。
- 旁支：框架、向量库、生产部署、持久化、写操作、多 Agent、付费或真实 provider 调用。

## 已知背景与约束

已明确参数并授权直接写，不再次确认。工作环境 Python 3.14.0、Windows PowerShell；代码采用 Python 3.10+ 语法，其他 Python 版本未实测。原先误读安装目录 0.19，后改读当前仓库 0.20 并据此修订；最终版本标识对应实际用于复核、交付的当前版。五项目标先固定于 goals.md，后按同一能力写成 G1–G5；不读取 evals 题库或其他报告。主代理取得并共享实际原文后，已补核工具字段。该过程作为集成试跑，不归为完全干净的新版发布评测。
