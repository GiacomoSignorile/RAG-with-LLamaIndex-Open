import tabula
import pdf2image
import layoutparser as lp
import numpy as np
import pandas as pd
import fitz
import re

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

def replace_tables_in_text(pdf_path):
    doc_fitz = fitz.open(pdf_path)
    text_chunks = []

    model = lp.models.Detectron2LayoutModel(
        config_path='./Docs/config2.yaml',
        model_path='./models/TableBank-faster_rcnn_R_101_FPN_3x-model.pth',
        label_map={0: "Table"},
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8]
    )

    doc = pdf2image.convert_from_path(pdf_path)

    for page_num, document in enumerate(doc_fitz):
        img = np.asarray(doc[page_num])
        detected = model.detect(img)

        accumulated_text = ""
        previous_bottom = 0
        page = doc_fitz[page_num]

        if detected:
            detected.sort(key=lambda x: x.block.y_1)  # Ordina le tabelle per la coordinata y

            for i, table in enumerate(detected):
                new_coordinates = scale_xy(table)
                area = [new_coordinates[0], new_coordinates[1], new_coordinates[2], new_coordinates[3]]
                tables = tabula.read_pdf(pdf_path, pages=page_num + 1, area=area, multiple_tables=False)
                if not tables:
                    continue
                
                md_table = tables[0].dropna(axis=1, how='all').fillna('')
                md_table = md_table.to_markdown(index=False)

                top, bottom = new_coordinates[0], new_coordinates[2]
                
                text_before = page.get_text("text", clip=fitz.Rect(0, previous_bottom, page.rect.width, top))
                text_before = processing_text(text_before)
                previous_bottom = bottom  # Aggiorna il testo finale per il prossimo for

                accumulated_text += text_before + f' <start_table{i+1}>' + md_table + f' <end_table{i+1}>'

            # Aggiungi il testo dopo l'ultima tabella
            text_after = page.get_text("text", clip=fitz.Rect(0, previous_bottom, page.rect.width, page.rect.height))
            text_after = processing_text(text_after)
            accumulated_text += text_after
        else:
            # Nessuna tabella rilevata, usa tutto il testo della pagina
            accumulated_text = processing_text(page.get_text('text'))

        text_chunks.append(accumulated_text)

    return text_chunks
