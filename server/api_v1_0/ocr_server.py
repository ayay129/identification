#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-06-06 16:57
# @Author: Rangers
# @Site: 
# @File: ocr_server.py

from server.api_v1_0 import app
from server.bodys import PostData, CardResponse, UrlData, BaseResponse, InterfaceError
from core.const import RETCODE, RespType, err_msg, ReqType
from core.identification import function_map, change_format, doc_crop_enhance, merge_images
from core.aigc_multi_class import distribute_file_class


# pdf/png/jpg/jpeg/word格式
# 'words_result': {'姓名': {'location': {'top': 101, 'left': 184, 'width': 86, 'height': 38}, 'words': '孙么'}, '民族': {'location': {'top': 167, 'left': 362, 'width': 26, 'height': 29}, 'words': '汉'}, '住址': {'location': {'top': 281, 'left': 184, 'width': 304, 'height': 71}, 'words': '内蒙古通辽市科尔沁区永清十委14组179号'}, '公民身份号码': {'location': {'top': 428, 'left': 343, 'width': 396, 'height': 38}, 'words': '152301199802185042'}, '出生': {'location': {'top': 222, 'left': 180, 'width': 304, 'height': 30}, 'words': '19980218'}, '性别': {'location': {'top': 166, 'left': 190, 'width': 27, 'height': 31}, 'words': '女'}}, 'words_result_num': 6, 'idcard_number_type': 1, 'image_status': 'normal', 'risk_type': 'screen', 'log_id': 1666721773649062414}
@app.post("/document/identification")
async def identity(request: PostData):
    """
    身份证，港澳通行证，学位认证报告，出生证，护照识别
    :param request: input_type，指定证件类型; .url 指定可访问的证件url地址
    :return:
    """
    image_data = change_format(url=request.url)
    if not image_data:
        return InterfaceError(code=RETCODE.CHANGE_FORMAT_ERROR, message=err_msg[RETCODE.CHANGE_FORMAT_ERROR])
    if isinstance(image_data, list):
        image_bytes = image_data[0]
    else:
        image_bytes = image_data
    # 1.身份证
    if request.input_type == ReqType.IdentityCard:
        try:
            response_data = function_map[ReqType.IdentityCard](image_data)
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
    # 2.出生证
    elif request.input_type == ReqType.BirthCert:
        try:
            response_data = function_map[ReqType.BirthCert](image_bytes)
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
    # 3.护照
    elif request.input_type == ReqType.PassPort:
        try:
            response_data = function_map[ReqType.PassPort](image_bytes)
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
    # 4. 港澳通行证
    elif request.input_type == ReqType.HkMacaoPermit:
        # 转二进制
        try:
            response_data = function_map[ReqType.HkMacaoPermit](image_bytes)
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
    # 5. 学位证 type 5
    elif request.input_type == ReqType.DegreeCertReport:
        try:
            response_data = function_map[ReqType.DegreeCertReport](image_bytes)
        except Exception as err:
            return InterfaceError(code=RETCODE.ERROR, message="{}->{}".format(err_msg[RETCODE.ERROR], err))
        # 异常
        if isinstance(response_data, InterfaceError):
            return response_data
        elif response_data is None:
            return InterfaceError(code=RETCODE.RECOGNIZE_EMPTY_ERROR,
                                  message=err_msg[RETCODE.RECOGNIZE_EMPTY_ERROR])
        # 正常
        return CardResponse(code=RETCODE.OK, type=RespType.DegreeCertReport, message=err_msg[RETCODE.OK],
                            data=response_data)
    # 结婚证 10
    elif request.input_type == ReqType.Marriage:
        try:
            response_data = function_map[ReqType.Marriage](image_bytes)
        except Exception as err:
            return InterfaceError(code=RETCODE.ERROR, message="{}->{}".format(err_msg[RETCODE.ERROR], err))
        if isinstance(response_data, InterfaceError):
            return response_data
        return CardResponse(code=RETCODE.OK, type=RespType.Marriage, message=err_msg[RETCODE.OK],
                            data=response_data)
    # 毕业证 11
    elif request.input_type == ReqType.GraduationCert:
        try:
            response_data = function_map[ReqType.GraduationCert](image_bytes)
        except Exception as err:
            return InterfaceError(code=RETCODE.ERROR, message="{}->{}".format(err_msg[RETCODE.ERROR], err))
        return CardResponse(code=RETCODE.OK, type=RespType.GraduationCert, message=err_msg[RETCODE.OK],
                            data=response_data)
    # 学位证 12
    elif request.input_type == ReqType.DegreeCert:
        try:
            response_data = function_map[ReqType.GraduationCert](image_bytes)
        except Exception as err:
            return InterfaceError(code=RETCODE.ERROR, message="{}->{}".format(err_msg[RETCODE.ERROR], err))
        return CardResponse(code=RETCODE.OK, type=RespType.DegreeCert, message=err_msg[RETCODE.OK],
                            data=response_data)
    # 非范围内
    else:
        return InterfaceError(code=RETCODE.OUT_OF_SUPPORT, message=err_msg[RETCODE.OUT_OF_SUPPORT])


@app.post("/image/correct")
async def identity(request: UrlData):
    """
    图片纠正
    :param request: .url 图片url地址
    :return:
    """
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


@app.post("/image/merge")
async def function(request: UrlData):
    if not isinstance(request.url, list) or len(request.url) < 2:
        return InterfaceError(code=RETCODE.ERROR, message=err_msg[RETCODE.ERROR] + "params error")
    image_list = []
    for url in request.url:
        image_bytes = change_format(url)
        image_list.append(image_bytes)
    try:
        response_data = merge_images(image_list)
    except Exception as err:
        return InterfaceError(code=RETCODE.ERROR, message="{}->{}".format(err_msg[RETCODE.ERROR], err))
    return BaseResponse(code=RETCODE.OK, message=err_msg[RETCODE.OK], data={"image_b64": response_data})
