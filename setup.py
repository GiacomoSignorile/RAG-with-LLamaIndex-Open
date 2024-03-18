from setuptools import setup, find_packages

setup(
    name='rag_open_source',
    version='0.1',
    description='A package for RAG',
    author='Giacomo Signorile',
    python_requires='>=3.9',
    packages=find_packages('rag_open_source'),
    package_dir={'': 'rag_open_source'},
    entry_points={
        "console_scripts": [
            "rag = rag_open_source.main.dashboard:main"
        ]
    }
)
