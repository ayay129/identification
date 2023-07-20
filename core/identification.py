#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-06-06 17:34
# @Author: Rangers
# @Site: 
# @File: identification.py
import base64
import io
import re
import sys

if sys.platform != "win32":
    import pyheif
from config import baidu_client, baidu_image_client, baidu_face_client
from rembg import remove
import requests
from pdf2image import convert_from_bytes
from PIL import Image
from docx import Document
from urllib.parse import urlparse
import platform
from core.const import RespType, ReqType
from server.bodys import InterfaceError
from core.const import degree_header, birth_cert_header, passport_header, hk_macau_header
from core.cut_api import cut_tool
import json


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
    stream = io.BytesIO()
    concatenated_image.save(stream, format="PNG", quality=90)
    image_stream = stream.getvalue()
    image_stream = image_procedure(image_bytes=image_stream)
    image_stream = remove_transparent_pixels(image_stream, target_color=(255, 255, 255, 255))
    return image_stream


def pdf2_to_image_stream(image_bytes, page=2):
    if platform.system().lower() == "windows":
        images = convert_from_bytes(image_bytes, poppler_path="D:\\Program Files (x86)\\poppler-23.05.0\\Library\\bin")
    else:
        images = convert_from_bytes(image_bytes)
    images = images[:page]
    images_data = []
    for index, image in enumerate(images):
        # 调整大小
        stream = io.BytesIO()
        image.save(stream, format="PNG", quality=90)
        image_stream = stream.getvalue()
        image_stream = image_procedure(image_bytes=image_stream)
        # image_stream = remove(image_stream)
        # image_stream = remove_transparent_pixels(image_stream, target_color=(255, 255, 255, 255))
        images_data.append(image_stream)
    return images_data


# 文件格式转换逻辑
def change_format(url, compress=True):
    resp = requests.get(url)
    if resp.status_code != 200:
        return False
    image_bytes = resp.content
    url_path = urlparse(url).path
    if url_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
        # 图片->转换大小
        if compress:
            image = image_procedure(image_bytes)
        else:
            image = image_bytes
    elif url_path.lower().endswith("heic"):
        image_source = heif_to_png(image_bytes)
        if compress:
            image = image_rotate(image_source)
        else:
            image = image_source
    elif url_path.lower().endswith(".pdf"):
        # pdf，转图片
        image = pdf2_to_image_stream(image_bytes)
    elif url_path.lower().endswith(".doc"):
        # word，转图片
        image = word_to_image(image_bytes)
    else:
        return False
    return image


def heif_to_png(heif_data):
    heif_file = pyheif.read(heif_data)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    output = io.BytesIO()
    image.save(output, format="PNG")
    png_data = output.getvalue()
    return png_data


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
def deal_id_card(data):
    response_data = {}
    if not isinstance(data, list):
        data = [data]
    for image_bytes in data:
        resp = baidu_client.multi_idcard(image=image_bytes, options={"detect_risk": "true", "detect_quality": "true",
                                                                     "detect_direction": "true"})
        # 直接返回内部错误
        if resp.get("error_code"):
            continue
        results = resp["words_result"]
        if not results:
            continue
        for result in results:
            status = result["card_info"]["image_status"]
            # if status not in ["normal", "reverse_side","unknown"]:
            if status in ["other_type_card", "non_idcard"]:
                # return CardResponse(code=1, type=0, message="Recognize Failure. Cause {}".format(status))
                continue
            card_type = result["card_info"]["card_type"]
            card_result = result["card_result"]
            if not card_result:
                continue
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
    if not response_data:
        return None
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
def deal_HkMcau_permit(image_list):
    # response_data = {key: "" for key in hk_macau_header}
    if not isinstance(image_list, list):
        image_list = [image_list]
    response_data = {}
    is_back = False
    for image_bytes in image_list:
        resp = baidu_client.HKMacauExitentrypermit(image=image_bytes)
        if resp.get("error_code"):
            continue
        results = resp["words_result"]
        if not results:
            continue
        values = []
        for key, value in results.items():
            values.append(value)
        if not all(values):
            is_back = True
        elif not all([value.get("words") for value in values]):
            is_back = True
        else:
            response_data["name"] = results["NameChn"].get("words")
            response_data["pinyin"] = results["NameEng"].get("words")
            response_data["birth"] = results["Birthday"].get("words")
            response_data["gender"] = results["Sex"].get("words")
            valid_date = results["ValidDate"]["words"].split("-")
            response_data["termBegins"] = valid_date[0]
            response_data["endOfTerm"] = valid_date[1]
            response_data["issueLocation"] = results["Address"].get("words")
            response_data["cardNum"] = results["CardNum"].get("words")
    return response_data, is_back


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


