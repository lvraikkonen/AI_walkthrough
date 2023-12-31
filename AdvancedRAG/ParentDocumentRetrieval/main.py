from typing import List
from llama_index import (
    Document,
    VectorStoreIndex,
    SimpleDirectoryReader,
    ServiceContext,
)
from llama_index.retrievers import RecursiveRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.node_parser import SimpleNodeParser
from llama_index.embeddings import OpenAIEmbedding
from llama_index.schema import IndexNode
from llama_index.llms import OpenAI

import os, logging
from typing import List
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

from trulens_eval import Feedback, Tru, TruLlama
from trulens_eval.feedback import Groundedness
from trulens_eval.feedback.provider.openai import OpenAI as OpenAITruLens

import numpy as np

## Create LLM and Embedding Model
embed_model = OpenAIEmbedding() # default embedding model ada
llm = OpenAI(api_key=api_key, model="gpt-3.5-turbo")
service_context = ServiceContext.from_defaults(
    embed_model=embed_model, llm=llm
)

wd = Path(r"D:\Playground\AI_walkthrough\AdvancedRAG")
storage_dir = wd / "ParentDocumentRetrieval" / "storage"
source_data_dir = wd  / "Data"
benchmark_result_db_dir = wd

# load data
documents = SimpleDirectoryReader(
    input_dir=source_data_dir).load_data(show_progress=True)

doc_text = "\n\n".join([d.get_content() for d in documents])
docs = [Document(text=doc_text)]

# create nodes parser
node_parser = SimpleNodeParser.from_defaults(chunk_size=1024)

# split into nodes
base_nodes = node_parser.get_nodes_from_documents(documents=docs)

# set document IDs
for idx, node in enumerate(base_nodes):
    node.id_ = f"node-{idx}"

# create parent child documents
sub_chunk_sizes = [128, 256, 512]
sub_node_parsers = [
    SimpleNodeParser.from_defaults(chunk_size=c, chunk_overlap=0) for c in sub_chunk_sizes
]

all_nodes = []
for base_node in base_nodes:
    for n in sub_node_parsers:
        sub_nodes = n.get_nodes_from_documents([base_node])
        sub_inodes = [
            IndexNode.from_text_node(sn, base_node.node_id) for sn in sub_nodes
        ]
        all_nodes.extend(sub_inodes)

    # also add original node to node
    original_node = IndexNode.from_text_node(base_node, base_node.node_id)
    all_nodes.append(original_node)

        
all_nodes_dict = {n.node_id: n for n in all_nodes}

# creating index
index = VectorStoreIndex(nodes=all_nodes, service_context=service_context)

# creating a chunk retriever
vector_retriever_chunk = index.as_retriever(similarity_top_k=2)


retriever_chunk = RecursiveRetriever(
    "vector",
    retriever_dict={"vector": vector_retriever_chunk},
    node_dict=all_nodes_dict,
    verbose=True,
)

query_engine_chunk = RetrieverQueryEngine.from_args(
    retriever_chunk, service_context=service_context
)

benchmark_result_db = benchmark_result_db_dir / 'benchmark.sqlite'

tru = Tru(database_file=benchmark_result_db)

fopenai = OpenAITruLens()

grounded = Groundedness(groundedness_provider=OpenAITruLens())

# Define a groundedness feedback function
f_groundedness = Feedback(grounded.groundedness_measure_with_cot_reasons).on(
    TruLlama.select_source_nodes().node.text
    ).on_output(
    ).aggregate(grounded.grounded_statements_aggregator)

# Question/answer relevance between overall question and answer.
f_qa_relevance = Feedback(fopenai.relevance).on_input_output()

# Question/statement relevance between question and each context chunk.
f_qs_relevance = Feedback(fopenai.qs_relevance).on_input().on(
    TruLlama.select_source_nodes().node.text
    ).aggregate(np.mean)


tru_query_engine_recorder = TruLlama(query_engine_chunk,
    app_id='ParentDocumentRetrieval',
    feedbacks=[f_groundedness, f_qa_relevance, f_qs_relevance])

eval_questions = []
eval_questions_file = wd / "RAG_Baseline"/ 'eval_questions.txt'

with open(eval_questions_file, "r") as eval_qn:
    for qn in eval_qn:
        qn_stripped = qn.strip()
        eval_questions.append(qn_stripped)


def run_eval(eval_questions: List[str]):
    for qn in eval_questions:
        with tru_query_engine_recorder as recording:
            query_engine_chunk.query(qn)


run_eval(eval_questions=eval_questions)

# run dashboard
tru.run_dashboard()