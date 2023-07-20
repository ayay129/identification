#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-07-20 15:27
# @Author: Rangers
# @Site: 
# @File: pdf_deal.py

import fitz
from zhconv import convert


def has_images_in_pdf(binary_pdf):
    pdf_document = fitz.open(stream=binary_pdf)

    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        images = page.get_images(full=True)

        if images:
            pdf_document.close()
            return True

    pdf_document.close()
    return False


def extract_text_from_pdf(binary_pdf, is_convert=True):
    pdf_document = fitz.open(stream=binary_pdf)
    num_pages = pdf_document.page_count

    pdf_text = ""

    for page_num in range(num_pages):
        page = pdf_document.load_page(page_num)
        page_text = page.get_text()
        if is_convert:
            pdf_text += convert(page_text, "zh-hans")
        else:
            pdf_text += page_text

    pdf_document.close()
    return pdf_text


def extract_images_from_pdf(binary_pdf):
    pdf_document = fitz.open(stream=binary_pdf)
    num_pages = pdf_document.page_count

    images = []

    for page_num in range(num_pages):
        page = pdf_document.load_page(page_num)
        img_list = page.get_images(full=True)

        for img in img_list:
            images.append(img)

    pdf_document.close()
    return images


if __name__ == '__main__':
    with open("../data/agree/其他.pdf", "rb") as f:
        data_bytes = f.read()
    # resp = extract_images_from_pdf(data_bytes)
    resp = extract_text_from_pdf(data_bytes)
    print(resp)
