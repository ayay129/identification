#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-06-14 17:20
# @Author: Rangers
# @Site: 
# @File: const.py


degree_header = ["report_title", "name", "reportID", "printDate", "gender", "birth", "degreeAwardingUnit",
                 "degreeLevel", "major", "subjectCategory", "degreeYear", "degreeID"]

id_card_header = ["name", "gender", "nationality", "birth", "address", "cardNum", "issuingAuthority", "termBegins",
                  "endOfTerm"]

birth_cert_header = ["newborn", "gender", "birth", "motherName", "motherNum", "fatherName", "fatherNum", "code",
                     "hospital", "gestationalAge", "birthWeight", "birthLength", "birthProvince", "birthCity",
                     "birthCounty", "motherAge", "motherNationality", "motherEthnic", "motherAddress", "fatherAge",
                     "fatherNationality", "fatherEthnic", "fatherAddress"]

passport_header = ["name", "pinyin", "birth", "birthLocation", "issueLocation", "issueDate", "valid", "gender",
                   "countryCode", "MRZCode2", "issuingAuthority", "MRZCode1", "cardNum", "nationality"]

hk_macau_header = ["name", "pinyin", "birth", "gender", "termBegins", "endOfTerm", "issueLocation", "cardNum"]


class RETCODE:
    OK = 0
    ERROR = -1
    CHANGE_FORMAT_ERROR = 3001
    RECOGNIZE_EMPTY_ERROR = 3002
    OUT_OF_SUPPORT = 2
    GET_ERROR = 6001


err_msg = {
    RETCODE.OK: "请求成功",
    RETCODE.ERROR: "识别异常",
    RETCODE.OUT_OF_SUPPORT: "超出支持范围",
    RETCODE.CHANGE_FORMAT_ERROR: "格式转换失败",
    RETCODE.RECOGNIZE_EMPTY_ERROR: "识别结果为空",
    RETCODE.GET_ERROR: "GET获取地址{}的二进制流失败"
}


class ReqType:
    IdentityCard = 1
    BirthCert = 2
    PassPort = 3
    HkMacaoPermit = 4
    DegreeCertReport = 5
    Marriage = 10
    GraduationCert = 11
    DegreeCert = 12


class RespType(ReqType):
    Unknown = 0
    IdentityCardFront = 6
    IdentityCardBack = 7
    HkMacaoPermitFront = 8
    HkMacaoPermitBack = 9
