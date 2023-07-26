#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-07-20 15:27
# @Author: Rangers
# @Site: 
# @File: pdf_deal.py
import io

import fitz
from zhconv import convert
from config import baidu_client


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


def norm_pdf_image_deal(image_bytes,is_convert=True):
    resp = baidu_client.basicAccurate(image_bytes)
    words_result = resp.get("words_result")
    if not words_result:
        raise Exception("error format")
    data = []
    for obj in words_result:
        words = obj.get("words")
        if not words:
            continue
        if is_convert:
            text = convert(words, "zh-hans")
            data.append(text)
        else:
            data.append(words)
    return "\n".join(data)

