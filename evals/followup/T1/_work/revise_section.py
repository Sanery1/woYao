from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent.parent
report = root / "report.md"
before = (root / "_work" / "report.v1.md").read_bytes()
start = before.index("## 3 ".encode())
end = before.index("## 4 ".encode(), start)
section = r'''## 3 把公式放回四篇文档

现在只算“维修”这个词的贡献，让“手机”暂时留在表外。卡点是：长文多写几次“维修”，加分和长度调整到底谁占上风？把它拆成连续两步，比同时盯着整个公式容易。

第一步，把次数换成“按文章相对长度调整后的次数”。记长度调整量为L=1-b+b|d|/avgdl，则调整后词频是f/L。这里的L不是字数本身：它描述这篇文章相对集合里的典型文章，需要接受多大程度的长度调整。b=0时L恒为1；b为正、文章长于平均值时L大于1，相同的次数除以更大的量，会变小。

第二步，才把f/L送进饱和曲线。把上一节公式的分子、分母同时除以L，可得到同一个词的贡献：

$$
IDF(t)(k_1+1)\frac{f/L}{f/L+k_1}
$$

这不是另换一种算法，只是对原式做代数改写。固定这个词的IDF和k₁后，f/L越大贡献越大，但仍然越加越慢。因此先比较调整后的次数，再看饱和后的贡献，就能把两种影响连起来。〔推断〕

<!-- calc: bm25_joint -->
固定N=4、df=3、avgdl=150，教学参数k₁=1.2、b=0.75，脚本实际输出如下：〔示意〕

| 文档 | 词项长度 | “维修”次数f | 长度调整量L | 调整后次数f/L | “维修”贡献 |
| --- | --- | --- | --- | --- | --- |
| 短指南 | 50 | 1 | 0.5 | 2 | 0.490428 |
| 普通指南 | 150 | 3 | 1 | 3 | 0.560489 |
| 长汇总 | 300 | 3 | 1.75 | 1.714286 | 0.461579 |
| 其他说明 | 100 | 0 | — | 0 | 0 |

先沿普通指南与长汇总这一对看：两篇都出现3次，长汇总的长度是平均值的2倍；b只取0.75，因此L是1.75，而非直接取2。3除以1.75后只剩约1.714份调整后的证据，小于普通指南的3份，贡献随之降低。再比较短指南与长汇总：短指南虽然只出现1次，但它很短，L只有0.5，调整后的次数为2，反而高于长汇总约1.714。所以“次数更多”本身不保证胜出；需要连相对长度一起看。

现在只改长汇总：再加3个“维修”词项，其他三篇保持不变。它的次数从3变6，长度从300变303，全库总长度也增加3，平均长度从150变150.75。这里假定一次更新后立即使用这组准确统计，不模拟具体引擎统计更新时机。〔示意〕

<!-- calc: bm25_joint -->
复算后，L约为1.757463，调整后次数约3.414013，贡献约0.580606。〔示意〕次数增长在这次改写里超过了长度调整的影响，所以贡献上升；但贡献并没有翻倍，因为调整后的次数还会经过饱和曲线。把词重复下去，也不能据此断定一定超过其他文档：另外几篇的相对长度会随平均值改变，完整查询还要加“手机”的贡献。这个单词的局部结果也没有证明内容对用户更有用。〔推断〕

### 一个总分怎样解释

若一篇文章排在前面，可以把总分拆成“手机贡献”和“维修贡献”，逐项追问哪项更大。相同词可以因为词频、相对长度不同而贡献不同；稀有程度则决定这个词整体有多大的区分权重。这里的单词贡献不是完整查询的最终分数，更不是“用户认为相关的概率”。换集合、字段或分析规则后，统计的含义也变了。

若一个查询词完全没在文档里出现，f为零，调整后仍然是零；增加其他词的分数不能替它补一份命中证据。下一节就沿这条线区分：文档根本没进入候选，和已经进来但排得靠后，应怎样分别检查。

'''
# Preserve the original report's CRLF outside and inside the replaced section.
newline = b"\r\n" if b"\r\n" in before else b"\n"
replacement = section.replace("\n", newline.decode()).encode("utf-8")
after = before[:start] + replacement + before[end:]
report.write_bytes(after)
assert before[:start] == after[:start]
assert before[end:] == after[start + len(replacement):]
proof = {
    "before_sha256": hashlib.sha256(before).hexdigest(),
    "after_sha256": hashlib.sha256(after).hexdigest(),
    "prefix_identical": True,
    "suffix_identical": True,
    "prefix_sha256": hashlib.sha256(before[:start]).hexdigest(),
    "suffix_sha256": hashlib.sha256(before[end:]).hexdigest(),
    "target": "section 3 only",
    "retest_goal": "G3 only; original question and answer requirements unchanged",
}
(root / "_work" / "step1-integrity.json").write_text(json.dumps(proof, indent=2), encoding="utf-8")
