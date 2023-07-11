#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-06-06 17:34
# @Author: Rangers
# @Site: 
# @File: identification.py
import base64
import io
import json
from config import baidu_client, baidu_image_client, baidu_face_client
import requests
from pdf2image import convert_from_bytes
from PIL import Image
from docx import Document
from urllib.parse import urlparse
import platform
from core.const import RespType
from server.bodys import InterfaceError
from core.const import degree_header, birth_cert_header, passport_header, hk_macau_header


# pdf转图片
def pdf_to_image_stream(image_bytes, page=1):
    if platform.system().lower() == "windows":
        images = convert_from_bytes(image_bytes, poppler_path="D:\\Program Files (x86)\\poppler-23.05.0\\Library\\bin")
    else:
        images = convert_from_bytes(image_bytes)
    # 多页拼接
    # if len(images) > 2:
    #     images = images[:2]
    images = images[:page]
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
    # target_height = 800
    # target_width = 600
    # resize_image = concatenated_image.resize((target_width, target_height), resample=Image.LANCZOS)
    stream = io.BytesIO()
    # resize_image.save(stream, format="PNG", quality=90)
    concatenated_image.save(stream, format="PNG", quality=90)
    image_stream = stream.getvalue()
    image_stream = image_procedure(image_bytes=image_stream)
    return image_stream


