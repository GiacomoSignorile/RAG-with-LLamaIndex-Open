from setuptools import setup, find_packages

setup(
    name='rag_open_source',
    version='0.1',
    description='A package for RAG',
    author='Giacomo Signorile',
    python_requires='>=3.9',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        "console_scripts": [
            "start_rag = rag_open_source.main.main:main"
        ]
    }
)
