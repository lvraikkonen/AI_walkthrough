## RAG流程中提升性能的方式



### Data Ingestion Phrase

#### 数据清洗 Data Cleaning

在进行后续步骤之前，请确保您的数据满足以下标准：

- **清洁**：至少进行基本的数据清理，这在自然语言处理中非常常见，比如确保所有特殊字符都被正确编码。
- **准确**：确保您的信息是连贯且事实正确的，以免出现相互矛盾的信息，从而混淆大型语言模型。

#### 文档分块 Chunking

文档分块是一种将长文档拆分成小段或将小段信息组合成连贯段落的技术，旨在生成逻辑上连贯、信息丰富的文档片段。

重要的一点是要选择适当的 **分块技术**。例如，在 [LangChain 中，不同的文本分割器](https://python.langchain.com/docs/modules/data_connection/document_transformers/) 使用不同的逻辑来切分文档，如基于字符、Token 等。这种选择取决于您手头的数据类型。比如，处理代码类数据和处理 Markdown 文件时，您需要采用不同的分块策略。

理想的 **分块长度（**`chunk_size`**）** 也因应用场景而异：如果是问答系统，可能需要较短的精确信息块；如果是内容摘要，可能需要较长的信息块。同时，块的大小也需恰到好处：太短可能缺乏足够上下文，太长则可能含有过多无关信息。

此外，还需要在不同块之间考虑设置 **“滚动窗口”（**`overlap`**）**，以便增加额外的上下文信息。

#### 嵌入模型 Embedding Models

尽管通用嵌入模型可以直接使用，但在一些特定场景下，**对嵌入模型进行微调** 更有利于适应特定的使用环境，避免未来出现领域外问题 [9]。LlamaIndex 的实验显示，微调嵌入模型可以在检索效果上提升大约 [5–10%](https://github.com/run-llama/finetune-embedding/blob/main/evaluate.ipynb)

#### 元数据 Metadata

当你在向量数据库中存储向量嵌入时，有些数据库支持你将向量与元数据（或非向量化的数据）一同存储。**给向量嵌入添加元数据标注** 可以在后续的搜索结果处理中发挥重要作用，如进行 **元数据筛选**。比如，你可以加入诸如日期、章节或小节的引用等额外信息。

#### 多重索引 Multi-Indexing

比如，针对不同文档类型采用不同的索引策略。但请注意，这样做需要在数据检索时加入索引路由机制 [1, 9]。如果您对如何利用元数据和分离集合有更深的兴趣，建议您深入了解[原生多租户](https://www.youtube.com/watch?v=KT2RFMTJKGs)这一概念

#### 索引算法 Indexing Algorithm

向量数据库和索引库通常采用近似最近邻 (ANN) 搜索方法，而不是传统的 k-最近邻 (kNN) 搜索。ANN 算法通过近似计算来定位最近邻，因此可能在精确度上稍逊于 kNN 算法。

您可以考虑尝试多种**ANN 算法**，例如 [Facebook Faiss](https://github.com/facebookresearch/faiss) 的聚类算法、[Spotify Annoy](https://github.com/spotify/annoy) 的树状结构算法、[Google ScaNN](https://github.com/google-research/google-research/tree/master/scann) 的向量压缩技术，以及 [HNSWLIB](https://github.com/nmslib/hnswlib) 的邻近图算法。这些算法中许多都提供了可调整的参数，如 HNSW 的 `ef`、`efConstruction` 和 `maxConnections` [1]。

另外，您还可以为这些索引算法启用向量压缩技术。虽然向量压缩可能会牺牲一定的精度，但通过合理选择压缩算法并调整参数，您可以在保证效率的同时最大限度地减小精度损失。

不过，在实际应用中，这些参数通常由专门的研究团队在进行基准测试时调整，而非由 RAG 系统的开发人员设置。



### Reasoning Phrase (Retrieval and Generation)

主要介绍提升检索效果的策略（如[查询转换](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#query-transformations)、[检索参数](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#retrieval-parameters)、[高级检索策略](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#advanced-retrieval-strategies) 以及 [重排序模型](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#re-ranking-models)），因为相比之下，检索部分对整体影响更大。同时，也会简要介绍一些提升生成部分效果的方法



#### 查询转换 Query transformation

在 RAG 管道中，用于检索附加信息的搜索查询也会被嵌入到向量空间里，因此查询的措辞会直接影响搜索结果。所以，如果你发现搜索结果不尽人意，可以尝试以下几种[查询转换方法](https://gpt-index.readthedocs.io/en/v0.6.9/how_to/query/query_transformations.html) [5, 8, 9]，以提升检索效率：

- **重新措辞：** 利用大语言模型 (LLM) 改写你的查询语句，然后再试一次。
- **假设性文档嵌入（HyDE）：** 使用大语言模型 (LLM) 生成一个针对查询的假设性回答，并结合使用以进行检索。
- **子查询：** 将复杂的长查询分解成几个简短的小查询。



#### 检索参数 Retrieval parameters

首先，你需要决定仅使用语义搜索是否足够，或者你是否想尝试更复杂的混合搜索。

在选择混合搜索时，你需要研究如何在稀疏和密集检索方法之间进行有效的权重分配 [1, 4, 9]。这就涉及到调整 **`alpha`** 参数，该参数负责平衡基于语义的搜索（**`alpha = 1`**）和基于关键词的搜索（**`alpha = 0`**）的重要性。



#### 高级检索策略 Advanced retrival strategies

核心理念是：用于检索的数据块不必是用于生成内容的同一数据块。理想情况下，应该嵌入更小的数据块来进行检索（参见 [文档分块](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#chunking)），但同时检索更广泛的上下文。 [7]

- **句子窗口检索：** 在检索时，不只是找到相关的单个句子，而是要获取该句子前后的相关句子。
- **自动合并检索：** 文档按树状结构组织。在查询时，可以把若干个小的、相关的数据块合并成一个更大的上下文。



#### 重排序模型 Re-ranking

虽然语义搜索是根据搜索查询与上下文的语义相似度来进行的，但“最相似”并不总等同于“最相关”。像 [Cohere 的 Rerank](https://cohere.com/rerank?ref=txt.cohere.com&__hstc=14363112.8fc20f6b1a1ad8c0f80dcfed3741d271.1697800567394.1701091033915.1701173515537.7&__hssc=14363112.1.1701173515537&__hsfp=3638092843) 这样的**重排序模型**能够通过为每个检索结果计算与查询相关性的得分，帮助排除不相关的搜索结果 [1, 9]。

> “最相似”不总意味着“最相关”

使用重排序模型时，你可能需要重新调整搜索结果的数量，以及你想要输入到大语言模型 (Large Language Model) 的经过重排序的结果数量。



#### LLMs

LLM 的选择取决于您的具体需求，比如选择开放源代码还是专有模型、考虑推理成本、上下文长度等因素。您可以从众多 LLM 中挑选最适合的。

与处理嵌入模型或重新排序模型时相似，您可能需要**针对特定场景对 LLM 进行微调**，以便更好地融入特定的词汇或语调。



#### 提示工程 Prompt Engineering

一个好的提示词设计能让 LLM 提供更加准确和高质量的回答。

```
请确保您的回答仅基于搜索结果，不要添加任何其他信息！

这一点非常关键！您的回答必须严格基于提供的搜索结果。
并请说明您的回答为何与搜索结果密切相关！
```

在提示词中加入**少样本 (few-shot) 示例**，可以有效提升 LLM 生成内容的质量。

## Summary



在[数据录入阶段](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#ingestion-stage)中介绍了以下策略：

- [数据清洗](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#data-cleaning)：确保数据的清洁和准确性。
- [分块](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#chunking)：选择合适的分块技术、块大小（`chunk_size`）和块之间的重叠（`overlap`）。
- [嵌入模型](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#embedding-models)：选择嵌入模型，包括模型的维度以及是否需要进行微调。
- [元数据](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#metadata)：决定是否使用元数据以及选择哪些元数据。
- [多重索引](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#multi-indexing)：决定是否为不同的数据集合使用多个索引。
- [索引算法](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#indexing-algorithms)：选择和调整近似最近邻 (ANN) 和向量压缩算法，虽然这通常不是实践者所调整的。

在[推理阶段（检索和生成）](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#inferencing-stage)中介绍的策略：

- [查询转换](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#query-transformations)：尝试使用改写、HyDE 或子查询等方式。
- [检索参数](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#retrieval-parameters)：选择搜索技术（如果启用混合搜索，则为 `alpha`）和检索的搜索结果数量。
- [高级检索策略](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#advanced-retrieval-strategies)：决定是否使用高级检索策略，如句子窗口或自动合并检索。
- [重新排序模型](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#re-ranking-models)：是否使用重新排序模型，选择哪种重新排序模型，确定输入到该模型中的搜索结果数量，以及是否对模型进行微调。
- [大语言模型 (LLM)](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#llm)：选择适合的大语言模型并决定是否进行微调。
- [提示工程](https://baoyu.io/translations/rag/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications#prompt-engineering)：尝试使用不同的措辞和少样本示例。

## LangChain相应的实现方式





## Llama-Index实现方式

