#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-07-20 15:37
# @Author: Rangers
# @Site: 
# @File: email_server.py

from server.api_v1_0 import app
from server.bodys import InterfaceError, FaceReq, BaseResponse
from core.identification import change_format, face_compare
from core.const import ReqType, RETCODE, err_msg, RespType
from server.bodys import ConvertReq
from core.pdf_deal import extract_text_from_pdf, has_images_in_pdf
import requests


@app.post("/email/read")
def email(request: ConvertReq):
    resp = requests.get(url=request.url)
    if resp.status_code != 200:
        return InterfaceError(code=RETCODE.GET_ERROR, message=err_msg[RETCODE.GET_ERROR].format(request.url))
    if has_images_in_pdf(binary_pdf=resp.content):
        return InterfaceError(code=RETCODE.ERROR,
                              message=err_msg[RETCODE.ERROR] + "暂不支持pdf中含有图片,预计8月初支持")
    else:
        resp = extract_text_from_pdf(binary_pdf=resp.content, is_convert=request.convert if request.convert else True)
        return BaseResponse(code=RETCODE.OK, message=err_msg[RETCODE.OK], data=resp)
