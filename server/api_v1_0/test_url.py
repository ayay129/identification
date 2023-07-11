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
    "https://upload.cdn.galaxy-immi.com/crm/production/files/7891/1660562337192.pdf"
]
# #
# 港澳通行证
hk_urls = [
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10074/1686807812049.jpeg"
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10029/1686791992786.jpg",
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10070/1686744354080.jpg",
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10070/1686736171514.jpg",
    "https://upload.cdn.galaxy-immi.com/crm/production/files/6058/1656294519622.jpg",
    "https://upload.cdn.galaxy-immi.com/crm/production/files/1659612754369.jpg",
    "https://upload.cdn.galaxy-immi.com/crm/production/files/1659615211045.jpg",
    "https://upload.cdn.galaxy-immi.com/crm/production/files/7888/1660919894772.png",
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10029/1686730110871.jpg",
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10070/1686738383100.jpg"
]
#
# 出生证
born_urls = [
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10029/1686656152017.pdf",
    "https://upload.cdn.galaxy-immi.com/crm/production/files/7861/1660620969527.pdf",
    "https://upload.cdn.galaxy-immi.com/crm/production/files/7868/1660874135227.jpg",
    "https://upload.cdn.galaxy-immi.com/crm/production/files/7870/1662184804891.jpg"
    "https://upload.cdn.galaxy-immi.com/crm/production/files/14535/1688104083055.pdf"
]

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

marriage_urls = [
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/168897785083018018.png",
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10368/1689040846177.jpg"
]
test_dict = {
    1: id_urls,
    2: born_urls,
    3: pass_port_urls,
    4: hk_urls,
    5: degree_urls,
    10: marriage_urls
}

dismantle = {
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688355236313.jpg",
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688355244577.xls",
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688355437563.pdf",
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688355456810.pptx",
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688355426891.docx",
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688355415260.ppt",
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688366693905.doc",
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688366700252.png",
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688366705399.xlsx"
}


def transfer(url2t):
    url = "http://test.crm.galaxy-immi.com/business/temp/temp-url"
    data = {"field": url2t}
    response = requests.get(url=url, params=data)
    try:
        if 200 == response.status_code:
            return response.json()['data']['url']
    except Exception as err:
        return None


def main():
    for key, value in test_dict.items():
        # if key != 10:
        #     continue
        for url in value:
            links = transfer(url)
            print(links)
            if not links:
                print(links)
                continue
            resp = requests.post(url="http://127.0.0.1:52520/document/identification", json={
                "url": links,
                "input_type": key
            })
            print(resp.text)


def test_dis():
    for url in dismantle:
        links = transfer(url)
        if not links:
            continue
        resp = requests.post(url="http://127.0.0.1:52520/document/general", json={
            "url": links
        })
        print(links)
        print(resp.text)


if __name__ == '__main__':
    # test_dis()
    main()
