
@echo off
python -m venv rag_venv
.\rag_venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements2.txt
echo Installazione completata. Usa '.\venv\Scripts\activate' per attivare l'ambiente virtuale.
