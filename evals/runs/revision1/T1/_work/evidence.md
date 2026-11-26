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

- 断言：词项与向量独立取候选后可按名次融合；RRF不直接比较原始分数
- 标签：官方
- 来源：https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion
- 访问日期：2026-11-26
- 版本与定位：Elastic滚动文档，RRF公式、kNN与standard示例
- 摘录：the different relevance indicators do not have to be related to each other
- 用于：§4混合检索
- 限制：只核实公式与候选融合；归一化加权和重排为方案推断，未实测

## E8

- 断言：本文公式的单词贡献极限为IDF(t)×(k1+1)，k1为零时正词频因子为1；长度以集合平均值为参照
- 标签：推断
- 来源：https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables
- 访问日期：2026-11-26
- 版本与定位：复用E4已读官方片段与本文显式公式代数推导
- 摘录：见E4，不增加引文
- 用于：§2.2、§2.3
- 限制：固定其他量观察函数，不把理论极限当成真实引擎总分
