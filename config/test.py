import json
import base64
import hmac
from hashlib import sha1
import requests
import time


def hash_hmac(data, key, sha1):
    hmac_code = hmac.new(key.encode(), data.encode(), sha1).digest()
    return base64.b64encode(hmac_code).decode()


if __name__ == '__main__':
    print("--------demo---------")

    ak = "A8319C0745A7A4D06B6FD5C446E8E8A6"
    sk = "3E49E036C0CA7DB2AD66AAD8B497BED2"
    http_method = "POST"
    # uri = "/api/call/mattingportrait/"
    uri = "/api/call/passport/"
    query_string = ""
    time_stamp = str(int(time.time()))
    print(time_stamp)

    dict_body = {}
    dict_body["url"] = "https://st-gdx.dancf.com/gaodingx/10108011/clip/20191022-155924-2d56.jpg"
    dict_body["width"] = 1500
    dict_body["height"] = 1500
    dict_body["background"]= "#ffcc66"
    json_body = json.dumps(dict_body)

    list_raw = [http_method, "@", uri, "@", query_string, "@", time_stamp, "@", json_body]
    request_raw = "".join(list_raw)
    print(request_raw)

    signature = hash_hmac(request_raw, sk, sha1)
    print(signature)

    resquest_api = "https://open-api.gaoding.com/api/call/passport"
    headers = {'Content-Type': 'application/json', 'X-Timestamp': time_stamp, 'X-AccessKey': ak,
               "X-Signature": signature,"app_id":"VIICXM402379"}
    resp = requests.post(resquest_api, headers=headers, data=json_body)
    code = resp.status_code
    print(code)
    resp_data = resp.text
    print(resp_data)