def deal_graduation_and_degree_cert(image_bytes, depth=0):
    if depth >= 4:
        return RecursionError("90度旋转{}次均无法识别证件内容".format(depth))
    response_data = {}
    resp = baidu_client.accurate(image_bytes)
    words_result = resp.get("words_result")
    long_strings = [words["words"] for words in words_result]
    long_string = "|".join(long_strings)
    if re.findall(r"毕业证书", long_string):
        name_list = [r"学生\|([\u4e00-\u9fa5]+?)\|", r"学生([\u4e00-\u9fa5]+?)\|", r"\|([\u4e00-\u9fa5]{2,4})\|性别"]
        level_list = [r"(本科)|(硕士)|(博士)", r"(本\|科)|(硕\|士)|(博\|士)"]
        college_list = [r"校名[:：\s](.*大学)", r"[校\|名]+[:：\s](.*大学)", r"校名[:：\s](.*大學)",
                        r"校\|名[:：\s](.*大學)",
                        r".*\|(.*大學)\|"]
    elif re.findall(r"学位证书", long_string):
        # '王迪辛|,男，|一九七六|年十二月生。自|一九九四|年九月至一九九九年六月|在|浙江大学|信息与电子工程系|信息电子技术|完成了*年制本科学习计划，业已毕业。|经审核符合《中华人民共和国学位条例》|的规定，授予|ヱ|学学士学位。|学士学位证书|浙江大学|学位评定委员会主席|(普通高等教育本科毕业生)|潘鹤|1999年6月25日|证书编号：103314991197'
        name_list = [r"([\u4e00-\u9fa5]{2,5})[\|]*[，,]*[男女系][，,]*.*?\|", r"([\u4e00-\u9fa5]{2,4})[男女]"]
        level_list = [r"(学士)|(硕士)|(博士)", r"(学\|士)|(硕\|士)|(博\|士)"]
        college_list = [r"在*([\u4e00-\u9fa5]{2,6}大学)"]
    else:
        rotate_image_bytes = image_rotate(image_bytes)
        return deal_graduation_and_degree_cert(rotate_image_bytes, depth=depth + 1)
    student = match(name_list, long_string)
    if student:
        response_data["student"] = re.sub(r"\|+", "", student[0])
    level = match(level_list, long_string)
    if level:
        for obj in level[0]:
            if obj:
                response_data["education_level"] = re.sub(r"\|+", "", obj)
    college = match(college_list, long_string)
    if college:
        response_data["school"] = re.sub(r"\|+", "", college[0])
    if not response_data:
        rotate_image_bytes = image_rotate(image_bytes)
        return deal_graduation_and_degree_cert(rotate_image_bytes, depth=depth + 1)
    else:
        return response_data


def match(re_list, string):
    for re_match in re_list:
        resp = re.findall(re_match, string)
        if not resp:
            continue
        return resp
    else:
        return None


def image_rotate(image_bytes, angle=90):
    image = Image.open(io.BytesIO(image_bytes))
    rotated_image = image.rotate(angle, expand=True)
    output_binary = io.BytesIO()
    rotated_image.save(output_binary, format='PNG')
    output_binary.seek(0)

    # 从二进制流读取旋转后的图像数据
    rotated_image_binary = output_binary.read()
    return rotated_image_binary


# 图片合成
def merge_images(images_list: list, num=2, input_type=1):
    images = []
    for image in images_list[:num]:
        # 存在透明
        output_binary = remove(image)
        # 处理后为RGBA
        output_binary = remove_transparent_pixels(output_binary)
        if input_type == 1:
            resp = baidu_client.multi_idcard(image=output_binary,
                                             options={"detect_risk": "true", "detect_quality": "true",
                                                      "detect_direction": "true"})
            direction = resp["words_result"][0]["card_info"]["direction"]
            output_binary = rotate_id_card(output_binary, direction)
        else:
            output_binary = output_binary
        # images.append(Image.open(io.BytesIO(image_binary)).convert("RGBA"))
        images.append(Image.open(io.BytesIO(output_binary)))

    # 创建一个新的白底图像，尺寸为两张输入图片的最大宽度和最大高度
    total_height = int(sum(image.height for image in images) * 1.2)
    max_width = int(max(image.width for image in images) * 1.2)
    concatenated_image = Image.new("RGBA", (max_width, total_height), "white")

    y_offset = int(total_height * 0.1)
    for image in images:
        x_offset = int((max_width - image.width) / 2)
        concatenated_image.paste(image, (x_offset, y_offset))
        y_offset += int(image.height + total_height * 0.05)
    # 转换为RGB
    stream = io.BytesIO()
    concatenated_image.save(stream, format="PNG", quality=90)
    image_stream = stream.getvalue()
    return base64.b64encode(image_stream)


