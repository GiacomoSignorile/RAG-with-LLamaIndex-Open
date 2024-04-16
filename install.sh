python3.10 -m venv py310
source py310/bin/activate
sudo apt-get install -y poppler-utils
sudo apt-get install gcc-11
sudo apt install g++-11
sudo apt-get install build-essential
sudo apt install -y default-jdk
pip install -U pip
pip install -r requirements.txt
sudo apt-get install python3-dev
python3.10 -m pip install -U 'git+https://github.com/facebookresearch/detectron2.git@ff53992b1985b63bd3262b5a36167098e3dada02'
pip install git+https://github.com/FlagOpen/FlagEmbedding.git
rm -rf build/ dist/ src/src.egg-info/
cd dist
pip install "$(ls)" --force-reinstall
python3.10 src/rag_open_source/setup.py bdist_wheel
start_rag