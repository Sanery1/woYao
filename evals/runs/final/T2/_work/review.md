# 复核记录

## 过程与版本

先固定五项能力目标于 goals.md，然后成文。最初误读安装目录0.19，后读取工作仓库的0.20.0-preview.1及必要references/templates，并据当前版补齐front matter、map题面、台账、calc、图与自测。题面正式格式化晚于正文的偏差保留在map，没有伪装为完全按时完成，也没有降低原目标。

## 实际验证

- Python 3.14.0。
- `python -m unittest -v test_local`：5个测试方法通过，工具错误含5个子场景；实际HTTP mock往返。
- `python scripts/check.py evals/runs/final/T2 --json --reader-copy`：首次0 ERROR；正文3357字（后续微调后以最终check结果为准）。
- calc quote 的两个值与正文一致；3897分、4897分均为教学算术，不是模型实测。
- 未调用用户API、付费服务或真实provider。

## 机械WARN处理

- C12首次Agent出现与加粗不一致：已将定义移到首次正文位置。
- C18一手来源1，低于参考4：核心接口来自单一官方协议；网络补读失败，不用无关来源凑数。关键段仍需补核，已在证据边界披露。

最终机械检查：`python -X utf8 scripts/check.py evals/runs/final/T2 --json --reader-copy`，0 ERROR、1 WARN，3385字；唯一WARN为来源参考数。最新reader-copy.md已生成，旧副本保存在reader-copy.initial.md。

修改测试隔离环境以避免继承真实密钥后再次执行`python -X utf8 -m unittest -v test_local`：5个方法全部通过，4.622秒。未改Agent行为，正文嵌入代码仍与agent.py一致。`git diff --check -- evals/runs/final/T2 evals/runs/final/T3`退出0；目录是新增文件，该命令不替代新增内容复核。

## 内容顺读复核

正文先建立谁执行，再看消息状态变化，再到完整实现。代码中的arguments二次解析、先整批协议检查、逐调用回传、正常stop检查和预算均有因果解释。多调用变式与删除assistant消息的反例用于检验关联理解。此为作者内容复核，不计独立读者成绩。

## 独立测验

状态：pending，由主代理另行安排无历史读者与判分代理。不得以本文件的作者复核替代真实测试分。最新副本将在最终check后生成；尚无原始回答、分数或通过结论。

## 证据未完成项

初次官方函数调用页关键段访问失败；主代理后定向取得并共享agents-details.txt，已读2936–2949及2875–2886行，补核arguments解析、assistant消息保存与tool_call_id关联，台账已更新。此缺口已解决；真实provider验证仍未执行。

## 冻结状态

2026-11-25补证后冻结：正文3377字，`python -X utf8 scripts/check.py evals/runs/final/T2 --json --reader-copy`为0 ERROR、1 WARN，仅保留单一官方协议来源少于参考数量的WARN，理由如前。旧副本归档为reader-copy.before-source-verification.md，最新reader-copy.md已从当前正文生成。`git diff --check`退出0。独立读者状态仍为pending，交主代理执行。

因为误读旧安装版及题面后补，该轮归类为集成试跑，不视作完全干净的新版发布评测；保留原过程记录。
