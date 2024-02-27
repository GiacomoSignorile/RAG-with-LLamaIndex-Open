
@echo off
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements2.txt
python setup.py bdist_wheel
echo Installazione completata. Usa '.\.venv\Scripts\activate' per attivare l'ambiente virtuale.
