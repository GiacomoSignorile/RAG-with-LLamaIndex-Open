from llama_index.vector_stores.astra_db import AstraDBVectorStore
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
import os
import pymongo
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
import logging

def setupAstradb(embedding_dim, collection_name, ASTRA_TOKEN, ASTRA_API_ENDPOINT, ASTRA_NAMESPACE):
    try:
        astra_db_store = AstraDBVectorStore(
            token=ASTRA_TOKEN,
            api_endpoint=ASTRA_API_ENDPOINT,
            namespace=ASTRA_NAMESPACE,
            collection_name=collection_name,
            embedding_dimension=embedding_dim
        )
        return astra_db_store
    except Exception as e:
        logging.error(f"Error initializing AstraDB Vector Store: {e}")
        return None

def setupChromaDB(nodes=None, path="./database", name="default_collection"):
    try:
        chroma_client = chromadb.PersistentClient(path)
        chroma_collection = chroma_client.get_or_create_collection(name)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        if nodes is not None:
            vector_store.add(nodes)
        
        return vector_store
    except Exception as e:
        logging.error(f"Error initializing ChromaDB Vector Store: {e}")
        return None

def setupPinecone(api_key, name, dimension=512, metric="euclidean"):
    try:
        pc = Pinecone(api_key=api_key)
        if name not in pc.list_indexes():
            pc.create_index(name, dimension=dimension, metric=metric)
        
        index = pc.Index(name)
        vector_store = PineconeVectorStore(pinecone_index=index)
        return vector_store
    except Exception as e:
        logging.error(f"Error setting up Pinecone Vector Store: {e}")
        return None
    
def print_vector_stores(path="./VectorStore"):
    try:
        chroma_client = chromadb.PersistentClient(path)
        
        vector_stores = chroma_client.list_collections()
        
        for vector_store in vector_stores:
            print(vector_store)
    except Exception as e:
        # If there's an error, log it
        logging.error(f"Error listing ChromaDB Vector Stores: {e}")


# Uncomment and adjust the MongoDB setup function as necessary, including the correct parameters and error handling.
# def setupMondoDB():
#     try:
#         mongo_uri = os.environ["MONGO_URI"]
#         mongodb_client = pymongo.MongoClient(mongo_uri)
#         vector_store = MongoDBAtlasVectorSearch(mongodb_client)
#         return vector_store
#     except Exception as e:
#         logging.error(f"Error setting up MongoDB Vector Store: {e}")
#         return None
