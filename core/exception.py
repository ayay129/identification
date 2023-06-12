#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-06-12 15:04
# @Author: Rangers
# @Site:  错误码封装模块
# @File: exception.py


class RETCODE:
    OK = 0
    ERROR = -1
    QPS_LIMIT = 18
    TOTAL_LIMIT = 19
    IMAGE_EMPTY = 216200
    IMAGE_FORMAT_ERROR = 216201
    IMAGE_TOO_LARGE = 216202
    RECOGNIZE_ERROR = 216630
    OUT_OF_SUPPORT = 666


err_msg = {
    RETCODE.OK: "请求成功",
    RETCODE.ERROR: "请求失败",
    RETCODE.QPS_LIMIT: "QPS超限额",
    RETCODE.TOTAL_LIMIT: "请求总量超额",
    RETCODE.IMAGE_EMPTY: "图片为空",
    RETCODE.IMAGE_FORMAT_ERROR: "图片格式错误",
    RETCODE.RECOGNIZE_ERROR: "识别失败",
    RETCODE.IMAGE_TOO_LARGE: "图片过大",
    RETCODE.OUT_OF_SUPPORT: "超出支持范围"
}


class ReqType:
    IdentityCard = 1
    BirthCert = 2
    PassPort = 3
    HkMacaoPermit = 4
    Degree = 5


class RespType(ReqType):
    Unknown = 0
    IdentityCardFront = 6
    IdentityCardBack = 7
    HkMacaoPermitFront = 8
    HkMacaoPermitBack = 9
