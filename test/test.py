#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-07-14 10:54
# @Author: Rangers
# @Site: 
# @File: test.py

import nltk

text = "她和张明在一起。"  # 一段包含人名的文字
words = nltk.word_tokenize(text)  # 将文字分解成单词
tagged = nltk.pos_tag(words)  # 获取每个单词的词性
named_entities = nltk.ne_chunk(tagged, binary=True)  # 提取出人名
people = set()
for chunk in named_entities:
    if hasattr(chunk, 'label') and chunk.label() == 'NE':  # 如果chunk有标签并且标签是'NE'
        person = ' '.join(c[0] for c in chunk.leaves())
        people.add(person)
        print(people)
