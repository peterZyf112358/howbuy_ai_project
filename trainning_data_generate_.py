# -*- coding: utf-8 -*-
import json
import random
import re
import pandas as pd
import pymysql

import entity_load


def db_structer_generater(list_of_name, write_file):
    result = []
    temp = {}

    for name in list_of_name:
        column_names = []
        column_types = []
        cursor.execute('desc kg.' + name)
        list_item = cursor.fetchall()
        temp['table_names'] = name
        temp['table_names_original'] = name
        for item in list_item:
            column_names.append([0, item[0]])
            column_types.append(item[1])
        temp['column_names'] = column_names
        temp['column_types'] = column_types
        temp["foreign_keys"] = []
        temp["primary_keys"] = [1]
        result.append(temp)
        temp = {}
    f2 = open(write_file, mode='w', encoding="utf-8")
    f2.write(json.dumps(result, ensure_ascii=False))
    f2.close()
    return json.dumps(result, ensure_ascii=False)

def date_structer_generater_a(list_of_info, write_file):
    result = []
    temp_dict = {}
    count = 0
    for item in list_of_info:
        path, table, usecols, entity, others_ = item[0], item[1], item[2], item[3], item[4]
        wb = pd.read_excel(path, sheet_name=table, usecols=usecols, header=0)

        try:
            for value in wb.values:
                temp = value[2].split('<e>')
                choice = random.choice(entity[value[1]])
                sql = temp[0] + "'" + choice + "'" + temp[1]
                question = value[0].split('<e>')
                question.insert(1, choice)
                question_ = "".join(question)
                temp_dict["db_id"] = "kg"
                temp_dict["query"] = sql
                temp_dict["question"] = question_
                temp_dict['question_id'] = 'qid'+str(count)
                result.append(temp_dict)
                temp_dict = {}
                count += 1
        except Exception as e:
            print(value)
            print(e)
    f2 = open(write_file, mode='w', encoding="utf-8")
    f2.write(json.dumps(result))
    f2.close()

