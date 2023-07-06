# -*- coding: utf-8 -*-
import pandas as pd
from 转译文件 import time_self


def transpose(X):
    m,n = len(X), len(X[0])
    return [[X[i][j] for i in range(m)] for j in range(n)]


def load_entity(path, sheet_name, usecols, dict_):
    wb = pd.read_excel(path, sheet_name=sheet_name, usecols=usecols, header=1)
    header = []
    for value in wb.values:
        header.append(value)
    for item in header:
        if item[1] not in dict_:
            dict_[item[1]] = [item[0]]
        else:
            dict_[item[1]].append(item[0])
    return dict_

def generate_dict(excel_xlsx):
    enum_ = {}
    others_ = {}
    entity_ = {}
    load_entity(excel_xlsx, '属性枚举值', "A:C", enum_)
    load_entity(excel_xlsx, '属性其他类型值', "A:B", others_)
    load_entity(excel_xlsx, 'ner_样例实体', 'A:B', entity_)
    load_entity(excel_xlsx, 'intention _样例实体', 'A:B', entity_)
    load_entity(excel_xlsx, '属性对应实体类别', 'A:B', entity_)
    return enum_, others_, entity_


def generate_relationship(path, table, usecols):
    wb = pd.read_excel(path, sheet_name=table, usecols=usecols, header=0)
    result = {}
    for items in wb.values:
        result[items[1]] = items[0]
    return result

if __name__ == '__main__':
    enum, others, entity = generate_dict()
    for item in others['date']:
        if not time_self.recognize_date(item):
            print(item)
        else:
            print(item, time_self.recognize_date(item))

