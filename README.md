# AI_walkthrough

hands-on experience of AI features like OpenAI and LLM-based application framework.



## OpenAI 

- [x] GPT-4V
- [x] Dall.E-3
- [x] TTS
- [x] GPT-4-Turbo
- [ ] Assistant API


### GPTs creation examples

- [x] Create a GPTs using authorized API

Action config, using OpenAPI schema

## Framework

### LangChain General-purpose LLM framework

something about LangChain

- [ ] LLMs/Chat Models
- [ ] Embedding Models
- [ ] Prompts / Prompt Templates / Prompt Selectors
- [ ] Output Parsers
- [ ] Document Loaders
- [ ] Vector Stores / Retrievers
- [ ] Memory
- [ ] Agents / Agent Executors
- [ ] Tools / Toolkits
- [ ] Chains
- [ ] Callbacks/Tracing
- [ ] Async
- [ ] Integration open-source models

### Llama-Index

Focus on ingesting, structuring, and accessing private or domain-specific data. Say RAG.

### AutoGen

AutoGen is a framework that enables development of LLM applications using multiple agents that can converse with each other to solve tasks.

#### Use Cases

- Group Chat


### Multi-Modal

- [ ] Naive text RAG
- [ ] Text, Table, Image RAG

### Low-code design AI flow

[Flowise](https://flowiseai.com/)


## Landing AI Tech

### RAG

#### Evaluation System

1. TruLens [Trulens_Eval - Evaluation of LLMs and LLM-based applications with TruLens-Eval](https://www.trulens.org/trulens_eval/quickstart/)
2. Ragas [Ragas - Evaluate framework for RAG system](https://docs.ragas.io/en/latest/)



#### How to improve RAG

- [ ] Data quality, data cleaning
- [ ] Text segmentation, try different segmentation strategies
- [ ] Try different vector storage methods: Faiss, Chroma, Pinecone. Experiment with different embedding methods (e.g., BGE)
- [ ] Experiment with different retrievers
- [ ] Use hybrid search methods, such as BM25+Faiss
- [ ] RAG-Fusion: Generate multiple user queries and rank the results, utilizing Reciprocal Rank Fusion (RRF) and custom vector score weighting to achieve comprehensive and accurate results.