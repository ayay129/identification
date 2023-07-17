#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-07-15 18:16
# @Author: Rangers
# @Site: 
# @File: abording.py
# 废弃
import time
import base64
import hmac
from config import straw_api
from hashlib import sha1
from PIL import Image
import io
import requests
import json


class GDApi(object):
    __domain = "https://open-api.gaoding.com"
    __portrait = "/api/call/mattingportrait/"
    __passport = "/api/call/passport/"
    __common = "/api/call/mattingcommon/"

    def _get_image_size(self, image_bytes):
        image = Image.open(io.BytesIO(image_bytes))
        return image.width, image.height

    def _get_params(self, image_bytes, option):
        # width, height = self._get_image_size(image_bytes)
        params = {
            "file_base64": base64.b64encode(image_bytes).decode(),
            # "width": width,
            # "height": height,
            # "background": "transparent",
            # "result_type": "base64"
            # "is_skip_crop": 1
        }
        if option:
            params.update(option)
        return params

    def portrait(self, image_bytes, option=None):
        return self._request(method="POST", uri=self.__portrait, data=self._get_params(image_bytes, option))

    def common(self, image_bytes, option=None):
        return self._request(method="POST", uri=self.__common, data=self._get_params(image_bytes, option))

    def passport(self, image_bytes, option=None):
        return self._request(method="POST", uri=self.__passport, data=self._get_params(image_bytes, option))

    def _request(self, method, uri, data, headers=None):
        headers = self._getAuthHeaders(method=method, uri=uri, params=data, headers=headers)
        url = self.__domain + uri
        req_func = getattr(requests, method.lower())
        return req_func(url=url, headers=headers, json=data)

    def _getAuthHeaders(self, method, uri, params=None, headers=None):
        time_stamp = str(int(time.time()))
        # CanonicalRequest = HTTPRequestMethod + '@' + CanonicalURI + '@' +CanonicalQueryString + '@' +Timestamp + '@' + RequestPayload
        list_raw = [method, "@", uri, "@", "", "@", time_stamp, "@", json.dumps(params)]
        request_raw = "".join(list_raw)
        signature = base64.b64encode(
            hmac.new(straw_api["secret_key"].encode(), request_raw.encode(), sha1).digest()).decode()
        new_headers = {"Content_Type": "application/json", "X-Timestamp": time_stamp,
                       "X-AccessKey": straw_api["api_key"], "X-Signature": signature, "app_id": straw_api["app_id"]}
        if headers:
            new_headers.update(headers)
        return new_headers


def transfer(url2t):
    url = "https://test-crm.galaxy-immi.com/business/temp/temp-url?field={}".format(url2t)
    response = requests.get(url=url)
    try:
        if 200 == response.status_code:
            return response.json()['data']['url']
    except Exception as err:
        return None


# if __name__ == '__main__':
#     from rembg import remove
#
#     with open("../data/近期证件照/近期证件照片（孙舒云）.jpeg", "rb") as f:
#         datas = f.read()
#     output = remove(datas)
#     with open("../test.png", "wb") as f:
#         f.write(output)
    # resp = goding.common(datas)
    # print(resp)
    # url = "https://upload.cdn.galaxy-immi.com/crm/test/files/9602/1689064069752.jpg"
    # links = transfer(url)
    # resp = goding.passport(links)
