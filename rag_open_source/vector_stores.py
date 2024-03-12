from llama_index.vector_stores.astra_db import AstraDBVectorStore
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
import os
import pymongo
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch

def setupAstradb(embedding_dim,collection_name,ASTRA_TOKEN,ASTRA_API_ENDPOINT,ASTRA_NAMESPACE):
    astra_db_store = AstraDBVectorStore(
        token=ASTRA_TOKEN,
        api_endpoint=ASTRA_API_ENDPOINT,
        namespace=ASTRA_NAMESPACE,
        collection_name=collection_name,
        embedding_dimension=embedding_dim
    )
    return astra_db_store


def setupChromaDB(nodes=None, path="./VectorStore", name="default_collection"):
    """
    Initializes a Chroma database collection and optionally adds nodes (vectors) to it if they are provided.
    
    Parameters:
    - nodes: The vector data to be added to the collection. If None, no nodes are added.
    - path: The filesystem path for storing the database files. Default is "./VectorStore".
    - name: The name of the collection. Default is "default_collection".
    
    Returns:
    - The initialized vector store object.
    """
    try:
        chroma_client = chromadb.PersistentClient(path)
        
        chroma_collection = chroma_client.get_or_create_collection(name)
        
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        if nodes is not None:
            vector_store.add(nodes)
        
        return vector_store
    except Exception as e:
        print(f"Error initializing ChromaDB Vector Store: {e}")
        return None

    
def setupPinecone(api_key, name, dimension=512, metric="euclidean"):
    """
    Initializes or connects to a Pinecone index with specified configurations and prepares a vector store.
    
    Parameters:
    - api_key: Your Pinecone API key.
    - name: The name of the Pinecone index.
    - dimension: The dimensionality of the vectors to be stored. Default is 512.
    - metric: The metric used for vector comparison (e.g., "euclidean", "cosine"). Default is "euclidean".
    - pod_type: The type of Pinecone pod to use (affects performance and cost). Default is "p1".
    
    Returns:
    - The initialized Pinecone vector store object, or None if an error occurs.
    """
    try:
        # Initialize Pinecone environment
        pc = Pinecone(api_key = api_key)

        # Check if the index exists; if not, create it with specified configurations
        if name not in pc.list_indexes():
            pc.create_index(
                name, dimension=dimension, metric=metric
            )
        
        # Connect to the existing or newly created index
        index = pc.Index(name)
        
        # Construct the vector store
        vector_store = PineconeVectorStore(pinecone_index=index)
        return vector_store
    except Exception as e:
        print(f"Error setting up Pinecone Vector Store: {e}")
        return None
    

# def setupMondoDB():
#     """
#     Initializes or connects to a Pinecone index with specified configurations and prepares a vector store.
    
#     Parameters:
#     - api_key: Your Pinecone API key.
#     - name: The name of the Pinecone index.
#     - dimension: The dimensionality of the vectors to be stored. Default is 128.
#     - metric: The metric used for vector comparison (e.g., "euclidean", "cosine"). Default is "euclidean".
#     - pod_type: The type of Pinecone pod to use (affects performance and cost). Default is "p1".
    
#     Returns:
#     - The initialized Pinecone vector store object, or None if an error occurs.
#     """
#     try:
#         # Initialize Pinecone environment
#         mongo_uri = os.environ["MONGO_URI"]

#         mongodb_client = pymongo.MongoClient(mongo_uri)

#         # construct store
#         vector_store = MongoDBAtlasVectorSearch(mongodb_client)

#         return vector_store
#     except Exception as e:
#         print(f"Error setting up Pinecone Vector Store: {e}")
#         return None
