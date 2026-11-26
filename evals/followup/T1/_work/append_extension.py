from pathlib import Path

root = Path(__file__).resolve().parent.parent
p = root / "report.md"
before = p.read_bytes()
section = r'''## 5 继续深入：标题与正文怎样交给BM25F

前面一直把文章看作一个整体；现在保持“手机维修”这个查询，只把同一文章拆成标题与正文两个**字段**，即可以分别统计的内容部分。标题写“维修”常比正文偶然出现更像主题信号，可直接把两个字段各自的BM25分数相加吗？

**BM25F**把多字段的词项证据先合并，再进行饱和。作者的TREC-2004报告§4.1指出：各字段先对词频做自己的长度调整，按字段重要性加权相加，形成一个“合成词频”，然后送入同一个BM25饱和函数。标题与正文各用本字段的平均长度，不能拿整篇或正文的平均长度去调整标题。〔论文〕[作者报告](https://www.microsoft.com/en-us/research/wp-content/uploads/2004/01/Microsoft-Cambridge-at-TREC-2004-Web-and-HARD-track.pdf)

把第3节的f/L延伸为每个字段的一项即可：对词t，字段j的次数为f_j，长度调整为L_j=1-b_j+b_j|d_j|/avglen_j，权重为w_j；先求x=Σ_j w_j f_j/L_j。再用x替代单字段调整后的次数进入饱和曲线。共同IDF在字段合并后作用于这个词；这里讨论的作者版本并不为每个字段各算一套IDF。

<!-- calc: bm25f_demo -->
设标题和正文恰好都等于各自的平均长度，标题出现“维修”1次、正文2次，标题权重取2、正文取1，则合成词频为4。沿用教学k₁=1.2，并暂把共同IDF放在表外，先合并再饱和的因子约1.692308；把两个已加权词频分别送入饱和函数再相加，则得到2.75。〔示意〕这两个结果不同，原因就是饱和函数不是线性的：同一词分散出现在两个字段，仍是一篇文章的匹配证据，合并后只统一经历一次收益递减。

字段权重和长度调整也承担不同任务。标题权重大，表达“命中标题更值得计入”；标题自己的b_j决定“长标题多出的命中机会要补偿多少”。两者都不能把没有出现的词补出来。后续作者论文也明确每字段有自己的b和词频权重w，并讨论参数增加后的调参问题。〔论文〕[多参数优化论文§3.2](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/optimisation_multiple_parameters.pdf)

在售后知识库里，先检查标题是否可靠、字段缺失怎样处理，再用固定查询及相关性标注比较首屏结果。标题权重更高是可检验的业务假设；分数增大无法证明用户更容易找到答案。本文核对的是历史作者模型与教学算例，未证明某个当前搜索产品的字段查询等同于BM25F，也未运行真实效果实验。〔推断〕

'''
newline = b"\r\n" if b"\r\n" in before else b"\n"
section = section.replace("\n", newline.decode()).encode("utf-8")
assert "## 5 继续深入".encode() not in before
after = before.replace("## 回到开头".encode(), section + "## 回到开头".encode(), 1)
after = after.replace("概率模型完整推导、BM25变体和具体引擎配置".encode(), "概率模型完整推导、其他BM25变体和具体引擎配置".encode())
references = '''
- 〔论文〕[Microsoft Cambridge at TREC–13](https://www.microsoft.com/en-us/research/wp-content/uploads/2004/01/Microsoft-Cambridge-at-TREC-2004-Web-and-HARD-track.pdf)：2004作者报告§4.1，在线修正版，多字段归一化及统一饱和。
- 〔论文〕[Optimisation Methods for Ranking Functions with Multiple Parameters](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/optimisation_multiple_parameters.pdf)：CIKM 2006，§3.2，字段权重和参数。
'''
after += references.replace("\n", newline.decode()).encode("utf-8")
p.write_bytes(after)
