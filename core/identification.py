#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-06-06 17:34
# @Author: Rangers
# @Site: 
# @File: identification.py
import io

from config import baidu_client
import requests
from pdf2image import convert_from_bytes
from PIL import Image
from docx import Document
from urllib.parse import urlparse


def pdf_to_image_stream(image_bytes):
    images = convert_from_bytes(image_bytes, poppler_path="D:\\Program Files (x86)\\poppler-23.05.0\\Library\\bin")
    # 多页拼接
    # if len(images) > 2:
    #     images = images[:2]
    images = images[:1]
    total_height = sum(image.height for image in images)
    max_width = max(image.width for image in images)
    # 拼接图,底图
    concatenated_image = Image.new("RGB", (max_width, total_height), "white")
    y_offset = 0
    # 自上而下拼接
    for image in images:
        concatenated_image.paste(image, (0, y_offset))
        y_offset += image.height
    # 调整大小
    target_height = 800
    target_width = 600
    resize_image = concatenated_image.resize((target_width, target_height), resample=Image.LANCZOS)
    stream = io.BytesIO()
    resize_image.save(stream, format="PNG", quality=90)
    image_stream = stream.getvalue()
    return image_stream


def change_format(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        return False
    image_bytes = resp.content
    url_path = urlparse(url).path
    if url_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
        image = image_procedure(image_bytes)
    elif url_path.lower().endswith(".pdf"):
        image = pdf_to_image_stream(image_bytes)
    elif url_path.lower().endswith(".doc"):
        image = word_to_image(image_bytes)
    else:
        return False
    return image


def image_procedure(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    # 获取图像的原始尺寸
    original_width, original_height = image.size

    # 判断图像是否需要调整大小
    if original_width > 800 or original_height > 600:
        # 定义目标尺寸
        target_width = 800
        target_height = 600

        # 调整图像尺寸
        resized_image = image.resize((target_width, target_height))
    else:
        # 图像不需要调整大小
        resized_image = image
    stream = io.BytesIO()
    resized_image.save(stream, format="PNG", quality=90)
    image_stream = stream.getvalue()
    return image_stream


def word_to_image(image_bytes):
    document = Document(io.BytesIO(image_bytes))
    sections = document.sections
    # if len(sections) > 2:
    #     sections = sections[:2]
    sections = sections[:1]
    total_height = sum(section.page_height for section in sections)
    max_width = max(section.page_width for section in sections)
    # 拼接图,底图
    concatenated_image = Image.new('RGB', (max_width, total_height), 'white')
    y_offset = 0
    for section in sections:
        image = Image.new('RGB', (int(section.page_width * 2.8), int(section.page_height * 2.8)), 'white')
        concatenated_image.paste(image, (0, y_offset))
        y_offset += image.height
    return concatenated_image


def deal_id_card(data, image=True):
    response_data = {}
    if image:
        resp = baidu_client.multi_idcard(image=data, options={"detect_risk": "true", "detect_quality": "true",
                                                              "detect_direction": "true"})
    else:
        resp = baidu_client.multi_idcardUrl(url=data, options={"detect_risk": "true", "detect_quality": "true",
                                                               "detect_direction": "true"})
    results = resp["words_result"]
    if not results:
        # return CardResponse(code=0, type=1, message="Recognize Failure. Cause Unknown")
        return None
    for result in results:
        status = result["card_info"]["image_status"]
        if status not in ["normal", "reverse_side"]:
            # return CardResponse(code=1, type=0, message="Recognize Failure. Cause {}".format(status))
            return None
        card_type = result["card_info"]["card_type"]
        card_result = result["card_result"]
        if card_type == "idcard_front":
            # 正面
            response_data["name"] = card_result["姓名"]["words"]
            response_data["gender"] = card_result["性别"]["words"]
            response_data["nationality"] = card_result["民族"]["words"]
            response_data["birth"] = card_result["出生"]["words"]
            response_data["address"] = card_result["住址"]["words"]
            response_data["cardNum"] = card_result["公民身份号码"]["words"]
        else:
            # 反面
            response_data["issuingAuthority"] = card_result["签发机关"]["words"]
            response_data["termBegins"] = card_result["签发日期"]["words"]
            response_data["endOfTerm"] = card_result["失效日期"]["words"]
    return response_data


def deal_birth_cert(data, image=True):
    response_data = {}
    if image:
        resp = baidu_client.birthCertificate(image=data)
    else:
        resp = baidu_client.birthCertificateUrl(url=data)
    results = resp.get("words_result")
    if not results:
        # return CardResponse(code=1, type=0, message="Recognize Failure. Cause Unknown")
        return None
    # 原始
    response_data["newborn"] = results["BabyName"]["words"]
    response_data["gender"] = results["BabySex"]["words"]
    response_data["birth"] = results["BabyBirthday"]["words"]
    response_data["motherName"] = results["MotherName"]["words"]
    response_data["motherNum"] = results["MotherID"]["words"]
    response_data["fatherName"] = results["FatherName"]["words"]
    response_data["fatherNum"] = results["FatherID"]["words"]
    # 新增
    response_data["code"] = results["Code"]["words"]
    response_data["hospital"] = results["Hospital"]["words"]
    response_data["gestationalAge"] = results["GestationalAge"]["words"]
    response_data["birthWeight"] = results["BirthWeight"]["words"]
    response_data["birthLength"] = results["BirthLength"]["words"]
    response_data["birthProvince"] = results["BirthProvince"]["words"]
    response_data["birthCity"] = results["BirthCity"]["words"]
    response_data["birthCounty"] = results["BirthCounty"]["words"]
    response_data["motherAge"] = results["MotherAge"]["words"]
    response_data["motherNationality"] = results["MotherNationality"]["words"]
    response_data["motherEthnic"] = results["MotherEthnic"]["words"]
    response_data["motherAddress"] = results["MotherAddress"]["words"]
    response_data["fatherAge"] = results["FatherAge"]["words"]
    response_data["fatherNationality"] = results["FatherNationality"]["words"]
    response_data["fatherEthnic"] = results["FatherEthnic"]["words"]
    response_data["fatherAddress"] = results["FatherAddress"]["words"]
    return response_data


def deal_passport(data, image=True):
    response_data = {}
    if image:
        resp = baidu_client.passport(image=data)
    else:
        resp = baidu_client.passportUrl(url=data)
    results = resp["words_result"]
    if not results:
        return None
    # 原始字段
    response_data["name"] = results["姓名"]["words"]
    response_data["pinyin"] = results["姓名拼音"]["words"]
    response_data["birth"] = results["生日"]["words"]
    response_data["birthLocation"] = results["出生地点"]["words"]
    response_data["issueLocation"] = results["护照签发地点"]["words"]
    response_data["issueDate"] = results["签发日期"]["words"]
    response_data["valid"] = results["有效期至"]["words"]
    # 新增
    response_data["gender"] = results["性别"]["words"]
    response_data["countryCode"] = results["国家码"]["words"]
    response_data["MRZCode2"] = results["MRZCode2"]["words"]
    response_data["issuingAuthority"] = results["签发机关"]["words"]
    response_data["MRZCode1"] = results["MRZCode1"]["words"]
    response_data["cardNum"] = results["护照号码"]["words"]
    response_data["nationality"] = results["国籍"]["words"]
    return response_data


def deal_HkMcau_permit(image_bytes):
    response_data = {}
    resp = baidu_client.HKMacauExitentrypermit(image=image_bytes)
    results = resp["words_result"]
    if not results:
        return None
        # return CardResponse(code=1, type=0, message="Recognize Failure. Cause Unknown")
    response_data["name"] = results["NameChn"]["words"]
    response_data["pinyin"] = results["NameEng"]["words"]
    response_data["birth"] = results["Birthday"]["words"]
    response_data["gender"] = results["Sex"]["words"]
    valid_date = results["ValidDate"]["words"].split("-")
    response_data["termBegins"] = valid_date[0]
    response_data["endOfTerm"] = valid_date[1]
    response_data["issueLocation"] = results["Address"]["words"]
    response_data["cardNum"] = results["CardNum"]["words"]
    return response_data


def deal_degree_report(image_bytes):
    response_data = {}
    # resp = baidu_client.accuratePdf(pdf_file=image_bytes)
    resp = baidu_client.accurate(image_bytes)
    results = resp.get("words_result")
    long_strings = [result["words"] for result in results]
    long_string = ",".join(long_strings)
    if "中国高等教育学位认证报告" in long_string:
        degree_type = 1
    elif "教育部学位与研究生教育发展中心" in long_string:
        degree_type = 2
    else:
        degree_type = 0
    response_data = parse_degree_report_type(long_strings, degree_type=degree_type)
    return response_data


def parse_degree_report_type(long_strings, degree_type=0):
    response_data = {}
    if not degree_type:
        return None
    if degree_type == 1:
        for string in long_strings:
            if ":" in string:
                split_s = string.split(":")
            else:
                split_s = string.split("：")
            if string.startswith("中国高等教育"):
                response_data["report_title"] = string
            elif string.startswith("姓名"):
                response_data["name"] = split_s[-1].strip()
            elif string.startswith("报告编号"):
                response_data["reportID"] = split_s[-1].strip()
            elif string.startswith("打印日期"):
                response_data["printDate"] = split_s[-1].strip()
            elif string.startswith("性别"):
                response_data["gender"] = split_s[-1].strip()
            elif string.startswith("出生日期"):
                response_data["birth"] = split_s[-1].strip()
            elif string.startswith("学位授予单位"):
                response_data["degreeIssuer"] = split_s[-1].strip()
            elif string.startswith("学位层级"):
                response_data["degreeLevel"] = split_s[-1].strip()
            elif string.startswith("学位门类"):
                response_data["degreeClass"] = split_s[-1].strip()
            elif string.startswith("学位专业"):
                response_data["degreeMajor"] = split_s[-1].strip()
            elif string.startswith("获学位年份"):
                response_data["degreeGetDate"] = split_s[-1].strip()
            elif string.startswith("学位证书"):
                response_data["degreeID"] = split_s[-1].strip()
            else:
                pass
    elif degree_type == 2:
        for string in long_strings:
            if ":" in string:
                split_s = string.split(":")
            else:
                split_s = string.split("：")
            if string.startswith("教育部学位与研究生教育发展中心"):
                response_data["report_title"] = string
            elif string.startswith("姓名"):
                response_data["name"] = split_s[-1]
            elif string.startswith("性别"):
                response_data["gender"] = split_s[-1]
            elif string.startswith("出生日期"):
                response_data["birth"] = split_s[-1]
            elif string.startswith("学位层级"):
                response_data["degreeLevel"] = split_s[-1]
            elif string.startswith("学位授予单位"):
                response_data["degreeIssuer"] = split_s[-1]
            elif string.startswith("专业（"):
                response_data["degreeMajor"] = split_s[-1]
            elif string.startswith("学科门类"):
                response_data["degreeClass"] = split_s[-1]
            elif string.startswith("获学位年份"):
                response_data["degreeGetDate"] = split_s[-1]
            elif string.startswith("证书编号"):
                response_data["degreeID"] = split_s[-1]
            else:
                pass
    return response_data


# if __name__ == '__main__':
#     # with open("../data/degree/本科学位认证报（王迪辛）.pdf", "rb") as f:
#     #     pdf = f.read()
#     with open("../data/degree/复旦大学硕士学位认证报告（我司代办）.pdf", "rb") as f:
#         pdf = f.read()
#     image = pdf_to_image_stream(pdf)
#     deal_degree_report(image)
