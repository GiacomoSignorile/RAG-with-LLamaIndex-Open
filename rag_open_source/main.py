import yaml
from rag_open_source import chunk_splitter, pdf_ingestion, extract_layout, embeddings, vector_stores, retriever

def main(config_path):
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
   
    documents,tables_md = chunk_splitter.get_documents(config['custom_splitter']['path'][0])

    embed_model = embeddings.getEmbeddingModel(config['embeddings']['name'][0])

    nodes = embeddings.createEmbeddings(documents, embed_model)

    vector_store = vector_stores.setupChromaDB(nodes, config['vector_store']['path'][0], config['vector_store']['name'][0])

    vector_db_retriever_instance = retriever.VectorDBRetriever(vector_store=vector_store, embed_model=embed_model, similarity_top_k=3)    
        
    query_engine = retriever.get_query_engine(vector_db_retriever_instance)

    query_str= input("Inserisci la tua domanda:")

    response = retriever.get_response_italian(query_str,query_engine)

    print(response)

if __name__ == "__main__":
    config_path = './config_project.yaml' 
    main(config_path)