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


def pdf_to_image_stream(pdf_url):
    resp = requests.get(pdf_url)
    if resp.status_code != 200:
        return None
    images = convert_from_bytes(resp.content)
    # 多页拼接
    if len(images) > 2:
        return None
    else:
        total_height = sum(image.height for image in images)
        max_width = max(image.width for image in images)
        # 拼接图,底图
        concatenated_image = Image.new("RGB", (max_width, total_height), "white")
        y_offset = 0
        # 自上而下拼接
        for image in images:
            concatenated_image.paste(image, (0, y_offset))
            y_offset += image.height
    return concatenated_image


def word_to_image(word_url):
    resp = requests.get(word_url)
    if resp.status_code != 200:
        return None
    document = Document(io.BytesIO(resp.content))
    if len(document.sections):
        return
    else:
        total_height = sum(section.page_height for section in document.sections)
        max_width = max(section.page_width for section in document.sections)
        # 拼接图,底图
        concatenated_image = Image.new('RGB', (max_width, total_height), 'white')
        y_offset = 0
        for section in document.sections:
            image = Image.new('RGB', (int(section.page_width * 2.8), int(section.page_height * 2.8)), 'white')
            concatenated_image.paste(image, (0, y_offset))
            y_offset += image.height
        return concatenated_image


def deal_id_card(url):
    response_data = {}
    resp = baidu_client.multi_idcardUrl(url=url, options={"detect_risk": "true", "detect_quality": "true",
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


def deal_birth_cert(url):
    response_data = {}
    resp = baidu_client.birthCertificateUrl(url=url)
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


def deal_password(url):
    response_data = {}
    resp = baidu_client.passportUrl(url=url)
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


def deal_HkMcau_permit(url):
    response_data = {}
    response = requests.get(url)
    if response.status_code != 200:
        return None
    resp = baidu_client.HKMacauExitentrypermit(image=response.content)
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
