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
import json
from core.identification import deal_password,deal_id_card,deal_HkMcau_permit,deal_birth_cert
import uvicorn

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
    # 身份证
    if request.input_type == 1:
        response_data = deal_id_card(url=request.url)
        if response_data is None:
            return CardResponse(code=1, type=0, message="Recognize Failure. Cause Unknown")
        elif len(response_data.keys()) == 6:
            return CardResponse(code=0, type=6, message="Success", data=response_data)
        elif len(response_data.keys()) == 3:
            return CardResponse(code=0, type=7, message="Success", data=response_data)
        else:
            return CardResponse(code=0, type=1, message="Success", data=response_data)
    # 出生证
    elif request.input_type == 2:
        response_data = deal_birth_cert(url=request.url)
        if response_data is None:
            return CardResponse(code=1, type=0, message="Recognize Failure. Cause Unknown")
        return CardResponse(code=0, type=2, message="Success", data=response_data)
    # 护照
    elif request.input_type == 3:
        response_data = deal_password(url=request.url)
        if response_data is None:
            return CardResponse(code=1, type=0, message="Recognize Failure. Cause Unknown")
        return CardResponse(code=0, type=3, message="Success", data=response_data)
    # 港澳通行证
    elif request.input_type == 4:
        # 转二进制
        try:
            response_data = deal_HkMcau_permit(url=request.url)
        except Exception as e:
            return
        if response_data is None:
            return CardResponse(code=1, type=0, message="Recognize Failure. Cause Unknown")
        return CardResponse(code=0, type=4, message="Success", data=response_data)
    # 学位证
    elif request.input_type == 5:
        pass
    # 非范围内
    else:
        pass


def transfer(url2t):
    url = "http://test.crm.galaxy-immi.com/business/temp/temp-url"
    data = {"field": url2t}
    response = requests.get(url=url, params=data)
    if 200 == response.status_code:
        return response.json()['data']['url']




