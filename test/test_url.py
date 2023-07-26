#! /usr/bin/python3 # -*- coding:utf-8 -*-
# @Time: 2023-06-08 17:47
# @Author: Rangers
# @Site: 
# @File: test_url.py
import json

import requests

# 身份证
id_urls = [
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/9602/1685621038948.pdf",  # 正反两页
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/9602/1685624368732.jpg",  # 正面
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/9602/1689064162085.jpg",
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/9602/1689236998244.png"  # 混贴
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10029/1689681073159.pdf "
]
heic = {
    1: [
        "https://upload.cdn.galaxy-immi.com/crm/test/files/1689837931469.heic?x-oss-process=image/crop,x_0,y_0,w_794,h_529&OSSAccessKeyId=LTAI4G23YzQkpcybpJwSnPSk&Expires=506951442900&Signature=z5YQeWi131Iv0v%2FJIL2qNaQNjUY%3D&v=1689838143"
    ]
}

# #
# 港澳通行证
hk_urls = [
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/9602/1689232260827.pdf",  # 正反两页
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/9602/1689232644168.jpg"
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10029/1689663431793.jpg"
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10029/1689663806686.pdf"
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/9602/1689232260827.pdf "
    "https://upload.cdn.galaxy-immi.com/crm/production/files/15523/1689856565210.jpg"
]
#
# 出生证
born_urls = [
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10029/1686656152017.pdf",
    "https://upload.cdn.galaxy-immi.com/crm/production/files/7861/1660620969527.pdf",
    # "https://upload.cdn.galaxy-immi.com/crm/production/files/7868/1660874135227.jpg",
    # "https://upload.cdn.galaxy-immi.com/crm/production/files/7870/1662184804891.jpg"
    # "https://upload.cdn.galaxy-immi.com/crm/production/files/14535/1688104083055.pdf"
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10844/1689669960798.pdf"
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10029/1689668281085.pdf"
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
    "https://upload.cdn.galaxy-immi.com/crm/test/files/168897785083018018.png",
    "https://upload.cdn.galaxy-immi.com/crm/test/files/10368/1689040846177.jpg"
]
# 学位证
degree_cert_urls = [
    "https://upload.cdn.galaxy-immi.com/crm/test/files/9602/1689219348065.jpg",
]

# 毕业证
graduation_cert_urls = [
    "https://upload.cdn.galaxy-immi.com/crm/test/files/9602/1689219407935.jpg"
]

business_licence = [
    "http://upload.cdn.galaxy-immi.com/crm/production/files/1634868746010.pdf",
    "http://upload.cdn.galaxy-immi.com/crm/production/files/21YH8274/1636596800959.pdf",
    "http://upload.cdn.galaxy-immi.com/crm/production/files/21YH8274/1636621597963.pdf",
    "http://upload.cdn.galaxy-immi.com/crm/production/files/1636103858312.pdf"
]

test_dict = {
    1: id_urls,
    2: born_urls,
    3: pass_port_urls,
    4: hk_urls,
    5: degree_urls,
    10: marriage_urls,
    11: graduation_cert_urls,
    12: degree_cert_urls,
    13: business_licence
}

dismantle = {
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688355236313.jpg",
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688355244577.xls",
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688355437563.pdf",
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688355456810.pptx",
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688355426891.docx",
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688355415260.ppt",
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688366693905.doc",
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688366700252.png",
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/10416/1688366705399.xlsx"
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/1689837931469.heic?x-oss-process=image/crop,x_0,y_0,w_794,h_529&OSSAccessKeyId=LTAI4G23YzQkpcybpJwSnPSk&Expires=506951442900&Signature=z5YQeWi131Iv0v%2FJIL2qNaQNjUY%3D&v=1689838143"
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/1690180283749.pdf"
    # "https://upload.cdn.galaxy-immi.com/crm/test/files/1690180321172.ppt"
    "http://galaxy-immi-mp.oss-cn-shenzhen.aliyuncs.com/crm/test/files/attach/202210/3120011117269.pdf"

}


def transfer(url2t):
    # url = "https://test.crm.galaxy-immi.com/business/temp/temp-url?field={}".format(url2t)
    url = "https://test-crm.galaxy-immi.com/business/temp/temp-url?field={}".format(url2t)
    response = requests.get(url=url)
    try:
        if 200 == response.status_code:
            return response.json()['data']['url']
    except Exception as err:
        return None


def main():
    for key, value in test_dict.items():
        if key != 13:
            continue
        print(">>>{}".format(key))
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


def heic_test():
    for key, value in heic.items():
        if key != 1:
            continue
        for url in value:
            resp = requests.post(url="http://172.18.45.66:52520/document/identification", json={
                "url": url,
                "input_type": key
            })
            print(resp.text)


def test_dis():
    for url in dismantle:
        links = transfer(url)
        # links = url
        if not links:
            continue
        # resp = requests.post(url="http://172.18.45.66:52520/document/general", json={
        resp = requests.post(url="http://127.0.0.1:52520/document/general", json={
            "url": links
        })
        print(links)
        print(resp.text)


def test_human_face():
    first_url = "https://upload.cdn.galaxy-immi.com/crm/test/files/9602/1685624368732.jpg"
    second_url = "https://upload.cdn.galaxy-immi.com/crm/test/files/9602/1689044492094.jpg"
    first_link = transfer(first_url)
    second_link = transfer(second_url)

    resp = requests.post(url="http://127.0.0.1:52520/face/compare",
                         json={
                             "first_image_url": first_link,
                             "second_image_url": second_link
                         })
    print(resp.text)


def test_merge_image():
    urls = [
        "https://upload.cdn.galaxy-immi.com/crm/test/files/10029/1689745912852.jpg",
        "https://upload.cdn.galaxy-immi.com/crm/test/files/10029/1689745915848.jpg"
    ]

    urls = [transfer(url) for url in urls]
    resp = requests.post(url="http://127.0.0.1:52520/image/merge", json={"urls": urls, "input_type": 1})
    print(resp.text)


def test_email_read():
    # url = "https://upload.cdn.galaxy-immi.com/crm/file/email/attach/43720_1.pdf?OSSAccessKeyId=LTAI5tGMZ7J75CmXjiuANNcm&Expires=1689842414&Signature=Vc24eerToPmG%2FyCadyxx3z1RgrE%3D&v=1689842114"
    url = "https://upload.cdn.galaxy-immi.com/crm/file/email/attach/38716_1.pdf"
    url = transfer(url)
    resp = requests.post(url="http://127.0.0.1:52520/email/read", json={"url": url})
    print(resp.text)


def correct_image():
    url = "https://upload.cdn.galaxy-immi.com/crm/test/files/10619/1690270315924.jpg"
    url = transfer(url)
    resp = requests.post(url="http://127.0.0.1:52520/image/correct", json={"url": url,"compress":True})
    print(resp.text)


if __name__ == '__main__':
    # correct_image()
    test_email_read()
    # test_dis()
    # main()
    # test_merge_image()
    # test_human_face()
    # heic_test()
