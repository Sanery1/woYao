# T1 独立事实抽查

抽查日期：2026-11-26。抽样 10 条不同的关键断言；支持 10，不支持 0，无法核实 0；严重错误 0，轻微错误 0。

范围：仅报告、对应证据台账、共享原文缓存和引用的官方原页；未读取 topics 金标或评分。证据台账用于定位，不能单独证明断言。报告原文未修改。

判定规则：严重错误会导致错误技术判断；轻微错误为局部术语或规范强度不准确。无法核实不算通过，不能由未知反推断言为假。共享缓存保留真实 web 工具原文、URL 和原页面行号；本次额外打开的网页按官方 URL 与具体段落定位。教学数字由独立 Python 标准库运算复算，未用台账复述作为数值证明。

## T1-F01：支持（严重度：无）

位置：[report.md:21](D:/Code/Project/woYao/evals/runs/final/T1/report.md:21)；台账定位：E2。

原句/原文片段：这里假定“手机维修”被切成“手机”和“维修”。

核查来源：evals/source-cache/official-opened.txt；Elastic Standard analyzer 原文 L15–31

具体支持段及核对：原文说明分析器依照 Unicode 文本切分产生词项；中文具体切分在报告中明示为教学假设，不作为实测。

建议：无需修改

## T1-F02：支持（严重度：无）

位置：[report.md:25](D:/Code/Project/woYao/evals/runs/final/T1/report.md:25)；台账定位：E3。

原句/原文片段：普通text字段查询会先分析

核查来源：evals/source-cache/official-opened.txt；Elastic match query 原文 L16、L43

具体支持段及核对：原文规定提供的文本匹配前分析，text 字段匹配分析后的 tokens。

建议：无需修改

## T1-F03：支持（严重度：无）

位置：[report.md:59](D:/Code/Project/woYao/evals/runs/final/T1/report.md:59)；台账定位：E1。

原句/原文片段：IDF(t)=\ln\left(1+\frac{N-df(t)+0.5}{df(t)+0.5}\right)

核查来源：evals/source-cache/official-opened.txt；Lucene 10.3.1 BM25Similarity 原文 L74–76

具体支持段及核对：idf 方法说明的对数表达式与正文相同；API 使用 docCount 与 docFreq。正文讨论教学四文档集合。

建议：无需修改

## T1-F04：支持（严重度：无）

位置：[report.md:63](D:/Code/Project/woYao/evals/runs/final/T1/report.md:63)；台账定位：E5。

原句/原文片段：“维修”的df是3，得到IDF约0.356675；“手机”的df是4，得到约0.105361。

核查来源：独立 Python 标准库 math 复算；本审计工具输出

具体支持段及核对：ln(1+1.5/3.5)=0.3566749439387324；ln(1+0.5/4.5)=0.10536051565782635，六位小数一致。

建议：无需修改

## T1-F05：支持（严重度：无）

位置：[report.md:72](D:/Code/Project/woYao/evals/runs/final/T1/report.md:72)；台账定位：E5。

原句/原文片段：词频从1变到2时，词频因子从1变成1.375；变到10时约1.964286；变到100时约2.173913。

核查来源：独立 Python math 复算；正文显式教学公式

具体支持段及核对：固定 k1=1.2、长度比=1，计算 f*2.2/(f+1.2) 得 1、1.375、1.9642857142857144、2.173913043478261；极限 2.2。

建议：无需修改

## T1-F06：支持（严重度：无）

位置：[report.md:74](D:/Code/Project/woYao/evals/runs/final/T1/report.md:74)；台账定位：E4。

原句/原文片段：k₁较大通常让饱和来得更慢

核查来源：evals/source-cache/bm25-mechanism.txt；Elastic BM25 原文 L153–156

具体支持段及核对：原文将 k1 解释为词频饱和参数，较大 k1 使重复出现仍有较大的边际贡献；与教学固定长度机制一致。

建议：无需修改

## T1-F07：支持（严重度：无）

位置：[report.md:80](D:/Code/Project/woYao/evals/runs/final/T1/report.md:80)；台账定位：E4。

原句/原文片段：b=0意味着长度因素退出计算；b=1意味着在这一项里完全使用相对长度比。

核查来源：evals/source-cache/bm25-mechanism.txt 原文 L149；正文公式代数

具体支持段及核对：原文说明 b=0 消除长度比影响。将 b=0、1 分别代入正文 1-b+b|d|/avgdl，得到 1 和 |d|/avgdl。

建议：无需修改

## T1-F08：支持（严重度：无）

位置：[report.md:91](D:/Code/Project/woYao/evals/runs/final/T1/report.md:91)；台账定位：E5。

原句/原文片段：| 短指南 | 50 | 1 | 0.490428 |

核查来源：独立 Python math 复算；正文四行贡献表

具体支持段及核对：以 N=4、df=3、avgdl=150、k1=1.2、b=.75 重算四行：0.49042804791575706、0.5604891976180081、0.46157933921483024、0；与全部表格行一致。

建议：无需修改

## T1-F09：支持（严重度：无）

位置：[report.md:106](D:/Code/Project/woYao/evals/runs/final/T1/report.md:106)；台账定位：E6。

原句/原文片段：当某个查询词没有在文档里出现，它的词频为零，在这里贡献就是零

核查来源：正文显式教学公式；独立复算

具体支持段及核对：令 f=0，分子为 0，示例参数的分母为正，贡献为 0；该局部推断未声称查询结构等同于评分函数。

建议：无需修改

## T1-F10：支持（严重度：无）

位置：[report.md:116](D:/Code/Project/woYao/evals/runs/final/T1/report.md:116)；台账定位：E1。

原句/原文片段：Lucene 10.3.1文档列出k₁=1.2、b=0.75的默认值

核查来源：evals/source-cache/official-opened.txt；Lucene 10.3.1 原文 L32、L36

具体支持段及核对：两个构造函数说明均列出相同默认值；正文已将教学公式与具体引擎全部评分细节分开。

建议：无需修改
