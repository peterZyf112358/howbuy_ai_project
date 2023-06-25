import pandas as pd

def transpose(X):
    m,n = len(X), len(X[0])
    return [[X[i][j] for i in range(m)] for j in range(n)]


def load_entity(path, sheet_name, usecols, dict_):
    wb = pd.read_excel(path, sheet_name='ner_样例实体', usecols="A:B", header=1)
    header = []
    for value in wb.values:
        header.append(value)
    for item in header:
        if item[1] not in dict_:
            dict_[item[1]] = [item[0]]
        else:
            dict_[item[1]].append(item[0])
    return dict_

def generate_dict():
    enum = {}
    others = {}
    entity = {}
    load_entity('C:/Users/yifan.zhao01/Desktop/模板.xlsx', '属性枚举值', "A:C", enum)
    load_entity('C:/Users/yifan.zhao01/Desktop/模板.xlsx', '属性其他类型值', "A:B", others)
    load_entity('C:/Users/yifan.zhao01/Desktop/模板.xlsx', 'ner_样例实体', 'A:B', entity)
    load_entity('C:/Users/yifan.zhao01/Desktop/模板.xlsx', 'intention _样例实体', 'A:B', entity)
    load_entity('C:/Users/yifan.zhao01/Desktop/模板.xlsx', '属性对应实体类别', 'A:B', entity)
    return enum, others, entity



if __name__ == '__main__':
    enum, others, entity = generate_dict()


