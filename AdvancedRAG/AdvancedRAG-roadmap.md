## Naive and Baseline RAG system

![img](https://miro.medium.com/v2/resize:fit:700/0*Ko_ihY8ecAukf2g1.png)



``` python
# very simple RAG pipeline
```



## Advanced RAG methods



### 1. Chunking and Vectorize

#### 1.1 Chunk Size

#### 1.2 Model to Embed chunks

OpenAIEmbedding(ada2) or OpenSource Embedding ([MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard))

##### 1.2.1 Fine-tune Embedding model



### 2. Search Index

#### 2.1 VectorStore Index

A proper search index, optimised for efficient retrieval on 10000+ elements scales is a vector index like faiss, nmslib or annoy, using some Approximate Nearest Neighbours implementation like clustring, trees or HNSW algorithm.

There are also managed solutions like OpenSearch or ElasticSearch and vector databases, taking care of the data ingestion pipeline described in step 1 under the hood, like Pinecone, Weaviate or Chroma.



**you can also store metadata along with vectors** and then use **metadata filters**



#### 2.2 Hierarchical Index

![](https://miro.medium.com/v2/resize:fit:1100/format:webp/0*nDwj0Jgpyk2qc_qJ.png)

**create two indices — one composed of summaries and the other one composed of document chunks**



#### 2.3 Hypothetical Questions and HyDE

Ask an LLM to **generate a question** for each chunk and embed these questions in vectors, at runtime performing query search against this index of question vectors (replacing chunks vectors with questions vectors in our index) and then after retrieval route to original text chunks and send them as the context for the LLM to get an answer.
This approach improves search quality due to a higher semantic similarity between query and hypothetical question compared to what we’d have for an actual chunk.

[**HyDE**](http://boston.lti.cs.cmu.edu/luyug/HyDE/HyDE.pdf) — ask an LLM to **generate a hypothetical response** given the query and then use its vector along with the query vector to enhance search quality.



#### 2.4 Context enrichment

The concept here is to retrieve smaller chunks for better search quality, but add up surrounding context for LLM to reason upon.

##### 2.4.1 Sentence Window Retrieval

![img](https://miro.medium.com/v2/resize:fit:1000/0*JKZ9m_c6jyIKqCWu.png)

##### 2.4.2 Auto-merging Retriever (aka Parent Document Retriever)

![img](https://miro.medium.com/v2/resize:fit:1000/0*x4rMd50GP99OSDuo.png)

#### 2.5 Fusion retrieval or hybrid search

combine keyword-base and semantic-base

then Rerank

![img](https://miro.medium.com/v2/resize:fit:1000/0*0pQbhBEez7U-2knd.png)



### 3. Reranking & filtering

have got retrieval results

In LlamaIndex there is a variety of available `Postprocessors`, filtering out results based on similarity score, keywords, metadata or reranking them with other models like an LLM,
sentence-transformer cross-encoder, Cohere reranking endpoint
or based on metadata like date recency



### 4. Query transformations

User query is not clear.

Query transformations are a family of techniques using an LLM as a reasoning engine to modify user input in order to improve retrieval quality.

[Multi Query Retriever](https://python.langchain.com/docs/modules/data_connection/retrievers/MultiQueryRetriever?ref=blog.langchain.dev) in Langchain and as a [Sub Question Query Engine](https://docs.llamaindex.ai/en/stable/examples/query_engine/sub_question_query_engine.html) in Llamaindex.

- [**Step-back prompting**](https://arxiv.org/pdf/2310.06117.pdf?ref=blog.langchain.dev) **uses LLM to generate a more general query**, retrieving for which we obtain a more general or high-level context useful to ground the answer to our original query on.
- **Query re-writing uses LLM to reformulate initial query** in order to improve retrieval. Both [LangChain](https://github.com/langchain-ai/langchain/blob/master/cookbook/rewrite.ipynb?ref=blog.langchain.dev) and [LlamaIndex](https://llamahub.ai/l/llama_packs-fusion_retriever-query_rewrite) have implementations, tough a bit different, I find LlamaIndex solution being more powerful here.



**Reference citations**

There are a couple of ways to do that:

1. **Insert this referencing task into our prompt** and ask LLM to mention ids of the used sources.
2. **Match the parts of generated response to the original text chunks** in our index — llamaindex offers an efficient [fuzzy matching based solution](https://github.com/run-llama/llama-hub/tree/main/llama_hub/llama_packs/fuzzy_citation) for this case. In case you have not heard of fuzzy matching, this is an [incredibly powerful string matching technique](https://towardsdatascience.com/fuzzy-matching-at-scale-84f2bfd0c536).



### 5. Chat Engine

query compression technique, taking chat context into account



### 6. Query Routing

LLM-powered decision making upon what to do next given the user query



### 7. Agents in RAG

![img](https://miro.medium.com/v2/resize:fit:700/0*FZp2J2NyHHBXPtii.png)



## Evaluation

[Ragas](https://docs.ragas.io/en/latest/index.html), mentioned in the previous section, uses [faithfulness](https://docs.ragas.io/en/latest/concepts/metrics/faithfulness.html) and [answer relevance](https://docs.ragas.io/en/latest/concepts/metrics/answer_relevance.html) as the generated answer quality metrics and classic context [precision](https://docs.ragas.io/en/latest/concepts/metrics/context_precision.html) and [recall](https://docs.ragas.io/en/latest/concepts/metrics/context_recall.html) for the retrieval part of the RAG scheme.

In a recently released great short course [Building and Evaluating Advanced RAG](https://learn.deeplearning.ai/building-evaluating-advanced-rag/) by Andrew NG, LlamaIndex and the evaluation framework [Truelens](https://github.com/truera/trulens/tree/main), they suggest the **RAG triad** — **retrieved context relevance** to the query, **groundedness** (how much the LLM answer is supported by the provided context) and **answer relevance** to the query.

The key and the most controllable metric is the **retrieved context relevance** — basically parts 1–7 of the advanced RAG pipeline described above plus the Encoder and Ranker fine-tuning sections are meant to improve this metric, while part 8 and LLM fine-tuning are focusing on answer relevance and groundedness.