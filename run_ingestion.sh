python3.10 -m venv py310
source py310/bin/activate
pip install -U pip
pip install -r requirements.txt
sudo apt-get install -y poppler-utils
python3.10 setup.py bdist_wheel