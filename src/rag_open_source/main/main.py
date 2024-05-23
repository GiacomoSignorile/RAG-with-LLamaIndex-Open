import yaml
from rag_open_source.pdf_parser import chunk_splitter, extract_layout, pdf_ingestion
from rag_open_source.retrieval import embeddings, retriever,vector_stores

def main():

    config_path = './config_project.yaml'

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
   
    documents,tables_md = chunk_splitter.get_documents(path = config['custom_splitter']['path'][0])

    embed_model = embeddings.getEmbeddingModel(name = config['embeddings']['name'][1])

    nodes = embeddings.createEmbeddings(documents, embed_model)

    #nodes = getattr(embeddings, 'createEmbeddings')(documents, embed_model)
    embeddings_dimensiom = len(nodes[0].embedding)
    
    #vector_store = vector_stores.setupChromaDB(nodes, config['vector_store']['path'][0], 
    #                                           config['vector_store']['name'][1])

    vector_store = vector_stores.choose_vector_store(store_name= 'AstraDB', nodes = nodes, embeddings_dim = embeddings_dimensiom, collection_name = 'test_bandi')

    vector_db_retriever_instance = retriever.VectorDBRetriever(vector_store=vector_store, 
                                                                embed_model=embed_model, 
                                                                similarity_top_k=5)   
    query_engine = retriever.get_query_engine(vector_db_retriever_instance, model_path='./model/mistral-Ita-7b-q5_k_m.gguf')

    query_str= input("Inserisci la tua domanda:")

    response = retriever.get_response_italian(query_str,query_engine)

    print(response)
