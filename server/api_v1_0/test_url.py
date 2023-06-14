#! /usr/bin/python3 # -*- coding:utf-8 -*-
# @Time: 2023-06-08 17:47
# @Author: Rangers
# @Site: 
# @File: test_url.py
import json

import requests

# 身份证
id_urls = [
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10029/1686641661087.jpg",
           "https://upload.cdn.galaxy-immi.com/crm/production/files/6058/1657076550912.jpg",
           "https://upload.cdn.galaxy-immi.com/crm/production/files/6058/1657076559505.jpg",
           "https://upload.cdn.galaxy-immi.com/crm/production/files/1659612739360.jpg",
           "https://upload.cdn.galaxy-immi.com/crm/production/files/1659612748670.jpg",
           "https://upload.cdn.galaxy-immi.com/crm/production/files/1659665753619.jpg",
           "https://upload.cdn.galaxy-immi.com/crm/production/files/7891/1660562337192.pdf"]
# #
# 港澳通行证
hk_urls = [
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10070/1686744354080.jpg",
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10070/1686736171514.jpg",
    # "https://upload.cdn.galaxy-immi.com/crm/production/files/6058/1656294519622.jpg",
    # "https://upload.cdn.galaxy-immi.com/crm/production/files/1659612754369.jpg",
    # "https://upload.cdn.galaxy-immi.com/crm/production/files/1659615211045.jpg",
    # "https://upload.cdn.galaxy-immi.com/crm/production/files/7888/1660919894772.png",
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10029/1686730110871.jpg",
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10070/1686738383100.jpg"
]
#
# 出生证
born_urls = [
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10029/1686656152017.pdf",
    "https://upload.cdn.galaxy-immi.com/crm/production/files/7861/1660620969527.pdf",
    "https://upload.cdn.galaxy-immi.com/crm/production/files/7868/1660874135227.jpg",
    "https://upload.cdn.galaxy-immi.com/crm/production/files/7870/1662184804891.jpg"]

# 护照
pass_port_urls = [
    "https://upload.cdn.galaxy-immi.com/crm/production/files/22YH003986/1661686939300.jpg",
    "https://upload.cdn.galaxy-immi.com/crm/production/files/7951/1661005683353.pdf"
]

# 学位认证报告
degree_urls = [
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10070/1686725282010.pdf",
    "https://upload.cdn.galaxy-immi.com/crm/production/files/7865/1661878654668.pdf",
    "https://upload.cdn.galaxy-immi.com/crm/production/files/7865/1660623492861.pdf",
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10070/1686725282010.pdf"
]

test_dict = {
    1: id_urls,
    2: born_urls,
    3: pass_port_urls,
    4: hk_urls,
    5: degree_urls
}


def transfer(url2t):
    url = "http://test.crm.galaxy-immi.com/business/temp/temp-url"
    data = {"field": url2t}
    response = requests.get(url=url, params=data)
    if 200 == response.status_code:
        return response.json()['data']['url']


for key, value in test_dict.items():
    if key != 4:
        continue
    for url in value:
        links = transfer(url)
        # print(links)
        resp = requests.post(url="http://127.0.0.1:52520/document/identification", json={
            "url": links,
            "input_type": key})
        print(resp.text)

# for url in urls:
#     links = transfer(url)
#     images = pdf_to_image_stream(pdf_url=links)
#     resp = baidu_client.birthCertificate(image=images)
#     print(resp)

# with open("./你好.png","rb") as f:
#     images = f.read()
#     resp = baidu_client.birthCertificate(image=images)
#     print(resp)
