from llama_index.core import Document
import pdf_ingestion
from llama_index.core.node_parser import SentenceSplitter
import os
import re

def custom_chunker(text, max_length=1024):
    # Pattern per identificare le tabelle
    table_pattern = re.compile(r'<start_table\d+>.*?<end_table\d+>', re.DOTALL)
    
    text_chunks = [] 
    current_chunk = ""
    
    # Trova tutte le tabelle nel testo
    tables = table_pattern.findall(text)

    table_positions = [(m.start(0), m.end(0)) for m in table_pattern.finditer(text)]
    
    last_pos = 0
    for start, end in table_positions:
        # Aggiungi il testo prima della tabella al chunk corrente
        pre_table_text = text[last_pos:start]
        for part in pre_table_text.split(" "):
            if len(current_chunk) + len(part) + 1 <= max_length:
                current_chunk += (part + " ")
            else:
                text_chunks.append(current_chunk.strip())  # Uso di "text_chunks" al posto di "chunks"
                current_chunk = part + " "
        
        # Aggiungi la tabella intera al chunk corrente o in uno nuovo
        table_text = text[start:end]
        if len(current_chunk) + len(table_text) <= max_length:
            current_chunk += table_text
        else:
            if current_chunk:  # Se il chunk corrente contiene del testo, lo salviamo
                text_chunks.append(current_chunk.strip())  
            text_chunks.append(table_text)  # Salviamo la tabella in un nuovo chunk
            current_chunk = ""  # Resettiamo il chunk corrente
        
        last_pos = end  # Aggiorniamo la posizione dell'ultimo carattere processato
    
    # Aggiungi eventuali parti di testo rimanenti dopo l'ultima tabella
    remaining_text = text[last_pos:]
    for part in remaining_text.split(" "):
        if len(current_chunk) + len(part) + 1 <= max_length:
            current_chunk += (part + " ")
        else:
            text_chunks.append(current_chunk.strip()) 
            current_chunk = part + " "
    
    if current_chunk:  # Aggiungi l'ultimo chunk se non è vuoto
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
        #print(f"Chunk di lunghezza {len(chunk)}: {chunk}\n---")
        chunks_splitted.append(chunk_splitted)

documents = [Document(text=text) for text in chunks_splitted]
