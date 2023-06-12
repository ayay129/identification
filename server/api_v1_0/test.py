#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-06-07 13:58
# @Author: Rangers
# @Site: 
# @File: test.py
import json

from config import baidu_client
import os

for root, dirs, files in os.walk("../../data/id_card"):
    for name in files:
        filename = '%s/%s' % (root, name)
        with open(filename, "rb") as fp:
            image = fp.read()
        res_image = baidu_client.multi_idcard(image,
                                        options={"detect_direction": "true", "detect_risk": "true",
                                                 "detect_quality": "true"})
        print(json.dumps(res_image))
        print(res_image)

# res_image = baidu_client.idcard(image="../../data/id_card/反面（袁鸿来）.pdf",id_card_side="front" )
# print(res_image)
