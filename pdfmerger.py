import os
import shutil

import fitz  # PyMuPDF


def merge_two_pages_into_one(input_pdf_path, tempdir):
    output_pdf_path = os.path.join(tempdir, "2on1_"+os.path.basename(input_pdf_path))
    doc = fitz.open(input_pdf_path)
    output_pdf = fitz.open()
    a4_width, a4_height = fitz.paper_size("a4")
    for i in range(0, len(doc), 2):
        new_page = output_pdf.new_page(width=a4_height, height=a4_width)
        page1 = doc.load_page(i)
        rect1 = fitz.Rect(0, 0, a4_height / 2, a4_width)  # Левая половина альбомного листа A4
        new_page.show_pdf_page(rect1, doc, i)  # Вставляем страницу на левую половину
        if i + 1 < len(doc):
            page2 = doc.load_page(i + 1)
            rect2 = fitz.Rect(a4_height / 2, 0, a4_height, a4_width)  # Правая половина альбомного листа A4
            new_page.show_pdf_page(rect2, doc, i + 1)  # Вставляем страницу на правую половину
        new_page.set_rotation(270)
    output_pdf.save(output_pdf_path)
    output_pdf.close()
    return output_pdf_path


def merge_four_pages_into_one(input_pdf_path, tempdir):
    output_pdf_path = os.path.join(tempdir, "4on1_" + os.path.basename(input_pdf_path))
    doc = fitz.open(input_pdf_path)
    output_pdf = fitz.open()
    a4_width, a4_height = fitz.paper_size("a4")
    for i in range(0, len(doc), 4):
        new_page = output_pdf.new_page(width=a4_width, height=a4_height)
        for j in range(4):
            if i + j < len(doc):
                page = doc.load_page(i + j)
                if j == 2:  # Верхний левый угол
                    rect = fitz.Rect(0, a4_height / 2, a4_width / 2, a4_height)
                elif j == 3:  # Верхний правый угол
                    rect = fitz.Rect(a4_width / 2, a4_height / 2, a4_width, a4_height)
                elif j == 0:  # Нижний левый угол
                    rect = fitz.Rect(0, 0, a4_width / 2, a4_height / 2)
                elif j == 1:  # Нижний правый угол
                    rect = fitz.Rect(a4_width / 2, 0, a4_width, a4_height / 2)
                new_page.show_pdf_page(rect, doc, i + j)
    output_pdf.save(output_pdf_path)
    output_pdf.close()
    doc.close()
    return output_pdf_path


def merge_pdfs(output_pdf_path, pdf_list, tempdir):
    temp_file = os.path.join(tempdir, os.path.basename(output_pdf_path))
    merged_pdf = fitz.open()
    for pdf_path in pdf_list:
        pdf_doc = fitz.open(pdf_path)
        merged_pdf.insert_pdf(pdf_doc)
        pdf_doc.close()
    merged_pdf.save(temp_file)
    merged_pdf.close()
    shutil.copy(temp_file, output_pdf_path)
