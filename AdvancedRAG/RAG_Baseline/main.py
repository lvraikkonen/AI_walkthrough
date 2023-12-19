from llama_index import SimpleDirectoryReader, VectorStoreIndex
from llama_index.node_parser import SimpleNodeParser
from llama_index import ServiceContext, StorageContext
from llama_index.embeddings import OpenAIEmbedding, HuggingFaceEmbedding
from llama_index.llms import OpenAI
from llama_index.query_engine import RetrieverQueryEngine
from llama_index import load_index_from_storage
import os, logging
from typing import List
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

## Create LLM and Embedding Model
embed_model = OpenAIEmbedding() # default embedding model ada
llm = OpenAI(api_key=api_key, model="gpt-3.5-turbo")
service_context = ServiceContext.from_defaults(
    embed_model=embed_model, llm=llm
)

wd = Path(r"D:\Playground\AI_walkthrough\AdvancedRAG")
storage_dir = wd / "RAG_Baseline" / "storage"
source_data_dir = wd  / "Data"
benchmark_result_db_dir = wd

# check if data index already exists
if not storage_dir.exists():
    ## Loading Documents
    documents = SimpleDirectoryReader(input_dir=source_data_dir).load_data(show_progress=True)

    # # check documents (only in notebook)
    # print(len(documents))
    # print(documents[0])


    ## Splitting Document Into Chunks
    node_parser = SimpleNodeParser.from_defaults(chunk_size=1024)
    # split into nodes
    base_nodes = node_parser.get_nodes_from_documents(documents=documents)

    # # check nodes (only in notebook)
    # print(len(base_nodes))
    # print(base_nodes[0])


    ## Create index: a vector store to store the embeddings
    index = VectorStoreIndex(
        nodes=base_nodes,
        service_context=service_context
    )
    # store index
    index.storage_context.persist(persist_dir=storage_dir)

else:
    # load existing index
    logging.info(f"Loading existing index from {storage_dir}...")
    storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
    index = load_index_from_storage(storage_context=storage_context)



# create retriever
retriever = index.as_retriever(similarity_top_k=2)

# test retriever
retrieved_nodes = retriever.retrieve("What did the president say about covid-19")
# print(retrieved_nodes)

# print("\n\n\n=============================================================")
# print("Node Texts")

# for node in retrieved_nodes:
#     print(node.text)
#     # get word count for each doc
#     print(len(node.text.split()))
#     print("==" * 10)


## Create Query Engine using retriever
query_engine = RetrieverQueryEngine.from_args(
    retriever=retriever,
    service_context=service_context
)

# test response
# response = query_engine.query("What did the president say about covid-19")

# print(response)


## Evaluation Part
from trulens_eval import Feedback, Tru, TruLlama, Select
from trulens_eval.feedback import Groundedness
from trulens_eval.feedback.provider.openai import OpenAI as OpenAITruLens

import numpy as np

benchmark_result_db = benchmark_result_db_dir / 'benchmark.sqlite'

tru = Tru(database_file=benchmark_result_db)

fopenai = OpenAITruLens() # default using GPT3.5-turbo for eval

grounded = Groundedness(groundedness_provider=OpenAITruLens())
# Define a groundedness feedback function
f_groundedness = Feedback(grounded.groundedness_measure_with_cot_reasons).on(
    TruLlama.select_source_nodes().node.text
    ).on_output(
    ).aggregate(grounded.grounded_statements_aggregator)

# Question/answer relevance between overall question and answer.
f_qa_relevance = Feedback(fopenai.relevance).on_input_output()

# Question/statement relevance between question and each context chunk.
f_context_relevance = Feedback(fopenai.qs_relevance).on_input().on(
    TruLlama.select_source_nodes().node.text
    ).aggregate(np.mean)

tru_query_engine_recorder = TruLlama(query_engine,
    app_id='RAG_Baseline_V0',
    feedbacks=[f_groundedness, f_qa_relevance, f_context_relevance])

eval_questions = []

eval_questions_file = wd / "RAG_Baseline"/ 'eval_questions.txt'

with open(eval_questions_file, "r") as eval_qn:
    for qn in eval_qn:
        qn_stripped = qn.strip()
        eval_questions.append(qn_stripped)


def run_eval(eval_questions: List[str]):
    for qn in eval_questions:
        # eval using context window
        with tru_query_engine_recorder as recording:
            query_engine.query(qn)


run_eval(eval_questions=eval_questions)


# run dashboard
tru.run_dashboard()