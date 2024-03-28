from llama_index.vector_stores.astra_db import AstraDBVectorStore
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from pinecone import Pinecone
from pinecone import ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
import os
import pymongo
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core.ingestion import IngestionPipeline
import logging
from dotenv import load_dotenv

load_dotenv('.env')

def choose_vector_store(store_name, *args, **kwargs):
    """
    Choose and setup a vector store based on the given store name.
    
    Args:
        store_name (str): Name of the vector store to setup.
        *args: Additional arguments for vector store setup.
        **kwargs: Additional keyword arguments for vector store setup.
        
    Returns:
        Instance of the chosen vector store.
    """
    if store_name == "AstraDB":
        if  "collection_name" in args:
            return setupAstradb(*args, **kwargs)
        else:
            logging.error("Missing required arguments for AstraDB Vector Store setup.")
            return None
    elif store_name == "ChromaDB":
        if "nodes" in kwargs and "path" in kwargs and "name" in kwargs:
            return setupChromaDB(*args, **kwargs)
        else:
            logging.error("Missing required arguments for ChromaDB Vector Store setup.")
            return None
    elif store_name == "Pinecone":
        if "api_key" in kwargs and "name" in kwargs:
            return setupPinecone(*args, **kwargs)
        else:
            logging.error("Missing required arguments for Pinecone Vector Store setup.")
            return None
    else:
        logging.error("Unknown vector store name.")
        return None


def setupAstradb(collection_name, nodes = None, embeddings_dim = 1024):
    try:
        ASTRA_TOKEN = os.getenv("ASTRA_TOKEN")
        ASTRA_API_ENDPOINT = os.getenv("ASTRA_API_ENDPOINT")
        
        
        astra_db_store = AstraDBVectorStore(
            token=ASTRA_TOKEN,
            api_endpoint=ASTRA_API_ENDPOINT,
            collection_name=collection_name,
            embedding_dimension=embeddings_dim
        )
        
        if nodes is not None:
            astra_db_store.add(nodes)
        
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

def setupPinecone(documents, embed_model, name, dimension=512, metric="euclidean",spec=ServerlessSpec(cloud="aws", region="us-west-2")):
    try:
        api_key = os.getenv("PINECONE_API_KEY")
        
        pc = Pinecone(api_key=api_key)
        if name not in pc.list_indexes():
            pc.create_index(name, dimension=dimension, metric=metric, spec=spec)
        
        index = pc.Index(name)
        vector_store = PineconeVectorStore(pinecone_index=index)
        
#        if nodes is not None:
#            try:
#                vector_store.fetch(ids=[nodes[0].id])
#            except:
#                vector_store.upsert(ids=[node.id for node in nodes], vectors=[node.vector for node in nodes])
        

                # Our pipeline with the addition of our PineconeVectorStore
        pipeline = IngestionPipeline(
            transformations=[
                embed_model,
                ],
                vector_store=vector_store  # Our new addition
            )

        # Now we run our pipeline!
        pipeline.run(documents=documents)

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
