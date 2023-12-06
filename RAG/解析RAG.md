![Deconstructing RAG](https://blog.langchain.dev/content/images/size/w1000/2023/11/blog_figure-1.jpg)

## RAG 快速开始



创建一个RAG应用的主要流程如下流程：

![](D:\OneDrive\文档\AI\RAG_flow.png)



入门的代码也很简单：

``` python
# Load docs
from langchain.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
data = loader.load()

# Split
from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 0)
all_splits = text_splitter.split_documents(data)

# Store splits
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())

# RAG prompt
from langchain import hub
prompt = hub.pull("rlm/rag-prompt")

# LLM
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

# RetrievalQA
qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vectorstore.as_retriever(),
    chain_type_kwargs={"prompt": prompt}
)
question = "What are the approaches to Task Decomposition?"
result = qa_chain({"query": question})
result["result"]
```

Typically, RAG systems involve: a question (often from a user) that determines what information to retrieve, a process of retrieving that information from a data source (or sources), and a process of passing the retrieved information directly to the LLM as part of the prompt

RAG 总体上分为两个部分：

- Retrieve
- Generation



## RAG的一些挑战以及应对办法



### 1. Query Transformation

A first question to ask when thinking about RAG: *how can we make retrieval robust to variability in user input?* For example, user questions may be poorly worded for the challenging task of retrieval.



查询转换可以使用的一些常见方法：

#### Query Expansion 查询扩展

Query expansion decomposes the input into sub-questions, each of which is a more narrow retrieval challenge. The m[ulti-query retriever](https://python.langchain.com/docs/modules/data_connection/retrievers/MultiQueryRetriever?ref=blog.langchain.dev) performs sub-question generation, retrieval, and returns the unique union of the retrieved docs. [RAG fusion](https://github.com/langchain-ai/langchain/blob/master/cookbook/rag_fusion.ipynb?ref=blog.langchain.dev) builds on by ranking of the returned docs from each of the sub-questions. [Step-back prompting](https://github.com/langchain-ai/langchain/blob/master/cookbook/stepback-qa.ipynb?ref=blog.langchain.dev) offers a third approach in this vein, generating a step-back question to ground an answer synthesis in higher-level concepts or principles (see [paper](https://arxiv.org/pdf/2310.06117.pdf?ref=blog.langchain.dev)). For example, a question about physics can be stepped-back into a question (and LLM-generated answer) about the physical principles behind the user query. 

#### Query re-writing 查询重写

In some RAG applications, such as [WebLang](https://blog.langchain.dev/weblangchain/) (our open source research assistant), a user question follows a broader chat conversation. In order to properly answer the question, the full conversational context may be required. To address this, we use [this prompt](https://smith.langchain.com/hub/langchain-ai/weblangchain-search-query?ref=blog.langchain.dev&organizationId=1fa8b1f4-fcb9-4072-9aa9-983e35ad61b8) to compress chat history into a final question for retrieval.

#### Query compression 查询压缩

In some RAG applications, such as [WebLang](https://blog.langchain.dev/weblangchain/) (our open source research assistant), a user question follows a broader chat conversation. In order to properly answer the question, the full conversational context may be required. To address this, we use [this prompt](https://smith.langchain.com/hub/langchain-ai/weblangchain-search-query?ref=blog.langchain.dev&organizationId=1fa8b1f4-fcb9-4072-9aa9-983e35ad61b8) to compress chat history into a final question for retrieval.



### 2. Routing 查询路由

A second question to ask when thinking about RAG: *where does the data live?* In many RAG demos, data lives in a single vectorstore but this is often not the case in production settings. When operating across a set of various datastores, incoming queries need to be routed. LLMs can be used to support dynamic query routing effectively (see [here](https://python.langchain.com/docs/expression_language/how_to/routing?ref=blog.langchain.dev)), as discussed in our recent review of OpenAI's [RAG strategies](https://blog.langchain.dev/applying-openai-rag/).



### 3. Query Construction 查询创建

A third question to ask when thinking about RAG: *what syntax is needed to query the data?* While routed questions are in natural language, data is stored in sources such as relational or graph databases that require specific syntax to retrieve. And even vectorstores utilize structured metadata for filtering. In all cases, natural language from the query needs to be converted into a query syntax for retrieval.

#### Text-To-SQL

Text-to-SQL can be done easily ([here](https://python.langchain.com/docs/expression_language/cookbook/sql_db?ref=blog.langchain.dev)) by providing an LLM the natural language question along with relevant table information; open source LLMs have proven effective at this task, enabling data privacy

#### Text-to-Cypher

While vector stores readily handle unstructured data, they don't understand the relationships between vectors. While SQL databases can model relationships, schema changes can be disruptive and costly. **Knowledge graphs** can address these challenges by modeling the relationships between data and extending the types of relationships without a major overhaul. They are desirable for data that has many-to-many relationships or hierarchies that are difficult to represent in tabular form.

#### Text-to-metadata filters

Vectorstores equipped with [metadata filtering](https://docs.trychroma.com/usage-guide?ref=blog.langchain.dev#filtering-by-metadata) enable structured queries to filter embedded unstructured documents. The [self-query retriever](https://python.langchain.com/docs/modules/data_connection/retrievers/self_query/?ref=blog.langchain.dev#constructing-from-scratch-with-lcel) can translate natural language into these structured queries with metadata filters using a specification for the metadata fields present in the vectorstore 



### 4. Indexing 构建索引

A fourth question to ask when thinking about RAG: *how to design my index?* For vectorstores, there is considerable opportunity to tune parameters like the **chunk size** and / or the **document embedding strategy** to support variable data types.



#### **Chunk size**

In our review of OpenAI's [RAG strategies](https://blog.langchain.dev/applying-openai-rag/), we highlight the notable boost in performance that they saw simply from experimenting with the chunk size during document embedding. This makes sense, because chunk size controls how much information we load into the context window (or "RAM" in our LLM OS analogy).



#### **Document embedding strategy**

One of the simplest and most useful ideas in index design is to decouple what you embed (for retrieval) from what you pass to the LLM (for answer synthesis). For example, consider a large passage of text with lots of redundant detail. We can embed a few different representations of this to improve retrieval, such as a *summary* or *small chunks to narrow the scope of information that is embedded*. In either case, we can then retrieve the *full text* to pass to the LLM. These can be implemented using [multi-vector](https://blog.langchain.dev/semi-structured-multi-modal-rag/) and [parent-document](https://python.langchain.com/docs/modules/data_connection/retrievers/parent_document_retriever?ref=blog.langchain.dev) retriever, respectively.

The multi-vector retriever also works well for semi-structured documents that contain a mix of text and tables 



### Post-Processing 后置处理

A final question to ask when thinking about RAG: *how to combine the documents that I have retrieved?* This is important, because the context window has limited size and redundant documents (e.g., from different sources) will utilize tokens without providing unique information to the LLM. A number of approaches for document post-processing (e.g., to improve diversity or filter for recency) have emerged, some of which we discuss in our blog post on OpenAI's [RAG strategies](https://blog.langchain.dev/applying-openai-rag/).



#### Re-Ranking 重排序

The Cohere ReRank endpoint can be used for document compression (reduce redundancy) in cases where we are retrieving a large number of documents. Relatedly, RAG-fusion uses reciprocal rank fusion (see blog and implementation) to ReRank documents returned from a retriever (similar to multi-query).

#### Classification
OpenAI classified each retrieved document based upon its content and then chose a different prompt depending on that classification. This marries tagging of text for classification with logical routing (in this case, for the prompt) based on a tag.



## Benchmark for LLM/RAG

评估体系与提升改进

### Ragas

![evol-generate](https://docs.ragas.io/en/latest/_static/imgs/component-wise-metrics.png)

### TruLens

![TruLens Feednacl Functions](https://www.trulens.org/img/trulens-feedback-functions.png)

- Truthfulness
- Question answering relevance
- Harmful or toxic language
- User sentiment
- Language mismatch
- Response verbosity
- Fairness and bias
- Or other custom feedback functions you provide

#### 使用TruLens评估LLM App的一般步骤



1. Build your LLM app 生成Base LLM App

   ``` python
   chain = LLMChain(llm=llm, prompt=prompt, memory=memory, verbose=True)
   ```

   

2. 将LLM App和TruLens连接，并记录输入和响应

   The next step is to instrument the app with TruLens to log inputs and responses from the chain.

   ``` python
   chain_recorder = TruChain(chain, chain_id="Chain-Ver1")
   
   # run the chain
   answer, record = chain_recorder.call_with_record(question)
   # log the interaction
   tru.add_record(record, ...)
   ```

3. 使用Feedback函数来评估并记录App的质量数据

   ``` python
   # Run feedback functions
   feedbacks = tru.run_feedback_functions(record, [
       Feedback(hugs.language_match).on(text1="prompt", text2="response"),
       Feedback(openai.relevance).on(...),
       Feedback(openai.qs_relevance).on(...)
   ])
   
   # log feedbacks
   tru.add_feedbacks(feedbacks)
   ```

   

4. 在Dashboard中查看性能数据



5. 迭代过程获取最佳性能的app



## LangChain vs Llama-index



### Retrieval-Augmented Generation

Retrieval-Augmented Generation (or RAG) is an architecture used to help large language models like GPT-4 provide better responses by using relevant information from additional sources and reducing the chances that an LLM will leak sensitive data, or ‘hallucinate’ incorrect or misleading information.

### Vector Embeddings

Vector Embeddings are numerical vector representations of data. They are not only limited to text but can also represent images, videos, and other types of data. They are usually created using an embedding model such as OpenAI's `text-embedding-ada-002` ([see here for more information](https://platform.openai.com/docs/guides/embeddings/what-are-embeddings))

### LangChain vs. LlamaIndex

Let me start off by saying that it's not either LangChain or LlamaIndex. As you mentioned in your question, both tools can be used together to enhance your RAG application.

### LangChain

You can think of LangChain as a framework rather than a tool. It provides a lot of tools right out of the box that enable you to interact with LLMs. Key LangChain components include [chains](https://docs.langchain.com/docs/components/chains/). Chains allow the *chaining* of components together, meaning you could use a `PromptTemplate` and a `LLMChain` to:

1. Create a prompt
2. Query a LLM

Here's a quick example:

``` python
prompt = PromptTemplate(template=template, input_variables=["questions"])

chain = LLMChain(
    llm=llm,
    prompt=prompt
)

chain.run(query)
```

You can read more about LangChain [components here](https://docs.langchain.com/docs/category/components).

### LlamaIndex

LlamaIndex, (previously known as GPT Index), is a data framework specifically designed for LLM apps. Its primary focus is on ingesting, structuring, and accessing private or domain-specific data. It offers a set of tools that facilitate the integration of custom data into LLMs.

Based on my experience with LlamaIndex, it is an ideal solution if you're looking to work with vector embeddings. Using its [many available plugins](https://llamahub.ai/) you could load (or ingest) data from many sources easily, and generate vector embeddings using an embedding model.

One key feature of LlamaIndex is that it is optimized for index querying. After the data is ingested, an index is created. This `index` represents your vectorized data and can be easily queried like so:

``` python
query_engine = index.as_query_engine()
response = query_engine.query("Stackoverflow is Awesome.")
```

LlamaIndex abstracts this but it is essentially taking your query `"Stackoverflow is Awesome."` and comparing it with the most relevant information from your vectorized data (or `index`) which is then provided as context to the LLM.



### Compare LangChain vs. Llama-Index

### Framework summary

| **Feature**                                  | **LlamaIndex**                                               | **LangChain**                                                |
| -------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Primary focus**                            | Intelligent search and data indexing and retrieval           | Building a wide range of Gen AI applications                 |
| **Data handling**                            | Ingesting, structuring, and accessing private or domain-specific data | Loading, processing, and indexing data for various uses      |
| **Customization**                            | Offers tools for integrating private data into LLMs          | Highly customizable, it allows users to chain multiple tools and components |
| **Flexibility**                              | Specialized for efficient and fast search                    | General-purpose framework with more flexibility in application behavior |
| **Supported LLMs** **(As of December 2023)** | Connects to any LLM provider like OpenAI, Antropic, HuggingFace, and AI21 | Support for over 60 LLMs, including popular frameworks like OpenAI, HuggingFace, and AI21 |
| **Use cases**                                | Best for applications that require quick data lookup and retrieval | Suitable for applications that require complex interactions like chatbots, GQA, summarization |
| **Integration**                              | Functions as a smart storage mechanism                       | Designed to bring multiple tools together and chain operations |
| **Programming language**                     | Python-based library                                         | Python-based library                                         |
| **Front-end libraries**                      | LlamaIndex.ts                                                | LangChain.js                                                 |
| **Application breadth**                      | Focused on search-centric applications                       | Supports a broad range of applications                       |
| **Deployment**                               | Ideal for proprietary or specialized data                    | Facilitates the deployment of bespoke NLP applications       |

### Mix-Use of LangChain and Llama-Index

![](https://superwise.ai/wp-content/uploads/2023/11/LlamaIndex-LangChain_Blog-Internal-image-01-1024x565.png)
