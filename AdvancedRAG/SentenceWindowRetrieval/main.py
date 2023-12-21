from llama_index import (
    SimpleDirectoryReader, VectorStoreIndex,
    Document,
    ServiceContext, StorageContext,
    load_index_from_storage
)

from llama_index.node_parser import SimpleNodeParser, SentenceWindowNodeParser
from llama_index.embeddings import OpenAIEmbedding, HuggingFaceEmbedding
from llama_index.llms import OpenAI
from llama_index.query_engine import RetrieverQueryEngine

from llama_index.indices.postprocessor import MetadataReplacementPostProcessor
from llama_index.indices.postprocessor import SentenceTransformerRerank

import os, logging
from typing import List
from pathlib import Path

from trulens_eval import Feedback, Tru, TruLlama
from trulens_eval.feedback import Groundedness
from trulens_eval.feedback.provider.openai import OpenAI as OpenAITruLens

import numpy as np

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


## load documents
documents = SimpleDirectoryReader(input_dir="../Data").load_data(show_progress=True)

## merge pages into one
document = Document(text="\n\n".join([doc.text for doc in documents]))


def create_indices(
        documents: Document, 
        index_save_dir: str,
        window_size: int=4,
        llm_model: str="gpt-3.5-turbo",
        temperature: float=0.1
):
    node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=window_size,
        window_metadata_key="window",
        original_text_metadata_key="original_text",
    )

    ## Create LLM and Embedding Model
    embed_model = OpenAIEmbedding() # default embedding model ada
    llm = OpenAI(api_key=api_key, model=llm_model, temperature=temperature)

    # ServiceContext
    sentence_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model=embed_model,
        node_parser=node_parser,
    )

    if not os.path.exists(index_save_dir):
        index = VectorStoreIndex.from_documents(
            [documents], service_context=sentence_context
        )
        # persist index
        index.storage_context.persist(persist_dir=index_save_dir)
    else:
        # load index if exists
        index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=index_save_dir)
        )
    
    return index

def create_query_engine(
    sentence_index: VectorStoreIndex,
    similarity_top_k: int = 6,
    rerank_top_n: int = 5,
    rerank_model: str = "BAAI/bge-reranker-base"
):
    # add metadata using postprocessor
    postproc = MetadataReplacementPostProcessor(
        target_metadata_key="window"
    )

    # rerank
    rerank = SentenceTransformerRerank(
        top_n=rerank_top_n,
        model=rerank_model
    )

    sentence_window_engine = sentence_index.as_query_engine(
        similarity_top_k = similarity_top_k,
        node_postprocessors = [postproc, rerank]
    )

    return sentence_window_engine

# create index
index = create_indices(
    documents=documents,
    index_save_dir="./sentence_window_size_3_index",
    window_size=3,
    llm_model="gpt-3.5-turbo",
    temperature=0.1
)

# create query engine
sentence_window_engine = create_query_engine(
    sentence_index=index,
    similarity_top_k=5,
    rerank_top_n=2,
)

# RAG pipeline evals
tru = Tru(database_file="../default.sqlite")

openai = OpenAITruLens()

grounded = Groundedness(groundedness_provider=OpenAITruLens())

# Define a groundedness feedback function
f_groundedness = Feedback(grounded.groundedness_measure_with_cot_reasons).on(
    TruLlama.select_source_nodes().node.text
).on_output(
).aggregate(grounded.grounded_statements_aggregator)

# Question/answer relevance between overall question and answer.
f_qa_relevance = Feedback(openai.relevance).on_input_output()

# Question/statement relevance between question and each context chunk.
f_qs_relevance = Feedback(openai.qs_relevance).on_input().on(
    TruLlama.select_source_nodes().node.text
).aggregate(np.mean)


tru_query_engine_recorder = TruLlama(sentence_window_engine,
                                     app_id='sentence_window_size_10',
                                     feedbacks=[f_groundedness, f_qa_relevance, f_qs_relevance])


eval_questions = []

with open("./eval_questions.txt", "r") as eval_qn:
    for qn in eval_qn:
        qn_stripped = qn.strip()
        eval_questions.append(qn_stripped)


def run_eval(eval_questions: List[str]):
    for qn in eval_questions:
        # eval using context window
        with tru_query_engine_recorder as recording:
            sentence_window_engine.query(qn)


run_eval(eval_questions=eval_questions)

# run dashboard
tru.run_dashboard()