def rotate_id_card(image_bytes, direction=-1):
    if direction == 3:
        image_binary = image_rotate(image_bytes, angle=90)
    elif direction == 2:
        image_binary = image_rotate(image_bytes, angle=180)
    elif direction == 1:
        image_binary = image_rotate(image_bytes, angle=270)
    else:
        image_binary = image_bytes
    return image_binary


# 去除透明像素
def remove_transparent_pixels(image_bytes, target_color=(0, 0, 0, 0)):
    # 将二进制流转换为PIL图片对象
    image = Image.open(io.BytesIO(image_bytes))

    # 检查图像是否具有透明通道
    # if image.mode == 'RGBA':
    # 将图像转换为带有预乘透明度的RGBA模式
    image = image.convert("RGBA")

    # 获取图像中每个像素的RGBA值
    pixels = image.getdata()

    # 创建一个新的图像对象，用于存储去除透明像素后的图像
    new_image = Image.new("RGBA", image.size, "white")

    x_set, y_set = [], []
    # 遍历图像的每个像素
    for i, pixel in enumerate(pixels):
        # 检查像素的透明度
        if pixel != target_color:
            x = i % image.width
            y = i // image.width
            x_set.append(x)
            y_set.append(y)
            # 如果透明度大于0，则将像素添加到新图像中
            new_image.putpixel((x, y), pixel)

    coordinates = (min(x_set), min(y_set), max(x_set), max(y_set))
    crop_image = new_image.crop(coordinates)
    # 将新图像转换为二进制流
    output_bytes = io.BytesIO()
    crop_image.save(output_bytes, format='PNG', quality=90)
    output_bytes.seek(0)

    return output_bytes.getvalue()

    # else:
    #     图像没有透明通道，返回原始二进制流
    # return image_bytes


# 一键白底
def image_cutout(image_bytes):
    response = cut_tool.passport(image_bytes)
    if response.status_code != 200:
        raise Exception("抠图失败")
    image_b64 = json.loads(response.text)["result"]
    image = base64.b64decode(image_b64)
    output_binary = remove_transparent_pixels(image)
    return base64.b64encode(output_binary)


function_map = {
    ReqType.IdentityCard: deal_id_card,
    ReqType.BirthCert: deal_birth_cert,
    ReqType.PassPort: deal_passport,
    ReqType.HkMacaoPermit: deal_HkMcau_permit,
    ReqType.DegreeCertReport: deal_degree_report,
    ReqType.Marriage: deal_marriage_cert,
    ReqType.GraduationCert: deal_graduation_and_degree_cert,
    ReqType.DegreeCert: deal_graduation_and_degree_cert
}

# if __name__ == '__main__':
#     with open("../data/id_card/反面（子女）（唐言恢）_1.jpg", "rb") as img_file1, open(
#             "../data/id_card/反面（子女）（唐言恢）_2.jpg", "rb") as img_file2:
#         img1_bytes = img_file1.read()
#         img2_bytes = img_file2.read()
#         resp = merge_images([img1_bytes, img2_bytes])
#         print(resp)

# 学位证测试
# 毕业证测试
# for root, dirs, files in os.walk("../data/学位证"):
#     for name in files:
#         file_name = "%s/%s" % (root, name)
#         print(file_name)
#         with open(file_name, "rb") as f:
#             image = f.read()
#         if file_name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
#             # 图片->转换大小
#             images = image_procedure(image)
#         elif file_name.lower().endswith(".pdf"):
#             # pdf，转图片
#             images = pdf2_to_image_stream(image, page=1)
#         image = images[0] if isinstance(images, list) else images
#         resp = deal_graduation_and_degree_cert(image)
#         print(resp)
