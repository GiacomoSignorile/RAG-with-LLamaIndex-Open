import yaml
from rag_open_source import chunk_splitter, pdf_ingestion, extract_layout

def main(config_path):
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    
    pdf_files = pdf_ingestion.ingest_documents(config['ingestion_settings'])

    for pdf_file in pdf_files:
        
        chunks = chunk_splitter.split(config['chunk_splitter_settings'])
        
        
if __name__ == "__main__":
    config_path = 'path/to/your/config_project.yaml' 
    main(config_path)