def date_structer_generater_ab(list_of_info, write_file):
    result = []
    list = []
    temp_dict = {}
    time = 0
    count = 0
    for item in list_of_info:
        path, table, usecols, enum, entity, others_ = item[0], item[1], item[2], item[3], item[4], item[5]
        wb = pd.read_excel(path, sheet_name=table, usecols=usecols, header=0)

        try:
            for value in wb.values:
                ### attr1	attr2	attr1_type	attr2_type	module	entity_type sql

                if value[2] == 'enum' and value[3] == 'enum':
                    attr1 = random.choice(enum[value[0]])
                    attr1_5 = random.choice(enum[value[0]])
                    attr2 = random.choice(enum[value[1]])
                    attr2_5 = random.choice(enum[value[1]])
                    entity_ = random.choice(entity[value[5]])
                    temp = value[6].split('<e>')
                    sql = temp[0] + "'" + entity_ + "'" + temp[1]
                    question = value[4].split('<e>')
                    question.insert(1,entity_)
                    question = "".join(question)
                    attributes = re.findall('<\w*>', question)
                    if len(attributes) == 2:
                        question = re.split('<\w*>', question)
                        if '1' in attributes[0] and '1' in attributes[1]:
                            question.insert(1, attr1)
                            question.insert(3, attr1_5)
                        elif '2' in attributes[0] and '2' in attributes[1]:
                            question.insert(1, attr2)
                            question.insert(3,attr2_5)
                        elif '1' in attributes[0]:
                            question.insert(1, attr1)
                            question.insert(3, attr2)
                        else:
                            question.insert(1, attr2)
                            question.insert(3, attr1)
                    elif len(attributes) == 1:
                        question = re.split('<\w*>', question)
                        if '1' in attributes[0]:
                            question.insert(1, attr1)
                        else:
                            question.insert(1, attr2)
                    question_ = "".join(question)
                    # print(question_)
                    temp_dict["db_id"] = "kg"
                    temp_dict["query"] = sql
                    temp_dict["question"] = question_
                    temp_dict['question_id'] = 'qid'+str(count)
                    result.append(temp_dict)
                    temp_dict = {}
                    list.append(count)
                    count += 1

                elif (value[2] == 'enum' and value[3] != 'no_type')\
                        or (value[2] != 'no_type' and value[3] == 'enum'):
                    if value[2] == 'enum':
                        ### attr1	attr2	attr1_type	attr2_type	module	entity_type sql
                        attr1 = random.choice(enum[value[0]])
                        attr2 = random.choice(others_[value[3]])
                        attr1_5 = random.choice(enum[value[0]])
                        attr2_5 = random.choice(others_[value[3]])
                    else:
                        attr1 = random.choice(others_[value[2]])
                        attr2 = random.choice(enum[value[1]])
                        attr1_5 = random.choice(others_[value[2]])
                        attr2_5 = random.choice(enum[value[1]])

                    entity_ = random.choice(entity[value[5]])
                    temp = value[6].split('<e>')
                    sql = temp[0] + "'" + entity_ + "'" + temp[1]
                    question = value[4].split('<e>')
                    question.insert(1, entity_)
                    question = "".join(question)
                    attributes = re.findall('<\w*>', question)
                    if len(attributes) == 2:
                        question = re.split('<\w*>', question)
                        # print(question)
                        if '1' in attributes[0] and '1' in attributes[1]:
                            question.insert(1, str(attr1))
                            question.insert(3, str(attr1_5))
                        elif '2' in attributes[0] and '2' in attributes[1]:
                            question.insert(1, str(attr2))
                            question.insert(3, str(attr2_5))
                        elif '1' in attributes[0]:
                            question.insert(1, str(attr1))
                            question.insert(3, str(attr2))
                        else:
                            question.insert(3, str(attr2))
                            question.insert(3, str(attr1))
                    elif len(attributes) == 1:
                        question = re.split('<\w*>', question)
                        if '1' in attributes[0]:
                            question.insert(1, str(attr1))
                        else:
                            question.insert(1, str(attr2))
                    question_ = "".join(question)
                    temp_dict["db_id"] = "kg"
                    temp_dict["query"] = sql
                    temp_dict["question"] = question_
                    temp_dict['question_id'] = 'qid' + str(count)
                    result.append(temp_dict)
                    temp_dict = {}
                    count += 1

                elif value[2] == 'no_type' or value[3] == 'no_type':
                    if value[2] == 'no_type' and value[3] == 'no_type':
                        ### attr1	attr2	attr1_type	attr2_type	module	entity_type sql
                        entity_ = random.choice(entity[value[5]])
                        temp = value[6].split('<e>')
                        sql = temp[0] + "'" + entity_ + "'" + temp[1]
                        question = value[4].split('<e>')
                        question.insert(1, entity_)
                        question_ = "".join(question)
                        temp_dict["db_id"] = "kg"
                        temp_dict["query"] = sql
                        temp_dict["question"] = question_
                        temp_dict['question_id'] = 'qid' + str(count)
                        result.append(temp_dict)
                        temp_dict = {}
                    else:
                        if value[2] == 'no_type':
                            if value[3] == 'enum':
                                ### attr1	attr2	attr1_type	attr2_type	module	entity_type sql
                                attr2 = random.choice(enum[value[1]])
                            else:
                                attr2 = random.choice(others_[value[3]])
                            entity_ = random.choice(entity[value[5]])
                            temp = value[6].split('<e>')
                            sql = temp[0] + "'" + entity_ + "'" + temp[1]
                            question = value[4].split('<e>')
                            question.insert(1, entity_)
                            question = "".join(question)
                            question = re.split('\w*', question)
                            question.insert(1, str(attr2))
                            question_ = "".join(question)
                            temp_dict["db_id"] = "kg"
                            temp_dict["query"] = sql
                            temp_dict["question"] = question_
                            temp_dict['question_id'] = 'qid' + str(count)
                            result.append(temp_dict)
                            temp_dict = {}
                        else:
                            if value[2] == 'enum':
                                ### attr1	attr2	attr1_type	attr2_type	module	entity_type sql
                                attr2 = random.choice(enum[value[0]])
                            else:
                                attr2 = random.choice(others_[value[2]])
                            entity_ = random.choice(entity[value[5]])
                            temp = value[6].split('<e>')
                            sql = temp[0] + "'" + entity_ + "'" + temp[1]
                            question = value[4].split('<e>')
                            question.insert(1, entity_)
                            question = "".join(question)
                            question = re.split('\w*', question)
                            question.insert(1, str(attr2))
                            question_ = "".join(question)
                            temp_dict["db_id"] = "kg"
                            temp_dict["query"] = sql
                            temp_dict["question"] = question_
                            temp_dict['question_id'] = 'qid' + str(count)
                            result.append(temp_dict)
                            temp_dict = {}
                    count += 1
                else:
                    attr1 = random.choice(others_[value[2]])
                    attr2 = random.choice(others_[value[3]])
                    attr1_5 = random.choice(others_[value[2]])
                    attr2_5 = random.choice(others_[value[3]])
                    entity_ = random.choice(entity[value[5]])
                    temp = value[6].split('<e>')
                    sql = temp[0] + "'" + entity_ + "'" + temp[1]
                    question = value[4].split('<e>')
                    question.insert(1, entity_)
                    question = "".join(question)
                    attributes = re.findall('<\w*>', question)
                    if len(attributes) == 2:
                        question = re.split('<\w*>', question)
                        # print(question)
                        if '1' in attributes[0] and '1' in attributes[1]:
                            question.insert(1, str(attr1))
                            question.insert(3, str(attr1_5))
                        elif '2' in attributes[0] and '2' in attributes[1]:
                            question.insert(1, str(attr2))
                            question.insert(3, str(attr2_5))
                        elif '1' in attributes[0]:
                            question.insert(1, str(attr1))
                            question.insert(3, str(attr2))
                        else:
                            question.insert(3, str(attr2))
                            question.insert(3, str(attr1))
                    elif len(attributes) == 1:
                        question = re.split('<\w*>', question)
                        if '1' in attributes[0]:
                            question.insert(1, str(attr1))
                        else:
                            question.insert(1, str(attr2))
                    question_ = "".join(question)
                    temp_dict["db_id"] = "kg"
                    temp_dict["query"] = sql
                    temp_dict["question"] = question_
                    temp_dict['question_id'] = 'qid' + str(count)
                    result.append(temp_dict)
                    temp_dict = {}
                    count += 1
                time += 1
                print(count, time)


        except Exception as e:
            print(value)
            print(e)
    f2 = open(write_file, mode='w', encoding="utf-8")
    f2.write(json.dumps(result))
    f2.close()

