#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-06-06 16:57
# @Author: Rangers
# @Site: 
# @File: server.py

from fastapi import FastAPI, Response
import pydantic
from typing import Optional, List
from core.exception import ReqType, RETCODE, err_msg, RespType, InterfaceError
from core.identification import deal_passport, deal_id_card, deal_HkMcau_permit, deal_birth_cert, change_format, \
    deal_degree_report, doc_crop_enhance
from core.aigc_multi_class import distribute_file_class

app = FastAPI()


class UrlData(pydantic.BaseModel):
    url: str


class PostData(UrlData):
    input_type: int


class BaseResponse(pydantic.BaseModel):
    code: int
    message: str
    data: Optional[dict | str]


class CardResponse(BaseResponse):
    type: int


# pdf/png/jpg/jpeg/word格式
# 'words_result': {'姓名': {'location': {'top': 101, 'left': 184, 'width': 86, 'height': 38}, 'words': '孙么'}, '民族': {'location': {'top': 167, 'left': 362, 'width': 26, 'height': 29}, 'words': '汉'}, '住址': {'location': {'top': 281, 'left': 184, 'width': 304, 'height': 71}, 'words': '内蒙古通辽市科尔沁区永清十委14组179号'}, '公民身份号码': {'location': {'top': 428, 'left': 343, 'width': 396, 'height': 38}, 'words': '152301199802185042'}, '出生': {'location': {'top': 222, 'left': 180, 'width': 304, 'height': 30}, 'words': '19980218'}, '性别': {'location': {'top': 166, 'left': 190, 'width': 27, 'height': 31}, 'words': '女'}}, 'words_result_num': 6, 'idcard_number_type': 1, 'image_status': 'normal', 'risk_type': 'screen', 'log_id': 1666721773649062414}
@app.post("/document/identification")
async def identity(request: PostData):
    image_bytes = change_format(url=request.url)
    if not image_bytes:
        return InterfaceError(code=RETCODE.CHANGE_FORMAT_ERROR, message=err_msg[RETCODE.CHANGE_FORMAT_ERROR])
    # 身份证
    if request.input_type == ReqType.IdentityCard:
        try:
            response_data = deal_id_card(image_bytes)
        except Exception as err:
            # 识别异常
            return InterfaceError(code=RETCODE.ERROR, message="{}->{}".format(err_msg[RETCODE.ERROR], err))
        # 异常
        if response_data is None:
            return InterfaceError(code=RETCODE.RECOGNIZE_EMPTY_ERROR, message=err_msg[RETCODE.RECOGNIZE_EMPTY_ERROR])
        elif isinstance(response_data, InterfaceError):
            return response_data
        # 正常
        if len(response_data.keys()) == 6:
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
        try:
            response_data = deal_birth_cert(image_bytes)
        except Exception as err:
            # 识别异常
            return InterfaceError(code=RETCODE.ERROR, message="{}->{}".format(err_msg[RETCODE.ERROR], err))
        # 异常
        if response_data is None:
            return InterfaceError(code=RETCODE.RECOGNIZE_EMPTY_ERROR, message=err_msg[RETCODE.RECOGNIZE_EMPTY_ERROR])
        elif isinstance(response_data, InterfaceError):
            return response_data
        # 正常
        return CardResponse(code=RETCODE.OK, type=RespType.BirthCert, message=err_msg[RETCODE.OK], data=response_data)
    # 护照
    elif request.input_type == ReqType.PassPort:
        try:
            response_data = deal_passport(image_bytes)
        except Exception as err:
            # 识别异常
            return InterfaceError(code=RETCODE.ERROR, message="{}->{}".format(err_msg[RETCODE.ERROR], err))
        # 异常
        if response_data is None:
            return InterfaceError(code=RETCODE.RECOGNIZE_EMPTY_ERROR, message=err_msg[RETCODE.RECOGNIZE_EMPTY_ERROR])
        elif isinstance(response_data, InterfaceError):
            return response_data
        # 正常
        return CardResponse(code=RETCODE.OK, type=RespType.PassPort, message=err_msg[RETCODE.OK], data=response_data)
    # 港澳通行证
    elif request.input_type == ReqType.HkMacaoPermit:
        # 转二进制
        try:
            response_data = deal_HkMcau_permit(image_bytes)
        except Exception as err:
            # 识别异常
            return InterfaceError(code=RETCODE.ERROR, message="{}->{}".format(err_msg[RETCODE.ERROR], err))
        # 异常
        if response_data is None:
            # 为空
            return InterfaceError(code=RETCODE.RECOGNIZE_EMPTY_ERROR,
                                  message=err_msg[RETCODE.RECOGNIZE_EMPTY_ERROR])
        elif isinstance(response_data, InterfaceError):
            # 返回内部异常
            return response_data
        # 正常
        if response_data == RespType.HkMacaoPermitBack:
            # 反面
            return CardResponse(code=RETCODE.OK, type=RespType.HkMacaoPermitBack, message=err_msg[RETCODE.OK],
                                data=None)
        elif len(response_data.keys()) == 8:
            # 正面
            return CardResponse(code=RETCODE.OK, type=RespType.HkMacaoPermitFront, message=err_msg[RETCODE.OK],
                                data=response_data)
        else:
            # 混贴
            return CardResponse(code=RETCODE.OK, type=RespType.HkMacaoPermit, message=err_msg[RETCODE.OK],
                                data=response_data)
    # 学位证 type 5
    elif request.input_type == ReqType.Degree:
        try:
            response_data = deal_degree_report(image_bytes)
        except Exception as err:
            return InterfaceError(code=RETCODE.ERROR, message="{}->{}".format(err_msg[RETCODE.ERROR], err))
        # 异常
        if isinstance(response_data, InterfaceError):
            return response_data
        elif response_data is None:
            return InterfaceError(code=RETCODE.RECOGNIZE_EMPTY_ERROR,
                                  message=err_msg[RETCODE.RECOGNIZE_EMPTY_ERROR])
        # 正常
        return CardResponse(code=RETCODE.OK, type=RespType.Degree, message=err_msg[RETCODE.OK],
                            data=response_data)
    # 非范围内
    else:
        return InterfaceError(code=RETCODE.OUT_OF_SUPPORT, message=err_msg[RETCODE.OUT_OF_SUPPORT])


@app.post("/image/correct")
async def identity(request: UrlData):
    image_bytes = change_format(url=request.url)
    if not image_bytes:
        return InterfaceError(code=RETCODE.CHANGE_FORMAT_ERROR, message=err_msg[RETCODE.CHANGE_FORMAT_ERROR])
    try:
        response_data = doc_crop_enhance(image_bytes=image_bytes)
    except Exception as err:
        return InterfaceError(code=RETCODE.ERROR, message="{}->{}".format(err_msg[RETCODE.ERROR], err))
    if response_data is None:
        return InterfaceError(code=RETCODE.RECOGNIZE_EMPTY_ERROR,
                              message=err_msg[RETCODE.RECOGNIZE_EMPTY_ERROR])
    return BaseResponse(code=RETCODE.OK, message=err_msg[RETCODE.OK], data=response_data)


@app.post("/document/general")
async def identify(request: UrlData):
    try:
        response_data = distribute_file_class(url=request.url)
        if not response_data:
            raise ValueError
    except Exception as err:
        return InterfaceError(code=RETCODE.ERROR, message="{}->{}".format(err_msg[RETCODE.ERROR], err))
    return BaseResponse(code=RETCODE.OK, message=err_msg[RETCODE.OK], data=response_data)
