import subprocess
import tabula
import pdf2image
import layoutparser as lp
import numpy as np
import pandas as pd
import fitz
from .extract_layout import ExtractLayout
import os
import logging 
from img2table.document import Image
from img2table.ocr import TesseractOCR, PaddleOCR
import matplotlib.pyplot as plt
from PIL import Image as PILImage



log_directory = "./log"
log_filename = "application.log"


logging.basicConfig(filename=os.path.join(log_directory, log_filename),
                    filemode='w',  # 'a' to append to an existing file, 'w' to overwrite
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def is_scanned_pdf(pdf_path):
    with fitz.open(pdf_path) as doc:
        for page in doc:
            if page.get_text():
                return False
    return True


def scale_xy(textblock, scale=72/200):
    x_1 = textblock.block.x_1 * scale - 15
    y_1 = textblock.block.y_1 * scale - 5
    x_2 = textblock.block.x_2 * scale + 15
    y_2 = textblock.block.y_2 * scale + 5
    return y_1,x_1,y_2,x_2

def processing_text(text):
    listText = text.split()
    text = ' '.join(listText)
    return text

def extraction_table_ocr(img):
    ocr = PaddleOCR(lang='it')
    doc = Image(img)
    # Table extraction
    extracted_table= doc.extract_tables(ocr=ocr, implicit_rows=True, borderless_tables=True, min_confidence=50)
    ocrTableMD = extracted_table.df.to_markdown(index=False)
    #ocrTableMD = processing_text(ocrTableMD)

    return ocrTableMD


def apply_ocr_to_pdf(pdf_path, output_path=None):
    """
    Applica OCR a un PDF scannerizzato usando ocrmypdf.
    """
    if output_path is None:
        output_path = pdf_path  # Sovrascrive il file originale se non viene specificato un percorso di output
    subprocess.run(['ocrmypdf', pdf_path, output_path], check=True)


def replace_tables_in_text(pdf_path):
    
    model =  ExtractLayout(
        config_path='lp://TableBank/faster_rcnn_R_101_FPN_3x/config',
        # model_path='./models/TableBank-faster_rcnn_R_101_FPN_3x-model.pth',
        label_map={0: "Table"},
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8]
    )

    md_tables = []
    md_tables_ocr = []
    text_chunks = []
    

    if is_scanned_pdf(pdf_path):
        logging.info(f"Scanned PDF detected. Applying OCR to: {pdf_path}")
        apply_ocr_to_pdf(pdf_path)
        logging.info("OCR completed.")
    
    doc = pdf2image.convert_from_path(pdf_path)

    doc_fitz = fitz.open(pdf_path)

    for page_num, document in enumerate(doc_fitz):
        img = np.asarray(doc[page_num])
        img_pil = PILImage.fromarray(img)
        detected = model.detect(img)

        accumulated_text = ""
        previous_bottom = 0
        page = doc_fitz[page_num]
        
        logging.info(page_num + 1)
        if detected:
            detected.sort(key=lambda x: x.block.y_1)  # Ordina le tabelle per la coordinata y

            for i, table in enumerate(detected):
                new_coordinates = scale_xy(table)
                area = [new_coordinates[0], new_coordinates[1], new_coordinates[2], new_coordinates[3]]
                # Utilizza le coordinate rilevate dal modello per estrarre l'area corretta dall'immagine
                x1, y1, x2, y2 = int(table.block.x_1 - 15), int(), int(table.block.x_2 + 15), int(table.block.y_2 + 5)
                #table_img = imgpng[y1:y2, x1:x2]table.block.y_1 - 5
                table_img = img_pil.crop((table.block.x_1 - 15, table.block.y_1 - 5, table.block.x_2 + 15, table.block.y_2 + 5))
                # Visualizza l'immagine ritagliata utilizzando matplotlib
                plt.imshow(table_img)
                plt.axis('off')  # Nasconde gli assi
                plt.show()
                #table_img = img[int(table.block.x_1):int(table.block.y_1), int(table.block.x_1):int(table.block.y_2)]
                try:
                    tables = tabula.read_pdf(pdf_path, pages=page_num + 1, area=area, multiple_tables=False)
                    if tables:
                        md_table = tables[0].dropna(axis=1, how='all').fillna('')
                        md_table = md_table.to_markdown(index=False)
                        md_tables.append(md_table)
                        md_table = processing_text(md_table)
                        md_table_ocr = extraction_table_ocr(table_img)
                        
                        md_tables_ocr.append(md_table_ocr)
                        table_text = f' <start_table{i+1}>' + md_table + f' <end_table{i+1}>'
                    else:
                        table_text = ''
                except Exception as e:
                    logging.error(f"Error extracting table: {e}. Proceeding with text extraction only.")
                    table_text = ''

                top, bottom = new_coordinates[0], new_coordinates[2]
                text_before = page.get_text("text", clip=fitz.Rect(0, previous_bottom, page.rect.width, top))
                text_before = processing_text(text_before)
                previous_bottom = bottom

                accumulated_text += text_before + table_text

            # Aggiungi il testo dopo l'ultima tabella
            text_after = page.get_text("text", clip=fitz.Rect(0, previous_bottom, page.rect.width, page.rect.height))
            text_after = processing_text(text_after)
            accumulated_text += text_after
        else:
            # Nessuna tabella rilevata, usa tutto il testo della pagina
            logging.info('No tables')
            accumulated_text = processing_text(page.get_text('text'))

        
        text_chunks.append(accumulated_text)

    return text_chunks,md_tables,md_tables_ocr
