#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-07-20 15:37
# @Author: Rangers
# @Site: 
# @File: email_server.py

from server.api_v1_0 import app
from server.bodys import InterfaceError, BaseResponse
from core.identification import pdf2_to_image_stream
from core.const import ReqType, RETCODE, err_msg, RespType
from server.bodys import ConvertReq
from core.pdf_deal import extract_text_from_pdf, has_images_in_pdf, norm_pdf_image_deal
from fitz.fitz import EmptyFileError
import requests


@app.post("/email/read")
def email(request: ConvertReq):
    resp = requests.get(url=request.url)
    if resp.status_code != 200:
        return InterfaceError(code=RETCODE.GET_ERROR, message=err_msg[RETCODE.GET_ERROR].format(request.url))
    # 弃用，使用纯图片OCR
    # try:
    #     has_image = has_images_in_pdf(binary_pdf=resp.content)
    # except EmptyFileError as err:
    #     return InterfaceError(code=RETCODE.ERROR, message=err_msg[RETCODE.ERROR] + "文件为空")
    # if has_image:
    #     # pdf中有图片
    #     data = []
    #     images = pdf2_to_image_stream(resp.content)
    #     for image in images:
    #         content = norm_pdf_image_deal(image, is_convert=request.convert if request.convert else True)
    #         data.append(content)
    #     return BaseResponse(code=RETCODE.OK, message=err_msg[RETCODE.OK], data="\n\n".join(data))
    # else:
    #     resp = extract_text_from_pdf(binary_pdf=resp.content, is_convert=request.convert if request.convert else True)
    #     return BaseResponse(code=RETCODE.OK, message=err_msg[RETCODE.OK], data=resp)
    try:
        data = []
        images = pdf2_to_image_stream(resp.content)
        for image in images:
            content = norm_pdf_image_deal(image, is_convert=request.convert if request.convert else True)
            data.append(content)
        return BaseResponse(code=RETCODE.OK, message=err_msg[RETCODE.OK], data="\n\n".join(data))
    except Exception as err:
        return InterfaceError(code=RETCODE.ERROR, message=err_msg[RETCODE.ERROR] + "识别失败:{}".format(err))
