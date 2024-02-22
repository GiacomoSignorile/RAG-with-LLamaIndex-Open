from llama_index.core import Document
import pdf_ingestion.pdf_ingestion as pdf_ingestion
from llama_index.core.node_parser import SentenceSplitter
import os
import re

def custom_chunker(text, max_length=1024):
    
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


folder_path = '.\Docs'
pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

chunks = []

for pdf_file in pdf_files:
    full_path = os.path.join(folder_path, pdf_file)
    print(pdf_file)
    text = pdf_ingestion.replace_tables_in_text(full_path)
    chunks.append(text)

chunks_splitted = []

for chunk in chunks:
    for text in chunk:
        print(f'text unsplitted : {text}')
        chunk_splitted = custom_chunker(text)
        print(len(chunk_splitted))
        if len(chunk_splitted) > 1:
            print(f'lunghezza {len(chunk_splitted[0])} text splitted : {chunk_splitted}')
        chunks_splitted.extend(chunk_splitted)


documents = [Document(text=text) for text in chunks_splitted]
