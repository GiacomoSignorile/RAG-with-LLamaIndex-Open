from setuptools import setup, find_packages

setup(
    name="my_package",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Elenco di tutte le dipendenze dal tuo requirements.txt
    ],
    entry_points={
        'console_scripts': [
            'pdf_processor=pdf_processor.pdf_processor:main',  # Adatta questa riga al tuo codice
        ],
    },
)
