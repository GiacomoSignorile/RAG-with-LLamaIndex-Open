# sentence transformers
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.schema import TextNode
from llama_index.core.node_parser import MarkdownElementNodeParser
import nest_asyncio
nest_asyncio.apply()

def getEmbeddingModel(name = "nickprock/sentence-bert-base-italian-uncased", max_len = 512):
    embed_model = HuggingFaceEmbedding(model_name=name, max_length= max_len)
    return embed_model

def createEmbeddings(documents, embed_model):
    nodes = createNodes(documents)

    for node in nodes:
        node_embedding = embed_model.get_text_embedding(
            node.get_content(metadata_mode="all")
        )
        node.embedding = node_embedding
    return nodes

def createNodes(documents):
    # nodes = []

    # for idx, text_chunk in enumerate(documents):
    #     node = TextNode(
    #         text=text_chunk.text,
    #     )
    #     # src_doc = documents[doc_idxs[idx]]
    #     # node.metadata = src_doc.metadata
    #     nodes.append(node)
    node_parser = MarkdownElementNodeParser()
    nodes = node_parser.get_nodes_from_documents(documents)

    return nodes