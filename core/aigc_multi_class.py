#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-06-28 10:37
# @Author: Rangers
# @Site: AIGC生产线，多类型文件识别
# @File: aigc_multi_class.py
import platform
import subprocess

import requests
import zipfile
import rarfile
from pdf2image import convert_from_bytes
import io
from core.identification import image_procedure
import win32com.client as win32
from docx import Document
from config import baidu_client
from openpyxl import load_workbook
from xlrd import open_workbook
from core.exception import InterfaceError
from pptx import Presentation


# docx:6390, pdf 4007, jpg 1970,doc 1934,png 1543,
# pptx 520,xlsx 255, txt 98, ppt 59
# xls 59, zip 40, rar 10
# 处理文件，调用接口，

def pdf_to_image_page_stream(data_bytes, page=3):
    # pdf识别内容,使用通用接口,最多识别三也pdf
    if platform.system().lower() == "windows":
        images = convert_from_bytes(data_bytes, poppler_path="D:\\Program Files (x86)\\poppler-23.05.0\\Library\\bin")
    else:
        images = convert_from_bytes(data_bytes)
    if page:
        images = images[:page]
    # 调整大小
    stream = io.BytesIO()
    data = []
    for image in images:
        image.save(stream, format="PNG", quality=90)
        image_stream = stream.getvalue()
        # 改变大小,使之适配
        image_bytes = image_procedure(image_bytes=image_stream)
        resp = baidu_client.accurate(image_bytes)
        if resp.get("error_code"):
            return InterfaceError(code=resp.get("error_code"), message=resp.get("error_msg"))
        results = resp["words_result"]
        if not results:
            continue
        long_strings = [result["words"] for result in results]
        long_strings = "\n".join(long_strings)
        data.append(long_strings)
    return data


def image_stream_deal(data_bytes):
    image_bytes = image_procedure(image_bytes=data_bytes)
    resp = baidu_client.accurate(image_bytes)
    if resp.get("error_code"):
        return InterfaceError(code=resp.get("error_code"), message=resp.get("error_msg"))
    results = resp["words_result"]
    if not results:
        return None
    long_strings = [result["words"] for result in results]
    long_strings = "\n".join(long_strings)
    return [long_strings]


def doc2content(data_bytes):
    # doc文件读取
    doc_stream = io.BytesIO(data_bytes)
    data = []
    if platform.system().lower() == "windows":
        word_app = win32.Dispatch("Word.Application")
        doc = word_app.Documents.Open(doc_stream)
        for paragraph in doc.Paragraphs:
            text = paragraph.Range.Text.strip()
            if text.strip():
                data.append(text.strip())
        doc.Close()
        word_app.Quit()
    else:
        output = subprocess.check_output(["antiword", "-"], input=doc_stream.getvalue())
        text = output.decode("utf-8")
        if text.strip():
            data.append(text)
    return ["\n".join(data)]


def docx2content(data_bytes, page=None):
    document = Document(io.BytesIO(data_bytes))
    if page:
        paragraphs = document.paragraphs[:page]
    else:
        paragraphs = document.paragraphs
    data = []
    for index, paragraph in enumerate(paragraphs):
        if paragraph.text:
            data.append(paragraph.text)
    result = "\n".join(data)
    return [result]


def xlsx2content(data_types):
    excel_file = io.BytesIO(data_bytes)
    wb = load_workbook(excel_file)
    ws = wb.active
    max_rows = ws.max_row
    max_cols = ws.max_column
    data = []
    for col_index in range(1, max_cols + 1):
        for row_index in range(1, max_rows + 1):
            lattice = ws.cell(row=row_index, column=col_index)
            if not lattice.value:
                continue
            elif not lattice.value.strip():
                continue
            data.append(lattice.value.strip())
    result = ["\n".join(data)]
    return result


def xls2content(data_types):
    excel_file = io.BytesIO(data_bytes)
    data = open_workbook(file_contents=excel_file.read())
    table = data.sheets()[0]
    n_rows = table.nrows
    n_cols = table.ncols
    data = []
    for row_num in range(n_rows):
        row = table.row_values(row_num)
        if row:
            for i in range(n_cols):
                if row[i].strip():
                    data.append(row[i].strip())
    return data


def txt2content(data_types):
    stream = io.BytesIO(data_bytes)
    text = stream.read().decode("utf-8")
    return text


def ppt_or_pptx2content(data_types):
    stream = io.BytesIO(data_bytes)
    presentation = Presentation(stream)
    data = []
    for slide in presentation.slides:
        if not hasattr(slide, "shapes"):
            continue
        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text_frame.text
                if not text.strip():
                    continue
                data.append(text)
    return ["\n".join(data)]


def distribute_file_class(url):
    pass


if __name__ == '__main__':
    # with open("../data/dismantle/1687184654498.doc", "rb") as f:
    #     data_bytes = f.read()
    with open("../data/dismantle/1687184654498.doc", "rb") as f:
        data_bytes = f.read()
    # test = doc2content(data_bytes)
    # test = pdf_to_image_page_stream(data_bytes)
    # test = image_stream_deal(data_bytes=data_bytes)
    test = doc2content(data_bytes=data_bytes)
    # test = ppt_or_pptx2content(data_types=data_bytes)
    # test = xlsx2content(data_bytes)
    # test = xls2content(data_bytes)
    # test = ppt_or_pptx2content(data_bytes)
    print(test)
    print(len(test))
