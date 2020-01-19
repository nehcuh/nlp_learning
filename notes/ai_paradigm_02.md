# 基于概率的 AI 范式

## 场景描述

有一段文本资料 `export_sql_1558435.zip`, 希望以其包含的文本内容作为数据集，基于 N-gram 模型对输入的词组，或句子进行评价，不同的两句话，哪一句更可能出现。举例而言，“我来自江苏” 和
“江苏来自我”，显然应该是前者更为合理。

## 理论准备

### 1. 自然语言模型

将一段自然语言文本看做一段离散的时间序列，假设一段长度为 $T$ 的文本中的词依次为
$w_1, w_2, \ldots, w_T$, 那么，在离散的时间序列中， $w_t ( 1 \leq t \leq T)$
可看做在时间步 (time step) $t$ 的输出的输出或标签。当给定一个长度为 $T$ 的词序列
$w_1, w_2, \ldots, w_T$ 时，语言模型将计算该序列的概率 $P(w_1, w_2, \ldots, w_T)$.

### 2. 语言模型的计算 -- N-gram 模型

1. 假设序列 $w_1, w_2, \ldots, w_T$ 中每个词是依次生成的，我们有

$$
   P(w_{1}, w_{2}, \ldots, w_{T}) = \prod_{t=1}^{T}P(w_{t}|w_{1}, \ldots, w_{t-1})
$$

2. 一段只有 4 个词的文本，相应的语言模型概率计算如下

$$
   P(w_{1}, w_{2}, w_{3}, w_{4}) = P(w_{1})P(w_{2}|w_{1})P(w_{3}|w_{1}, w_{2})P(w_{4}|w_{1}, w_{2}, w_{3})
$$

3. N-gram 模型: N 元语法通过马尔科夫假设简化了语言模型的计算。马尔科夫假设指一个词的出现只与之前 $n$ 个词相关。 如果是 $N-1$ 阶马尔科夫链假设，相应的语言模型可以改写为

$$
  P(w_{1}, w_{2}, \ldots, w_{T}) \approx \prod_{t=1}^{T}P(w_{t}|w_{t-(n-1)}, \ldots, w_{t-1})
$$

4. **当给定一个文本数据集后，可以根据需要测算的词，或词组短语在该文本数据集中出现的频率，来对该短语的
   概率进行近似估计。**

## 利用 N-gram 模型生成自然语言评分系统

### 1. 数据集

1. 文件描述

- 压缩文件名 `export_sql_1558435.zip`
- 实际 `csv` 文件格式

2. 文件查看

- 直接解压
- `head` 指令 (对于中文文本，编码问题比较难以解决)

### 2. 文件读取

1. 如果是解压后的 csv 文件， `pd.read_csv(sqlResult_1558435.csv, encoding='gb18030)`
2. 为了节省磁盘空间，可以直接读取 `zip` 文件， `pd.read_csv(export_sql_1558435.zip, encoding='gb18030')`
3. 查看文件格式与内容

```python
import pandas as pd

# 读取 zip 文件
df = pd.read_csv(export_sql_1558435.zip, encoding='gb18030'

# 查看文件内容
df.head(3) # dataframe 前三行
df.columns # 列名
df.content.iloc[0]
```

### 3. 文本处理

1. 去除换行符等特殊字符 ==> 使用正则匹配，直接取出词汇 (正则表达式为 `\w+`)
2. 文本拼接 ==> 考虑到效率，使用了 `reduce`, 具体可以参考 !(how to make a flat list out of lists)[https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists]
3. 文本分词 ==> 使用 `jieba` 分词

```python
import re
from functools import reduce
from collections import Counter
import operator

# 1. 去除特殊字符，标点符号等
text = df.content.map(str).str.findall(r"(\w+)").tolist()

# 2. 降维与拼接
text = "".join(reduce(operator.iconcat, text, []))

# 3. 分词处理
words_1g = list(jieba.cut(text))

# 4. 统计
counter = Counter(words_1g)

print(counter.most_common(100))
```

### 4. 可视化

```python
import matplotlib.pyplot as plt

frequencies = [v for k,v in new_text.most_common(100)]
x = [i for i in range(100)]
plt.plot(x, frequencies)
```

!()[words_cnt.png]

### 5. 词组概率计算

1. 单独一个词汇的概率，直接计算相应词汇在语料库中的频率即可，但是这里可能会出现问题，即如果词汇不在语料库中，概率为 0，这里可以使用语料库中总词汇作为分母，用分母倒数作为该词汇的概率估计
2. 连续两个词汇的概率，只需要对 `words_1g` 进行再处理，即将 `words_1g` 中词汇两两配对即可，连续两个词汇可能出现概率太小，导致越界情况出现，这里可以使用对数频率来作为概率的估计
3. 为了简单起见，这里使用了 1-gram 模型，即当前单词概率仅与其之前两个单词有关
4. 最后，为了得到整句话的概率，我们可以使用 `jieba` 对输入的语句进行分词，然后对分词后的结果进行概率
   计算

```python
import math
def prob_single(word):
   """
   单独一个词汇单独概率
   """
   if word in words_1g:
      return -math.log(counter[words_1g[word]] / len(words_1g))
   else:
      return -math.log(1/len(words_1g))

# 连续连个词汇的概率计算
words_2g = ["".join(words_1g[i: i+2]) for i in range(len(words_1g) - 1)]
counter_2g = Counter(words_2g)
def prob_dual(word_1, word_2):
   """
   连续两个词汇出现概率
   """
   if word_1 + word_2 in words_2g:
      return -math.log(counter_2g[word_1 + word_2] / len(words_2g))
   else:
      return -math.log(1 / len(words_2g))

def get_probability(sentence):
   """
   获取 sentence 概率
   """
   words = list(cut(sentence))

   sentence_pro = 0.
   for i, word in enumerate(words[:-1]):
      next_ = words[i+1]
      prob_2_gram = prob_dual(word, next_)
      sentence_pro += prob_2_gram
   return sentence_pro
```

### 6. 测试

从概率计算公式可以看出，如果概率越大，那么返回的计算值越小，因为使用的函数是 `-math.log`, 于是，我们测试几句话，看看那句话更合理

输入：

```python
get_probability("我来自江苏")
```

输出为:

```
28.015696981346238
```

输入:

```python
get_probability("江苏来自我")
```

输出为:

```
32.259418944642945
```
