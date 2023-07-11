#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-07-10 17:20
# @Author: Rangers
# @Site: 
# @File: face_server.py

from server.api_v1_0 import app
from server.bodys import InterfaceError, FaceReq, BaseResponse
from core.identification import change_format, face_compare
from core.const import ReqType, RETCODE, err_msg, RespType


@app.post("/face/compare")
def compare(request: FaceReq):
    first_image_bytes = change_format(request.first_image_url)
    second_image_bytes = change_format(request.second_image_url)
    try:
        resp = face_compare(first_image_bytes, second_image_bytes)
        result = resp["result"]
        if not isinstance(result, dict) or not result:
            raise Exception("result get error")
    except Exception as err:
        return InterfaceError(code=RETCODE.ERROR, message=err_msg[RETCODE.ERROR] + "->{}".format(err))
    result["timestamp"] = resp["timestamp"]
    return BaseResponse(code=RETCODE.OK, message=err_msg[RETCODE.OK], data=result)
