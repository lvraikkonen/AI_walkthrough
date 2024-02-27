from typing import Optional
from nemoguardrails.actions import action
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.base.response.schema import StreamingResponse


# Global variable to cache the query_engine
query_engine_cache = None

def init():
    global query_engine_cache  # Declare to use the global variable
    # Check if the query_engine is already initialized
    if query_engine_cache is not None:  
        print('Using cached query engine')
        return query_engine_cache

    # load data
    documents = SimpleDirectoryReader("data").load_data()
    print(f'Loaded {len(documents)} documents')

    splitter = SentenceSplitter(chunk_size=256)
    index = VectorStoreIndex.from_documents(documents, transformations=[splitter])
    vector_retriever = index.as_retriever(similarity_top_k=2)

    bm25_retriever = BM25Retriever.from_defaults(
        docstore=index.docstore, similarity_top_k=2
    )

    retriever = QueryFusionRetriever(
        [vector_retriever, bm25_retriever],
        similarity_top_k=2,
        num_queries=3,  # set this to 1 to disable query generation
        mode="reciprocal_rerank",
        use_async=True,
        verbose=True,
        # query_gen_prompt="...",  # we could override the query generation prompt here
    )

    # get the query engine
    query_engine_cache = RetrieverQueryEngine.from_args(retriever)

    return query_engine_cache

def get_query_response(query_engine: BaseQueryEngine, query: str) -> str:
    """
    Function to query based on the query_engine and query string passed in.
    """
    response = query_engine.query(query)
    if isinstance(response, StreamingResponse):
        typed_response = response.get_response()
    else:
        typed_response = response
    response_str = typed_response.response
    if response_str is None:
        return ""
    return response_str

@action(is_system_action=True)
async def user_query(context: Optional[dict] = None):
    """
    Function to invoke the query_engine to query user message.
    """
    user_message = context.get("user_message")
    print('user_message is ', user_message)
    query_engine = init()
    return get_query_response(query_engine, user_message)