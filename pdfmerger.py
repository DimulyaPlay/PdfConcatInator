import os
import shutil
from PyPDF2 import PdfReader, PdfWriter, Transformation, PageObject

A4_WIDTH = 595.2756
A4_HEIGHT = 841.8898

def merge_two_pages_into_one(input_pdf_path, tempdir):
    output_pdf_path = os.path.join(tempdir, "2on1_" + os.path.basename(input_pdf_path))
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    a4_width, a4_height = A4_HEIGHT, A4_WIDTH
    for i in range(0, len(reader.pages), 2):
        new_page = PageObject.create_blank_page(width=a4_width, height=a4_height)

        # Левая страница
        page1 = reader.pages[i]
        orig_width1 = float(page1.mediabox.width)
        orig_height1 = float(page1.mediabox.height)
        scale1 = min((a4_width / 2) / orig_width1, a4_height / orig_height1)
        tx1 = 0
        ty1 = (a4_height - orig_height1 * scale1) / 2

        # Создаем копию
        page1_copy = PageObject.create_blank_page(width=orig_width1, height=orig_height1)
        page1_copy.merge_page(page1)
        page1_copy.add_transformation(Transformation().scale(scale1).translate(tx1, ty1))
        new_page.merge_page(page1_copy)

        # Правая страница (если есть)
        if i + 1 < len(reader.pages):
            page2 = reader.pages[i + 1]
            orig_width2 = float(page2.mediabox.width)
            orig_height2 = float(page2.mediabox.height)
            scale2 = min((a4_width / 2) / orig_width2, a4_height / orig_height2)
            tx2 = a4_width / 2
            ty2 = (a4_height - orig_height2 * scale2) / 2

            page2_copy = PageObject.create_blank_page(width=orig_width2, height=orig_height2)
            page2_copy.merge_page(page2)
            page2_copy.add_transformation(Transformation().scale(scale2).translate(tx2, ty2))
            new_page.merge_page(page2_copy)

        writer.add_page(new_page)

    with open(output_pdf_path, "wb") as f:
        writer.write(f)
    return output_pdf_path

def merge_four_pages_into_one(input_pdf_path, tempdir):
    output_pdf_path = os.path.join(tempdir, "4on1_" + os.path.basename(input_pdf_path))
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    a4_width, a4_height = A4_WIDTH, A4_HEIGHT

    for i in range(0, len(reader.pages), 4):
        new_page = PageObject.create_blank_page(width=a4_width, height=a4_height)
        positions = [
            (0, a4_height / 2),             # Верхний левый
            (a4_width / 2, a4_height / 2),  # Верхний правый
            (0, 0),                         # Нижний левый
            (a4_width / 2, 0),              # Нижний правый
        ]

        for j, (x_offset, y_offset) in enumerate(positions):
            if i + j < len(reader.pages):
                page = reader.pages[i + j]
                orig_width = float(page.mediabox.width)
                orig_height = float(page.mediabox.height)
                scale = min((a4_width / 2) / orig_width, (a4_height / 2) / orig_height)
                tx = x_offset
                ty = y_offset

                page_copy = PageObject.create_blank_page(width=orig_width, height=orig_height)
                page_copy.merge_page(page)
                page_copy.add_transformation(Transformation().scale(scale).translate(tx, ty))
                new_page.merge_page(page_copy)

        writer.add_page(new_page)

    with open(output_pdf_path, "wb") as f:
        writer.write(f)
    return output_pdf_path


def merge_pdfs(output_pdf_path, pdf_list, tempdir):
    temp_file = os.path.join(tempdir, os.path.basename(output_pdf_path))
    writer = PdfWriter()
    for pdf_path in pdf_list:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            writer.add_page(page)
    with open(temp_file, "wb") as f:
        writer.write(f)
    shutil.copy(temp_file, output_pdf_path)


def normalize_pdf_in_place(file_path: str):
    temp_path = file_path + ".tmp"
    reader = PdfReader(file_path)
    writer = PdfWriter()
    for page in reader.pages:
        orig_width = float(page.mediabox.width)
        orig_height = float(page.mediabox.height)
        is_landscape = orig_width > orig_height
        if is_landscape:
            target_width = A4_HEIGHT
            target_height = A4_WIDTH
        else:
            target_width = A4_WIDTH
            target_height = A4_HEIGHT
        scale = min(target_width / orig_width, target_height / orig_height)
        tx = (target_width - orig_width * scale) / 2
        ty = (target_height - orig_height * scale) / 2
        new_page = PageObject.create_blank_page(width=target_width, height=target_height)
        page_copy = PageObject.create_blank_page(width=orig_width, height=orig_height)
        page_copy.merge_page(page)
        page_copy.add_transformation(Transformation().scale(scale).translate(tx, ty))
        print(orig_height, orig_width, "->",  ty, tx)
        new_page.merge_page(page_copy)
        writer.add_page(new_page)
    with open(temp_path, "wb") as f:
        writer.write(f)
    os.replace(temp_path, file_path)