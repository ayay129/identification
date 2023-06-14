#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-06-06 16:34
# @Author: Rangers
# @Site: 
# @File: parser.py

import logging
import yaml
import os


class Parser(object):
    def __init__(self, encoding="utf-8", config=None):
        self.log = logging.getLogger(self.__class__.__name__)
        self._encoding = encoding
        self._json = None
        self._config = config


class YamlParser(Parser):

    def __load_yaml(self, yaml_file=None):
        if yaml_file is None:
            config_file = self._config
        else:
            config_file = yaml_file
        if config_file is None:
            self.log.error("File is None")
        file_obj = open(config_file, "r", encoding=self._encoding)
        try:
            self._json = yaml.load(file_obj, Loader=yaml.FullLoader)
        except IOError as e:
            self.log.error("error:{}".format(e))
        finally:
            if file_obj is not None:
                file_obj.close()

    @property
    def json(self):
        if not self._json:
            self.__load_yaml()
        return self._json

    @json.setter
    def json(self, value=None):
        if os.path.isfile(value) and value.endswith(".yml"):
            self.__load_yaml(value)
        elif isinstance(value, dict):
            self._json = value
        else:
            raise ValueError("There must input dict or existed file path")


class CfgParser(Parser):
    pass


class XMLParser(Parser):
    pass


class HTMLParser(Parser):
    pass

