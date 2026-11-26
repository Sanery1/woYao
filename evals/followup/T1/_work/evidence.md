# 证据台账

获取链：本代理web连接失败，升级PowerShell/curl后仍TLS失败。协调代理2026-11-25实际打开官方页面，原始工具输出共享到evals/source-cache/official-opened.txt和official-details.txt，本代理读取原文片段核查。未把本代理访问失败描述为直接网页访问成功。每来源摘录总量少于25英文词。

## E1

- 断言：Lucene10.3.1列出k1与b及默认值，IDF采用非负对数式，平均字段长度由词项统计计算
- 标签：官方
- 来源：https://lucene.apache.org/core/10_3_1/core/org/apache/lucene/search/similarities/BM25Similarity.html
- 访问日期：2026-11-25
- 版本与定位：Lucene10.3.1 BM25Similarity, idf(), avgFieldLength(), constructors
- 摘录：log(1 + (docCount - docFreq + 0.5)/(docFreq + 0.5))
- 用于：§2
- 限制：只证明API说明；本文计算是显式教学公式，不声称复现引擎所有数值细节

## E2

- 断言：分析器把输入拆成词项，分词配置影响检索对象
- 标签：官方
- 来源：https://www.elastic.co/docs/reference/text-analysis/analysis-standard-analyzer
- 访问日期：2026-11-25
- 版本与定位：Elastic滚动文档，Standard analyzer介绍及输出例子
- 摘录：It provides grammar based tokenization
- 用于：§1、§4
- 限制：未执行中文分析器；例中中文切分为明确教学假设

## E3

- 断言：match在搜索前先分析文本，普通text字段按分析后的词项匹配
- 标签：官方
- 来源：https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-match-query
- 访问日期：2026-11-25
- 版本与定位：Elastic滚动文档，Parameters与analyzer
- 摘录：The provided text is analyzed before matching.
- 用于：§1、§4
- 限制：仅讨论text词项检索；semantic_text另走语义检索，未把此结论扩到全部字段

## E4

- 断言：k1决定词频饱和特性，b调节字段长度对分数的影响
- 标签：官方
- 来源：https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables
- 访问日期：2026-11-25
- 版本与定位：Elastic官方算法讲解，2018-04-19，参数解释段；历史算法说明，不作为当前产品全部实现的契约
- 摘录：k1 is a variable which helps determine term frequency saturation characteristics.
- 用于：§2、§3
- 限制：协调代理补充实际打开的原文，evals/source-cache/bm25-mechanism.txt；教学公式数值仍与具体Lucene实现区分

## E5

- 断言：四文档平均长度150；维修df=3时IDF及各词频、长度贡献如正文
- 标签：示意
- 来源：_work/calc/bm25_demo.py与同名.out
- 访问日期：2026-11-25
- 版本与定位：Python标准库math；本任务自编脚本实际执行，UTF-8保存输出
- 摘录：short: tf=1, length=50, contribution=0.490428
- 用于：§2、§3
- 限制：构造数据复算；没有引擎性能或真实相关性实验。固定长度曲线只观察单一变量，不表示同一短文可无限重复。

## E6

- 断言：基础词项匹配缺乏共享词项时，调评分参数无法补充词汇关系；候选与排序需分开调试
- 标签：推断
- 来源：https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-match-query
- 访问日期：2026-11-25
- 版本与定位：text词项匹配契约及本文显式公式
- 摘录：见E3，不追加原文摘录
- 用于：§4
- 限制：排除同义词展开、模糊查询或其他额外候选机制后成立；实际产品必须检查查询结构。

## E7

- 断言：第3节将原式等价改写为以f/L输入饱和曲线；追加3个查询词时，tf、长度、平均长度共同变化，教学贡献为0.580606。
- 标签：示意
- 来源：_work/calc/bm25_joint.py与同名.out；E1与E4中的公式说明
- 访问日期：2026-11-26
- 版本与定位：Python标准库math；本次实际运行；第3节表格与联动例子
- 摘录：long_plus_3_matches: tf=6, length=303, avgdl=150.75, ratio=2.009950, L=1.757463, effective_tf=3.414013, score=0.580606
- 用于：§3
- 限制：教学构造，不是引擎效果实验；统计即时更新是例子的明确假设。

## E8

- 断言：BM25F按各字段平均长度做归一化，加权词频先合并，再进入统一饱和函数；IDF不按字段单独计算。
- 标签：论文
- 来源：https://www.microsoft.com/en-us/research/wp-content/uploads/2004/01/Microsoft-Cambridge-at-TREC-2004-Web-and-HARD-track.pdf
- 访问日期：2026-11-26
- 版本与定位：Microsoft Cambridge at TREC–13: Web and HARD tracks，2004，在线修正版，PDF第5页§4.1；web实际打开后find返回行344–437，脚注说明印刷版公式错误已修正
- 摘录：which is then used in the usual BM25 saturating function
- 用于：§5
- 限制：历史作者模型，非当前产品契约；摘录11英文词，未使用搜索摘要作证据。

## E9

- 断言：BM25F每个字段有独立的长度参数b与词频权重w；参数更多需要评估调优。
- 标签：论文
- 来源：https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/optimisation_multiple_parameters.pdf
- 访问日期：2026-11-26
- 版本与定位：Optimisation Methods for Ranking Functions with Multiple Parameters，CIKM 2006，PDF第5页§3.2；web实际open/find行480–497，关于过拟合见行120–129
- 摘录：Each field has its own b and its own term-frequency weight w.
- 用于：§5
- 限制：作者模型，不把论文的检索效果迁移为本次知识库收益；摘录13英文词。

## E10

- 断言：先合并词频再饱和与各自饱和后相加不同，教学因子1.692308与2.75。
- 标签：示意
- 来源：_work/calc/bm25f_demo.py与同名.out
- 访问日期：2026-11-26
- 版本与定位：本次自编Python标准库脚本实际运行；统一省略共同IDF，用前文带(k1+1)的教学尺度
- 摘录：combine_then_saturate=1.692308
- 用于：§5
- 限制：用于展示非线性，不是引擎数值复现或效果比较。
