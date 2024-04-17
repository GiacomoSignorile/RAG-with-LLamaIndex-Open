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
from difflib import SequenceMatcher
import tempfile



log_directory = "./src/log"
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
    x_1 = (textblock.block.x_1 - 20) * scale 
    y_1 = (textblock.block.y_1 - 20) * scale 
    x_2 = (textblock.block.x_2 + 20) * scale 
    y_2 = (textblock.block.y_2) * scale 
    return y_1,x_1,y_2,x_2

def processing_text(text):
    listText = text.split()
    text = ' '.join(listText)
    return text

def extraction_table_ocr(img):
    ocr = PaddleOCR(lang='it')
    #tesseract = TesseractOCR(lang='eng+ita')
    # Save PIL Image as PNG file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        temp_filename = temp_file.name
        img.save(temp_file.name, format='PNG')
    # Create Image object using the temporary PNG file
    doc = Image(temp_filename)
    # Table extraction
    extracted_table = doc.extract_tables(ocr=ocr, implicit_rows=False, borderless_tables=True, min_confidence=50)
    df = extracted_table[0].df
    df = df.dropna(axis=1, how='all').fillna('')
    df.columns = df.iloc[0]
    df = df.iloc[1:]
    df = df.astype(str)
    
    ocrTableMD = df

    #ocrTableMD = to_custom_markdown(df)
    
    # Clean up temporary file
    os.unlink(temp_filename)

    return ocrTableMD


def similarity_score(s1, s2):
    return SequenceMatcher(None, s1, s2).ratio()

def find_best_table(ocr_table, tabula_table, fitz_text):
    # Confronto delle colonne e delle righe
    if ocr_table.shape == tabula_table.shape:
        # Similarità del testo estratto
        ocr_text = ocr_table.to_string()
        tabula_text = tabula_table.to_string()
        ocr_similarity = similarity_score(fitz_text, ocr_text)
        tabula_similarity = similarity_score(fitz_text, tabula_text)
        
        if ocr_similarity > tabula_similarity:
            return ocr_table
        else:
            return tabula_table
    else:
        # Se le dimensioni delle tabelle non corrispondono, scegliere la tabella con più righe o colonne
        ocr_size = np.prod(ocr_table.shape)
        tabula_size = np.prod(tabula_table.shape)
        if ocr_size > tabula_size:
            return ocr_table
        else:
            return tabula_table


def apply_ocr_to_pdf(pdf_path, output_path=None):
    """
    Applica OCR a un PDF scannerizzato usando ocrmypdf.
    """
    if output_path is None:
        output_path = pdf_path  # Sovrascrive il file originale se non viene specificato un percorso di output
    subprocess.run(['ocrmypdf', pdf_path, output_path], check=True)


def replace_tables_in_text(pdf_path, use_ocr_table = False):
    
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

                x1, y1, x2, y2 = table.block.x_1 - 20, table.block.y_1 - 20, table.block.x_2 + 20, table.block.y_2
                table_img = img_pil.crop((x1, y1, x2, y2))

                rect_table = fitz.Rect(x1, y1, x2, y2) 
                
                fitz_table_text = page.get_text("text", clip=rect_table)
                
                logging.info(fitz_table_text)
                # plt.imshow(table_img)
                # plt.axis('off')  
                # plt.show()
                
                try:
                    tables = tabula.read_pdf(pdf_path, pages=page_num + 1, area=area, multiple_tables=False)
                    if tables:
                        md_table = tables[0].dropna(axis=1, how='all').fillna('')
                        md_tables.append(md_table)
                        md_table = md_table.to_markdown(index=False, tablefmt = "github")
                        #md_tables.append(md_table)
                        md_table = processing_text(md_table)
                        # md_table_ocr = extraction_table_ocr(table_img)

                        # md_tables_ocr.append(md_table_ocr)

                        if use_ocr_table == True:

                            md_table_ocr = extraction_table_ocr(table_img)
                            md_tables_ocr.append(md_table_ocr)
                            md_table_ocr = md_table_ocr.to_markdown(index=False, tablefmt = "github")
                            # md_tables.append(md_table)
                            md_table_ocr = processing_text(md_table_ocr)
                            
                            table_text = f' <start_table{i+1}>' + md_table_ocr + f' <end_table{i+1}>'
                        else:
                            table_text = f' <start_table{i+1}>' + md_table + f' <end_table{i+1}>'
                    else:
                        table_text = ''
                except Exception as e:
                    logging.error(f"Error extracting table: {e}. Proceeding with text extraction only.")
                    table_text = fitz_table_text

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

    return text_chunks,md_tables
