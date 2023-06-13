#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-06-06 16:57
# @Author: Rangers
# @Site: 
# @File: server.py

from fastapi import FastAPI, Response
import pydantic
import requests
from typing import Optional, List
from core.exception import ReqType, RETCODE, err_msg, RespType
from core.identification import deal_passport, deal_id_card, deal_HkMcau_permit, deal_birth_cert, change_format, \
    deal_degree_report

app = FastAPI()


class PostData(pydantic.BaseModel):
    url: str
    input_type: int


class CardResponse(pydantic.BaseModel):
    code: int
    type: int
    message: str
    data: Optional[dict]


# pdf/png/jpg/jpeg/word格式
# 'words_result': {'姓名': {'location': {'top': 101, 'left': 184, 'width': 86, 'height': 38}, 'words': '孙么'}, '民族': {'location': {'top': 167, 'left': 362, 'width': 26, 'height': 29}, 'words': '汉'}, '住址': {'location': {'top': 281, 'left': 184, 'width': 304, 'height': 71}, 'words': '内蒙古通辽市科尔沁区永清十委14组179号'}, '公民身份号码': {'location': {'top': 428, 'left': 343, 'width': 396, 'height': 38}, 'words': '152301199802185042'}, '出生': {'location': {'top': 222, 'left': 180, 'width': 304, 'height': 30}, 'words': '19980218'}, '性别': {'location': {'top': 166, 'left': 190, 'width': 27, 'height': 31}, 'words': '女'}}, 'words_result_num': 6, 'idcard_number_type': 1, 'image_status': 'normal', 'risk_type': 'screen', 'log_id': 1666721773649062414}
@app.post("/document/identification")
async def identity(request: PostData):
    image_bytes = change_format(url=request.url)
    if not image_bytes:
        return CardResponse(code=RETCODE.IMAGE_FORMAT_ERROR, type=RespType.Unknown,
                            message=err_msg[RETCODE.IMAGE_FORMAT_ERROR])
    # 身份证
    if request.input_type == ReqType.IdentityCard:
        response_data = deal_id_card(image_bytes)
        if response_data is None:
            return CardResponse(code=RETCODE.ERROR, type=RespType.Unknown, message=err_msg[RETCODE.ERROR])
        elif len(response_data.keys()) == 6:
            return CardResponse(code=RETCODE.OK, type=RespType.IdentityCardFront, message=err_msg[RETCODE.OK],
                                data=response_data)
        elif len(response_data.keys()) == 3:
            return CardResponse(code=RETCODE.OK, type=RespType.IdentityCardBack, message=err_msg[RETCODE.OK],
                                data=response_data)
        else:
            return CardResponse(code=RETCODE.OK, type=RespType.IdentityCard, message=err_msg[RETCODE.OK],
                                data=response_data)
    # 出生证
    elif request.input_type == ReqType.BirthCert:
        response_data = deal_birth_cert(image_bytes)
        if response_data is None:
            return CardResponse(code=RETCODE.ERROR, type=0, message=err_msg[RETCODE.ERROR])
        return CardResponse(code=RETCODE.OK, type=RespType.BirthCert, message=err_msg[RETCODE.OK], data=response_data)
    # 护照
    elif request.input_type == ReqType.PassPort:
        response_data = deal_passport(image_bytes)
        if response_data is None:
            return CardResponse(code=RETCODE.ERROR, type=0, message=err_msg[RETCODE.ERROR])
        return CardResponse(code=RETCODE.OK, type=RespType.PassPort, message=err_msg[RETCODE.OK], data=response_data)
    # 港澳通行证
    elif request.input_type == ReqType.HkMacaoPermit:
        # 转二进制
        try:
            response_data = deal_HkMcau_permit(image_bytes)
            if not response_data:
                raise
        except Exception as e:
            return CardResponse(code=RETCODE.ERROR, type=0, message=err_msg[RETCODE.ERROR] + e)
        return CardResponse(code=RETCODE.OK, type=RespType.HkMacaoPermit, message=err_msg[RETCODE.OK],
                            data=response_data)
    # 学位证
    elif request.input_type == ReqType.Degree:
        try:
            response_data = deal_degree_report(image_bytes)
            if not response_data:
                return CardResponse(code=RETCODE.IMAGE_FORMAT_ERROR, type=0,
                                    message=err_msg[RETCODE.IMAGE_FORMAT_ERROR])
        except Exception as e:
            return CardResponse(code=RETCODE.ERROR, type=0, message=err_msg[RETCODE.ERROR] + e)
        return CardResponse(code=RETCODE.OK, type=RespType.HkMacaoPermit, message=err_msg[RETCODE.OK],
                            data=response_data)
    # 非范围内
    else:
        return CardResponse(code=RETCODE.OUT_OF_SUPPORT, message=err_msg[RETCODE.OUT_OF_SUPPORT], data={})


def transfer(url2t):
    url = "http://test.crm.galaxy-immi.com/business/temp/temp-url"
    data = {"field": url2t}
    response = requests.get(url=url, params=data)
    if 200 == response.status_code:
        return response.json()['data']['url']
