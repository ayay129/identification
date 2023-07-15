#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-06-06 15:17
# @Author: Rangers
# @Site: 
# @File: __init__.py.py
import base64

from aip import AipOcr, AipImageProcess, AipFace
from core.parser import YamlParser
import os
from fastapi.logger import logger


class DefineOcr(AipOcr):
    __marriage_certificate = "https://aip.baidubce.com/rest/2.0/ocr/v1/marriage_certificate"

    def marriage_certificate(self, image, options=None):
        options = options or {}
        data = {}
        data["image"] = base64.b64encode(image).decode()
        data.update(options)
        return self._request(self.__marriage_certificate, data)


yaml_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
# 初始化配置
connect_cfg = YamlParser(config=os.path.join(yaml_dir, "api.yaml")).json
straw_api = connect_cfg.get("straw_api")
baidu_ocr_env = connect_cfg.get("baidu_ocr")

baidu_client = DefineOcr(str(baidu_ocr_env["app_id"]), str(baidu_ocr_env["api_key"]), str(baidu_ocr_env["secret_key"]))
baidu_image_client = AipImageProcess(str(baidu_ocr_env["app_id"]), str(baidu_ocr_env["api_key"]),
                                     str(baidu_ocr_env["secret_key"]))

baidu_face_client = AipFace(str(baidu_ocr_env["app_id"]), str(baidu_ocr_env["api_key"]),
                            str(baidu_ocr_env["secret_key"]))