# 文件格式转换逻辑
def change_format(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        return False
    image_bytes = resp.content
    url_path = urlparse(url).path
    if url_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
        # 图片->转换大小
        image = image_procedure(image_bytes)
    elif url_path.lower().endswith(".pdf"):
        # pdf，转图片
        image = pdf_to_image_stream(image_bytes)
    elif url_path.lower().endswith(".doc"):
        # word，转图片
        image = word_to_image(image_bytes)
    else:
        return False
    return image


# 图片大小处理
def image_procedure(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    # 获取图像的原始尺寸
    original_width, original_height = image.size
    # 判断图像是否需要调整大小
    target_height, target_width = original_height, original_width
    # if original_width > 1080 or original_height > 1920:
    while True:
        image_size = (target_height * target_width * 3) / (1024 * 1024)
        if image_size < 6:
            break
        target_height *= 0.95
        target_width *= 0.95

    # 超过200万像素
    if target_height != original_height or target_width != original_width:
        resized_image = image.resize((int(target_width), int(target_height)))
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


def read_doc(url):
    pass


# 身份证
def deal_id_card(data, image=True):
    response_data = {}
    if image:
        resp = baidu_client.multi_idcard(image=data, options={"detect_risk": "true", "detect_quality": "true",
                                                              "detect_direction": "true"})
    else:
        resp = baidu_client.multi_idcardUrl(url=data, options={"detect_risk": "true", "detect_quality": "true",
                                                               "detect_direction": "true"})
    # 直接返回内部错误
    if resp.get("error_code"):
        return InterfaceError(code=resp.get("error_code"), message=resp.get("error_msg"))
    results = resp["words_result"]
    if not results:
        return None
    for result in results:
        status = result["card_info"]["image_status"]
        # if status not in ["normal", "reverse_side","unknown"]:
        if status in ["other_type_card"]:
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


# 出生证
def deal_birth_cert(data, image=True):
    response_data = {key: "" for key in birth_cert_header}
    if image:
        resp = baidu_client.birthCertificate(image=data)
    else:
        resp = baidu_client.birthCertificateUrl(url=data)
    if resp.get("error_code"):
        return InterfaceError(code=resp.get("error_code"), message=resp.get("error_msg"))
    results = resp.get("words_result")
    if not results:
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


# 护照
def deal_passport(data, image=True):
    response_data = {key: "" for key in passport_header}
    if image:
        resp = baidu_client.passport(image=data)
    else:
        resp = baidu_client.passportUrl(url=data)
    if resp.get("error_code"):
        return InterfaceError(code=resp.get("error_code"), message=resp.get("error_msg"))
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


def deal_HkMcau_permit2(image_bytes):
    response_data = {key: "" for key in hk_macau_header}
    resp = baidu_client.accurate(image_bytes)
    if resp.get("error_code"):
        return InterfaceError(code=resp.get("error_code"), message=resp.get("error_msg"))
    results = resp["words_result"]
    if not results:
        return None
    long_strings = [result["words"] for result in results]
    long_string = ",".join(long_strings)
    if "签注" in long_string or "旅游" in long_string or "往来港澳通行证" not in long_string:
        # 背面
        return RespType.HkMacaoPermitBack
    else:
        resp = baidu_client.HKMacauExitentrypermit(image=image_bytes)
        results = resp["words_result"]
        response_data["name"] = results["NameChn"].get("words")
        response_data["pinyin"] = results["NameEng"].get("words")
        response_data["birth"] = results["Birthday"].get("words")
        response_data["gender"] = results["Sex"].get("words")
        valid_date = results["ValidDate"]["words"].split("-")
        response_data["termBegins"] = valid_date[0]
        response_data["endOfTerm"] = valid_date[1]
        response_data["issueLocation"] = results["Address"].get("words")
        response_data["cardNum"] = results["CardNum"].get("words")
        return response_data


# 港澳通行证
def deal_HkMcau_permit(image_bytes):
    response_data = {key: "" for key in hk_macau_header}
    resp = baidu_client.HKMacauExitentrypermit(image=image_bytes)
    if resp.get("error_code"):
        return InterfaceError(code=resp.get("error_code"), message=resp.get("error_msg"))
    results = resp["words_result"]
    if not results:
        return None
    for key, value in results.items():
        if not value:
            return RespType.HkMacaoPermitBack
        elif not value.get("words"):
            return RespType.HkMacaoPermitBack
    response_data["name"] = results["NameChn"].get("words")
    response_data["pinyin"] = results["NameEng"].get("words")
    response_data["birth"] = results["Birthday"].get("words")
    response_data["gender"] = results["Sex"].get("words")
    valid_date = results["ValidDate"]["words"].split("-")
    response_data["termBegins"] = valid_date[0]
    response_data["endOfTerm"] = valid_date[1]
    response_data["issueLocation"] = results["Address"].get("words")
    response_data["cardNum"] = results["CardNum"].get("words")
    return response_data


# 处理各种格式学位认证报告
def deal_degree_report(image_bytes):
    resp = baidu_client.accurate(image_bytes)
    if resp.get("error_code"):
        return InterfaceError(code=resp.get("error_code"), message=resp.get("error_msg"))
    results = resp.get("words_result")
    if not results:
        return None
    long_strings = [result["words"] for result in results]
    long_string = ",".join(long_strings)
    if "中国高等教育学位认证报告" in long_string:
        degree_type = 1
    elif "教育部学位与研究生教育发展中心" in long_string:
        degree_type = 2
    elif "中国高等教育学位在线验证报告" in long_string:
        degree_type = 3
    else:
        degree_type = 0
    response_data = parse_degree_report_type(long_strings, degree_type=degree_type)
    return response_data


# 解析学位认证报告
def parse_degree_report_type(long_strings, degree_type=0):
    response_data = {key: "" for key in degree_header}
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
            elif string.startswith("姓名") or string.startswith("名"):
                response_data["name"] = split_s[-1].strip()
            elif string.startswith("报告编号"):
                response_data["reportID"] = split_s[-1].strip()
            elif string.startswith("打印日期"):
                response_data["printDate"] = split_s[-1].strip()
            elif string.startswith("性别") or string.startswith("别"):
                response_data["gender"] = split_s[-1].strip()
            elif string.startswith("出生日期"):
                response_data["birth"] = split_s[-1].strip()
            elif string.startswith("学位授予单位"):
                # response_data["degreeIssuer"] = split_s[-1].strip()
                response_data["degreeAwardingUnit"] = split_s[-1].strip()
            elif string.startswith("学位层级"):
                response_data["degreeLevel"] = split_s[-1].strip()
            elif string.startswith("学科门类"):
                # response_data["degreeClass"] = split_s[-1].strip()
                response_data["major"] = split_s[-1].strip()
            elif string.startswith("学科专业"):
                # response_data["degreeMajor"] = split_s[-1].strip()
                response_data["subjectCategory"] = split_s[-1].strip()
            elif string.startswith("获学位年份"):
                # response_data["degreeGetDate"] = split_s[-1].strip()
                response_data["degreeYear"] = split_s[-1].strip()
            elif string.startswith("学位证书"):
                response_data["degreeID"] = split_s[-1].strip()
            else:
                pass
    elif degree_type == 2:
        for index, string in enumerate(long_strings):
            if ":" in string:
                split_s = string.split(":")
            else:
                split_s = string.split("：")
            if string.startswith("教育部学位与研究生教育发展中心"):
                response_data["report_title"] = string
            elif string.startswith("姓名"):
                response_data["name"] = split_s[-1].strip()
            elif string.startswith("性别"):
                response_data["gender"] = split_s[-1].strip()
            elif string.startswith("认证日期"):
                response_data["printDate"] = split_s[-1].strip()
            elif string.startswith("验证编码"):
                if split_s[-1].strip():
                    response_data["reportID"] = split_s[-1].strip()
                else:
                    response_data["reportID"] = long_strings[index + 1]
            elif string.startswith("出生日期"):
                response_data["birth"] = split_s[-1].strip()
            elif string.startswith("学位层级"):
                response_data["degreeLevel"] = split_s[-1].strip()
            elif string.startswith("学位授予单位"):
                # response_data["degreeIssuer"] = split_s[-1]
                response_data["degreeAwardingUnit"] = split_s[-1].strip()
            elif string.startswith("专业（"):
                # response_data["degreeMajor"] = split_s[-1]
                response_data["subjectCategory"] = split_s[-1].strip()
            elif string.startswith("学科门类"):
                # response_data["degreeClass"] = split_s[-1]
                response_data["major"] = split_s[-1].strip()
            elif string.startswith("获学位年份"):
                # response_data["degreeGetDate"] = split_s[-1]
                response_data["degreeYear"] = split_s[-1].strip()
            elif string.startswith("证书编号"):
                response_data["degreeID"] = split_s[-1].strip()
            else:
                pass
    elif degree_type == 3:
        for index, string in enumerate(long_strings):
            if ":" in string:
                split_s = string.split(":")
            else:
                split_s = string.split("：")
            if string.endswith("在线验证报告"):
                response_data["report_title"] = string
            elif string.startswith("更新日期"):
                response_data["printDate"] = split_s[-1].strip()
            elif string.startswith("姓名"):
                response_data["name"] = long_strings[index + 1]
            elif string.startswith("性别"):
                response_data["gender"] = long_strings[index + 1]
            elif string.startswith("出生日期"):
                response_data["birth"] = long_strings[index + 1]
            elif string.startswith("获学位日期"):
                response_data["degreeYear"] = long_strings[index + 1]
            elif string.startswith("学位授予单位"):
                response_data["degreeAwardingUnit"] = long_strings[index + 1]
            elif string.startswith("所授学位"):
                response_data["major"] = long_strings[index + 1]
            elif string.startswith("学位证书编号"):
                response_data["degreeID"] = long_strings[index + 1]
            else:
                continue
    return response_data


# 图片纠正
def doc_crop_enhance(image_bytes, option=None):
    if not option:
        resp = baidu_client.doc_crop_enhance(image_bytes)
    else:
        resp = baidu_client.doc_crop_enhance(image_bytes, options=option)
    if resp.get("error_code"):
        return InterfaceError(code=resp.get("error_code"), message=resp.get("error_msg"))
    image_b64 = resp.get("image_processed")
    if not image_b64:
        return None
    del resp["log_id"]
    return resp


# 处理结婚证
def deal_marriage_cert(data):
    response_data = {}
    resp = baidu_client.marriage_certificate(image=data)
    word_result = resp.get("words_result")
    if not word_result:
        return None
    if resp.get("error_code"):
        return InterfaceError(code=resp.get("error_code"), message=resp.get("error_msg"))
    try:
        response_data["husband_name"] = word_result["姓名_男"][0]["word"]
        response_data["husband_id_card"] = word_result["身份证件号_男"][0]["word"]
        response_data["husband_birth"] = word_result["出生日期_男"][0]["word"]
        response_data["husband_nationality"] = word_result["国籍_男"][0]["word"]
        response_data["wife_name"] = word_result["姓名_女"][0]["word"]
        response_data["wife_id_card"] = word_result["身份证件号_女"][0]["word"]
        response_data["wife_birth"] = word_result["出生日期_女"][0]["word"]
        response_data["wife_nationality"] = word_result["国籍_女"][0]["word"]
        response_data["marriage_certificate_number"] = word_result["结婚证字号"][0]["word"]
        response_data["holder_of_certificate"] = word_result["持证人"][0]["word"]
    except Exception as err:
        return InterfaceError(code=-1, message="")
    return response_data


# 人脸相似度对比
def face_compare(id_card_bytes, recent_bytes):
    image1 = {
        "image": base64.b64encode(id_card_bytes).decode(),
        "image_type": "BASE64"
    }
    image2 = {
        "image": base64.b64encode(recent_bytes).decode(),
        "image_type": "BASE64"
    }
    resp = baidu_face_client.match([image1, image2])
    if resp["error_code"] != 0:
        return InterfaceError(code=resp.get("error_code"), msg=resp.get("error_msg"))
    return resp


if __name__ == '__main__':
    # with open("../data/近期证件照/反面（配偶）（贺之讯）_2.jpg", "rb") as f:
    #     id_image_bytes = f.read()
    # with open("../data/近期证件照/近期证件照片（贺之讯）.jpg", "rb") as f:
    #     recent_image_bytes = f.read()
    # face_compare(id_image_bytes, recent_image_bytes)
    with open("../data/结婚证/结婚证（只需信息页）（张菲菲）_1.JPG","rb") as f:
        image = f.read()
    image_bytes = image_procedure(image)
    deal_marriage_cert(image_bytes)
