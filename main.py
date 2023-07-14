#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-06-12 11:01
# @Author: Rangers
# @Site: 
# @File: main.py

import uvicorn
from server.api_v1_0 import app
from server.api_v1_0 import face_server, ocr_server

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=52520, reload=True)
