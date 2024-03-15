from llama_index.core import Document
import os
import re
import logging


def custom_chunker(text, max_length=1024):
    '''
    Spezza il chunk in più chunk in base alla max_length e alla presenza di tabelle

    '''
    table_pattern = re.compile(r'<start_table\d+>.*?<end_table\d+>', re.DOTALL)
    
    text_chunks = [] 
    current_chunk = ""
    
    
    tables = table_pattern.findall(text)

    table_positions = [(m.start(0), m.end(0)) for m in table_pattern.finditer(text)]
    
    last_pos = 0
    for start, end in table_positions:
       
        pre_table_text = text[last_pos:start]
        for part in pre_table_text.split(" "):
            if len(current_chunk) + len(part) + 1 <= max_length:
                current_chunk += (part + " ")
            else:
                text_chunks.append(current_chunk.strip()) 
                current_chunk = part + " "
        
        
        table_text = text[start:end]
        if len(current_chunk) + len(table_text) <= max_length:
            current_chunk += table_text
        else:
            if current_chunk: 
                text_chunks.append(current_chunk.strip())  
            text_chunks.append(table_text)  
            current_chunk = ""  
        
        last_pos = end 
    
    
    remaining_text = text[last_pos:]
    for part in remaining_text.split(" "):
        if len(current_chunk) + len(part) + 1 <= max_length:
            current_chunk += (part + " ")
        else:
            text_chunks.append(current_chunk.strip()) 
            current_chunk = part + " "
    
    if current_chunk:  
        text_chunks.append(current_chunk.strip())  
    
    return text_chunks



def get_documents(path='./Docs', max_len=1024):
    import pdf_parser.pdf_ingestion as pdf_ingestion

    '''
    Loads PDF documents into chunks, splits them, and returns a structure containing a list
    of Documents with the chunked text.
    '''
    folder_path = path
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

    documents = []
    tables = []

    for pdf_file in pdf_files:
        full_path = os.path.join(folder_path, pdf_file)
        logging.info(pdf_file)
        texts, md_tables = pdf_ingestion.replace_tables_in_text(full_path)
        
        for text in texts:
            chunk_splitted = custom_chunker(text, max_length=max_len)
            logging.info(len(chunk_splitted))
            if len(chunk_splitted) > 1:
                logging.info(f'length : {len(chunk_splitted[0])} text splitted : {chunk_splitted}')
            
            for chunk in chunk_splitted:
                documents.append(Document(text=chunk, metadata={'source': pdf_file}))
            
        tables.append(md_tables)

    return documents, tables