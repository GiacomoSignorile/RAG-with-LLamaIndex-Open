from llama_index.core import QueryBundle
from llama_index.core.retrievers import BaseRetriever
from typing import Any, List
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.core.schema import NodeWithScore
from typing import Optional
from rag_open_source.vector_stores import AstraDBVectorStore
from rag_open_source import embeddings

class VectorDBRetriever(BaseRetriever):
    """Retriever over a postgres vector store."""

    def __init__(
        self,
        vector_store: AstraDBVectorStore,
        embed_model: embeddings.getEmbeddingmodel,
        query_mode: str = "default",
        similarity_top_k: int = 3,
    ) -> None:
        """Init params."""
        self._vector_store = vector_store
        self._embed_model = embed_model
        self._query_mode = query_mode
        self._similarity_top_k = similarity_top_k
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve."""
        query_embedding = embed_model.get_query_embedding(
            query_bundle.query_str
        )
        vector_store_query = VectorStoreQuery(
            query_embedding=query_embedding,
            similarity_top_k=self._similarity_top_k,
            mode=self._query_mode,
        )
        query_result = vector_store.query(vector_store_query)

        nodes_with_scores = []
        for index, node in enumerate(query_result.nodes):
            score: Optional[float] = None
            if query_result.similarities is not None:
                score = query_result.similarities[index]
            nodes_with_scores.append(NodeWithScore(node=node, score=score))

        return nodes_with_scores
    

def getRetriever(vector_store, embed_model):
    retriever = VectorDBRetriever(
    vector_store, embed_model, query_mode="default", similarity_top_k=2
    )
    return retriever

