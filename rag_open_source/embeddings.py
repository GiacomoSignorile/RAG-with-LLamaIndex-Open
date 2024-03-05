# sentence transformers
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def getEmbeddingmodel(name = "nickprock/sentence-bert-base-italian-uncased"):
    embed_model = HuggingFaceEmbedding(model_name=name)
    return embed_model

def createEmbeddings(nodes, embed_model):
    for node in nodes:
        node_embedding = embed_model.get_text_embedding(
            node.get_content(metadata_mode="all")
        )
        node.embedding = node_embedding
    return nodes

def getQueryEmbeddings(query_str):
    embed_model = getEmbeddingmodel()

    query_embedding = embed_model.get_query_embedding(query_str)

    return  query_embedding