def date_structer_generater_ba(list_of_info, write_file):
    result = []
    temp_dict = {}
    count = 0
    for item in list_of_info:
        path, table, usecols, entity, others_ = item[0], item[1], item[2], item[3], item[4]
        wb = pd.read_excel(path, sheet_name=table, usecols=usecols, header=0)

        try:
            for value in wb.values:
                temp = value[2].split('<e>')
                choice = random.choice(entity[value[1]])
                sql = temp[0] + "'" + choice + "'" + temp[1]
                question = value[0].split('<e>')
                question.insert(1, choice)
                question_ = "".join(question)
                temp_dict["db_id"] = "kg"
                temp_dict["query"] = sql
                temp_dict["question"] = question_
                temp_dict['question_id'] = 'qid'+str(count)
                result.append(temp_dict)
                temp_dict = {}
                count += 1
        except Exception as e:
            print(value)
            print(e)
    f2 = open(write_file, mode='w', encoding="utf-8")
    f2.write(json.dumps(result))
    f2.close()


if __name__ == "__main__":
    conn = pymysql.connect(host='192.168.209.110', port=3307, user='messi', password='messi', charset='utf8',
                           database='kg')
    cursor = conn.cursor()

    db_structer_generater(['基金表', '基金经理表', '基金与基金经理关联表'], 'E:\project\数据格式\output2.json')

    cursor.close()
    conn.close()


    # enum, others, entity = entity_load.generate_dict()



    # list1 = ['C:/Users/yifan.zhao01/Desktop/模板.xlsx', '实体查单属性模板', 'B,C,D', entity, others]
    # date_structer_generater_a([list1], 'E:\project\数据格式\_a.json')

    # list2 = ['C:/Users/yifan.zhao01/Desktop/模板.xlsx', '实体查多属性模板', "A:G",enum, entity, others]
    # date_structer_generater_ab([list2],'E:\project\数据格式\_ab.json')