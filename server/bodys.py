#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-07-10 17:43
# @Author: Rangers
# @Site: 
# @File: bodys.py
from pydantic import BaseModel
from typing import Optional


class UrlData(BaseModel):
    url: str | list


class ConvertReq(UrlData):
    url: str
    convert: Optional[bool]


class MergeData(BaseModel):
    urls: list
    input_type: Optional[int]


class PostData(UrlData):
    input_type: int


class FaceReq(BaseModel):
    first_image_url: str
    second_image_url: str


class BaseResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict | str]


class CardResponse(BaseResponse):
    type: int


class InterfaceError(BaseModel):
    code: str
    message: str
