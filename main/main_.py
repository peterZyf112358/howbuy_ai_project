# -*- coding: utf-8 -*-
import json
import random
import re
import sys
import traceback

import pandas as pd
import pymysql

import entity_load
import 表格实例拆分
import 转译文件.mysql2dusql as m_d


def db_struct_generate(list_of_name, write_file):
    result = []
    temp = {}
    temp['db_id'] = 'kg'
    column_names = []
    column_types = []
    column_names.append([-1, "*"])
    column_types.append('text')
    index = -1
    count = 1
    table_names = []
    table_names_original = []
    primary_keys = []
    item_name = []
    foreign_keys = []

    for name in list_of_name:
        index += 1
        cursor.execute('desc kg.' + name)
        list_item = cursor.fetchall()
        table_names.append(name)
        table_names_original.append(name)
        primary_keys.append(count)

        for item in list_item:
            count += 1
            if item[0] in item_name:
                if item[0] in ['机构代码', '基金代码', '经理代码']:
                    parent = item_name.index(item[0]) + 1
                    # print(item_name[parent-1], item[0])
                    foreign_keys.append([parent, count - 1])
            column_names.append([index, item[0]])
            item_name.append(item[0])
            if 'double' in [item[1]]:
                column_types.append('number')
            else:
                column_types.append('text')
        # temp["foreign_keys"] = []
    temp['table_names'] = table_names
    temp['table_names_original'] = table_names
    temp['column_types'] = column_types
    temp['column_names'] = column_names
    temp['primary_keys'] = primary_keys
    temp['column_names_original'] = column_names
    temp['foreign_keys'] = foreign_keys

    result.append(temp)
    f2 = open(write_file, mode='w', encoding="utf-8")
    f2.write(json.dumps(result, ensure_ascii=False))
    f2.close()

    print('db结构生成完成')

    return json.dumps(result, ensure_ascii=False)


def data_content_generate(list_of_name, write_file):
    result = []
    result_dict = {'db_id': "kg"}
    tables = {}
    for name in list_of_name:
        temp = {}
        cell = []
        column_names = []
        column_types = []
        cursor.execute('desc kg.' + name)
        list_item = cursor.fetchall()
        for item in list_item:
            column_names.append(item[0])
            if 'double' in [item[1]]:
                column_types.append('number')
            else:
                column_types.append('text')
        temp['header'] = column_names
        temp["table_name"] = name
        temp['type'] = column_types
        cursor.execute('select * from kg.' + name + ' limit 10000')
        list_item = cursor.fetchall()
        for item in list_item:
            cell.append(list(item))
        temp['cell'] = cell
        tables[name] = temp
    result_dict['tables'] = tables
    result.append(result_dict)
    f2 = open(write_file, mode='w', encoding="utf-8")
    # f2.write(json.dumps(result, ensure_ascii=False))
    json.dump(result, f2, ensure_ascii=False)
    f2.close()
    return


def data_structer_generater_a(list_of_info, result, schema_, result2, result3, train_1, test_2, test_, count):
    temp_dict = {}
    for item in list_of_info:
        path, table, usecols, entity, others_ = item[0], item[1], item[2], item[3], item[4]
        wb = pd.read_excel(path, sheet_name=table, usecols=usecols, header=0)

        try:
            # if count >= 500:
            #     count += 1
            #     continue

            for value in wb.values:
                # print('value', value)
                # if count > 500:
                #     count += 1
                #     return count
                temp = value[2].split('<e>')
                choice = random.choice(entity[value[1]])
                sql_ = temp[0] + "'" + choice + "'" + temp[1]
                question = value[0].split('<e>')
                question.insert(1, choice)
                question_ = "".join(question)
                query = "".join(sql_.split('kg.'))
                temp_dict["db_id"] = "kg"
                # temp_dict["query"] = sql_
                # 改成无db名字的格式
                temp_dict["query"] = query
                temp_dict["question"] = question_
                temp_dict['question_id'] = 'qid' + str(count)

                # print(query)
                q_json = m_d.get_sql(schema_, query, 'kg')
                temp_dict["sql"] = q_json
                if test_ and count % 5 == 0:
                    # temp_dict.pop("sql")
                    # temp_dict.pop("query")
                    # temp_dict['query'] = ""
                    # temp_dict['sql'] = ""
                    result2.append(temp_dict)
                    test_2.append(question_ + '#' + query + '\n')
                    temp_dict = {}
                    count += 1
                elif test_ and count % 4 == 0:
                    # temp_dict.pop("sql")
                    # temp_dict.pop("query")
                    # temp_dict['query'] = ""
                    # temp_dict['sql'] = ""
                    result3.append(temp_dict)

                    temp_dict = {}
                    count += 1
                else:

                    result.append(temp_dict)
                    train_1.append(question_ + '#' + query + '\n')
                    temp_dict = {}
                    count += 1
        except Exception as e:
            print(traceback.format_exc())
            print(query)
            print(count)
            print(e)
            print(query)
            sys.exit(1)
        finally:
            return count


def data_structer_generater_ab(list_of_info, result, schema_, result2, result3, train_1, test_2, test_, count):
    # result = []
    temp_dict = {}
    time = 0
    for item in list_of_info:
        path, table, usecols, enum, entity, others_ = item[0], item[1], item[2], item[3], item[4], item[5]
        wb = pd.read_excel(path, sheet_name=table, usecols=usecols, header=0)

        try:
            for value in wb.values:
                ### attr1	attr2	attr1_type	attr2_type	module	entity_type sql_

                if value[2] == 'enum' and value[3] == 'enum':
                    attr1 = random.choice(enum[value[0]])
                    attr1_5 = random.choice(enum[value[0]])
                    attr2 = random.choice(enum[value[1]])
                    attr2_5 = random.choice(enum[value[1]])
                    entity_ = random.choice(entity[value[5]])
                    temp = value[6].split('<e>')
                    sql_ = temp[0] + "'" + entity_ + "'" + temp[1]
                    question = value[4].split('<e>')
                    question.insert(1, entity_)
                    question = "".join(question)
                    attributes = re.findall('<\w*>', question)
                    if len(attributes) == 2:
                        question = re.split('<\w*>', question)
                        if '1' in attributes[0] and '1' in attributes[1]:
                            question.insert(1, attr1)
                            question.insert(3, attr1_5)
                        elif '2' in attributes[0] and '2' in attributes[1]:
                            question.insert(1, attr2)
                            question.insert(3, attr2_5)
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
                    query = "".join(sql_.split('kg.'))
                    # temp_dict["query"] = sql_
                    # 改成无db名字的格式
                    temp_dict["query"] = query
                    temp_dict["question"] = question_
                    temp_dict['question_id'] = 'qid' + str(count)

                    temp_dict['sql'] = m_d.get_sql(schema_, query, 'kg')
                    if test_ and count % 5 == 0:
                        # temp_dict.pop("sql")
                        # temp_dict.pop("query")
                        # temp_dict['query'] = ""
                        # temp_dict['sql'] = ""
                        result2.append(temp_dict)
                        test_2.append(question_ + '#' + query + '\n')

                        temp_dict = {}
                        count += 1
                    elif test_ and count % 4 == 0:
                        # temp_dict.pop("sql")
                        # temp_dict.pop("query")
                        # temp_dict['query'] = ""
                        # temp_dict['sql'] = ""
                        result3.append(temp_dict)

                        temp_dict = {}
                        count += 1
                    else:
                        result.append(temp_dict)
                        train_1.append(question_ + '#' + query + '\n')
                        temp_dict = {}
                        count += 1

                elif (value[2] == 'enum' and value[3] != 'no_type') \
                        or (value[2] != 'no_type' and value[3] == 'enum'):
                    if value[2] == 'enum':
                        ### attr1	attr2	attr1_type	attr2_type	module	entity_type sql_
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
                    sql_ = temp[0] + "'" + entity_ + "'" + temp[1]
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
                    query = "".join(sql_.split('kg.'))
                    # temp_dict["query"] = sql_
                    # 改成无db名字的格式
                    temp_dict["query"] = query
                    temp_dict["question"] = question_
                    temp_dict['question_id'] = 'qid' + str(count)
                    temp_dict['sql'] = m_d.get_sql(schema_, query, 'kg')
                    if test_ and count % 5 == 0:
                        # temp_dict.pop("sql")
                        # temp_dict.pop("query")
                        # temp_dict['query'] = ""
                        # temp_dict['sql'] = ""
                        result2.append(temp_dict)
                        test_2.append(question_ + '#' + query + '\n')
                        temp_dict = {}
                        count += 1
                    elif test_ and count % 4 == 0:
                        # temp_dict.pop("sql")
                        # temp_dict.pop("query")
                        # temp_dict['query'] = ""
                        # temp_dict['sql'] = ""
                        result3.append(temp_dict)

                        temp_dict = {}
                        count += 1
                    else:
                        result.append(temp_dict)
                        train_1.append(question_ + '#' + query + '\n')
                        temp_dict = {}
                        count += 1

                elif value[2] == 'no_type' or value[3] == 'no_type':
                    if value[2] == 'no_type' and value[3] == 'no_type':
                        ### attr1	attr2	attr1_type	attr2_type	module	entity_type sql_
                        entity_ = random.choice(entity[value[5]])
                        temp = value[6].split('<e>')
                        sql_ = temp[0] + "'" + entity_ + "'" + temp[1]
                        question = value[4].split('<e>')
                        question.insert(1, entity_)
                        question_ = "".join(question)
                        temp_dict["db_id"] = "kg"
                        query = "".join(sql_.split('kg.'))
                        # temp_dict["query"] = sql_
                        # 改成无db名字的格式
                        temp_dict["query"] = query
                        temp_dict["question"] = question_
                        temp_dict['question_id'] = 'qid' + str(count)
                        if test_ and count % 5 == 0:
                            # temp_dict.pop("sql")
                            # temp_dict.pop("query")
                            # temp_dict['query'] = ""
                            # temp_dict['sql'] = ""
                            result2.append(temp_dict)
                            test_2.append(question_ + '#' + query + '\n')
                            temp_dict = {}
                            count += 1
                        elif test_ and count % 4 == 0:
                            # temp_dict.pop("sql")
                            # temp_dict.pop("query")
                            # temp_dict['query'] = ""
                            # temp_dict['sql'] = ""
                            result3.append(temp_dict)

                            temp_dict = {}
                            count += 1
                        else:
                            result.append(temp_dict)
                            train_1.append(question_ + '#' + query + '\n')
                            temp_dict = {}
                            count += 1
                    else:
                        if value[2] == 'no_type':
                            if value[3] == 'enum':
                                ### attr1	attr2	attr1_type	attr2_type	module	entity_type sql_
                                attr2 = random.choice(enum[value[1]])
                            else:
                                attr2 = random.choice(others_[value[3]])
                            entity_ = random.choice(entity[value[5]])
                            temp = value[6].split('<e>')
                            sql_ = temp[0] + "'" + entity_ + "'" + temp[1]
                            question = value[4].split('<e>')
                            question.insert(1, entity_)
                            question = "".join(question)
                            question = re.split('\w*', question)
                            question.insert(1, str(attr2))
                            question_ = "".join(question)
                            temp_dict["db_id"] = "kg"
                            query = "".join(sql_.split('kg.'))
                            # temp_dict["query"] = sql_
                            # 改成无db名字的格式
                            temp_dict["query"] = query
                            temp_dict["question"] = question_
                            temp_dict['question_id'] = 'qid' + str(count)
                            temp_dict['sql'] = m_d.get_sql(schema_, query, 'kg')
                            if test_ and count % 5 == 0:
                                # temp_dict.pop("sql")
                                # temp_dict.pop("query")
                                # temp_dict['query'] = ""
                                # temp_dict['sql'] = ""
                                result2.append(temp_dict)
                                test_2.append(question_ + '#' + query + '\n')
                                temp_dict = {}
                                count += 1
                            elif test_ and count % 4 == 0:
                                # temp_dict.pop("sql")
                                # temp_dict.pop("query")
                                # temp_dict['query'] = ""
                                # temp_dict['sql'] = ""
                                result3.append(temp_dict)

                                temp_dict = {}
                                count += 1
                            else:
                                result.append(temp_dict)
                                train_1.append(question_ + '#' + query + '\n')
                                temp_dict = {}
                                count += 1
                        else:
                            if value[2] == 'enum':
                                ### attr1	attr2	attr1_type	attr2_type	module	entity_type sql_
                                attr2 = random.choice(enum[value[0]])
                            else:
                                attr2 = random.choice(others_[value[2]])
                            entity_ = random.choice(entity[value[5]])
                            temp = value[6].split('<e>')
                            sql_ = temp[0] + "'" + entity_ + "'" + temp[1]
                            question = value[4].split('<e>')
                            question.insert(1, entity_)
                            question = "".join(question)
                            question = re.split('\w*', question)
                            question.insert(1, str(attr2))
                            question_ = "".join(question)
                            temp_dict["db_id"] = "kg"
                            query = "".join(sql_.split('kg.'))
                            # temp_dict["query"] = sql_
                            # 改成无db名字的格式
                            temp_dict["query"] = query
                            temp_dict["question"] = question_
                            temp_dict['question_id'] = 'qid' + str(count)
                            temp_dict['sql'] = m_d.get_sql(schema_, query, 'kg')
                            if test_ and count % 5 == 0:
                                # temp_dict.pop("sql")
                                # temp_dict.pop("query")
                                # temp_dict['query'] = ""
                                # temp_dict['sql'] = ""
                                result2.append(temp_dict)
                                test_2.append(question_ + '#' + query + '\n')
                                temp_dict = {}
                                count += 1
                            elif test_ and count % 4 == 0:
                                # temp_dict.pop("sql")
                                # temp_dict.pop("query")
                                # temp_dict['query'] = ""
                                # temp_dict['sql'] = ""
                                result3.append(temp_dict)

                                temp_dict = {}
                                count += 1
                            else:
                                result.append(temp_dict)
                                train_1.append(question_ + '#' + query + '\n')
                                temp_dict = {}
                                count += 1
                    count += 1
                else:
                    attr1 = random.choice(others_[value[2]])
                    attr2 = random.choice(others_[value[3]])
                    attr1_5 = random.choice(others_[value[2]])
                    attr2_5 = random.choice(others_[value[3]])
                    entity_ = random.choice(entity[value[5]])
                    temp = value[6].split('<e>')
                    sql_ = temp[0] + "'" + entity_ + "'" + temp[1]
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
                    query = "".join(sql_.split('kg.'))
                    # temp_dict["query"] = sql_
                    # 改成无db名字的格式
                    temp_dict["query"] = query
                    temp_dict["question"] = question_
                    temp_dict['question_id'] = 'qid' + str(count)
                    temp_dict['sql'] = m_d.get_sql(schema_, query, 'kg')
                    if test_ and count % 5 == 0:
                        # temp_dict.pop("sql")
                        # temp_dict.pop("query")
                        # temp_dict['query'] = ""
                        # temp_dict['sql'] = ""
                        result2.append(temp_dict)
                        test_2.append(question_ + '#' + query + '\n')
                        temp_dict = {}
                        count += 1
                    elif test_ and count % 4 == 0:
                        # temp_dict.pop("sql")
                        # temp_dict.pop("query")
                        # temp_dict['query'] = ""
                        # temp_dict['sql'] = ""
                        result3.append(temp_dict)

                        temp_dict = {}
                        count += 1
                    else:
                        result.append(temp_dict)
                        train_1.append(question_ + '#' + query + '\n')
                        temp_dict = {}
                        count += 1
                time += 1
                # print(count, time)


        except Exception as e:
            print(traceback.format_exc())
            print(value)
            print(e)
            print(query)
            sys.exit(1)
        finally:
            return count


def data_structer_generater_ba(list_of_info, result, schema_, result2, result3, train_1, test_2, test_, count):
    # result = []
    temp_dict = {}
    for item in list_of_info:
        path, table, usecols, others_, enum_ = item[0], item[1], item[2], item[3], item[4]
        wb = pd.read_excel(path, sheet_name=table, usecols=usecols, header=0)

        try:
            for value in wb.values:
                attr_name = value[0]
                value_type = value[2]
                question = value[1]
                org_sql = value[3]
                if value_type == 'enum':
                    random_value = random.choice(enum_[attr_name])
                    input_data = str(random_value)
                else:
                    if value_type == 'area_value':
                        random_value = random.choice(others_['value_ratio'])
                    else:
                        random_value = random.choice(others_[value_type])

                    input_data = 表格实例拆分.check_type_and_return(value_type, random_value)
                if '<a>' in question:
                    temp_question = re.split('<a>', question)
                    temp_question.insert(1, attr_name)
                    question = "".join(temp_question)
                if re.search('<\w*>', question):
                    temp_question = re.split('<\w*>', question)
                    temp_question.insert(1, str(random_value))
                    question = "".join(temp_question)
                if input_data and re.search('<\w*>', org_sql):
                    if type(input_data) == list:
                        if len(input_data) == 2:
                            # print(input_data, '1')
                            temp_sql = re.split('<\w*>', org_sql)
                            temp_sql.insert(1, input_data[0])
                            temp_sql.insert(3, input_data[1])
                            org_sql = "".join(temp_sql)
                        else:
                            # print(random_value, input_data, '2')
                            temp_sql = re.split('<\w*>', org_sql)
                            temp_sql.insert(1, "'" + input_data[0] + "'")
                            org_sql = "".join(temp_sql)
                    else:
                        # print(input_data, '3')
                        temp_sql = re.split('<\w*>', org_sql)
                        temp_sql.insert(1, "'" + str(input_data) + "'")
                        org_sql = "".join(temp_sql)
                # print(question)
                temp_dict["db_id"] = "kg"
                temp_dict["query"] = org_sql
                temp_dict["question"] = question
                temp_dict['question_id'] = 'qid' + str(count)
                query = "".join(org_sql.split('kg.'))
                temp_dict['sql'] = m_d.get_sql(schema_, query, 'kg')
                # print(temp_sql)
                if test_ and count % 5 == 0:
                    # temp_dict.pop("sql")
                    # temp_dict.pop("query")
                    # temp_dict['query'] = ""
                    # temp_dict['sql'] = ""
                    result2.append(temp_dict)
                    test_2.append(question + '#' + query + '\n')
                    temp_dict = {}
                    count += 1
                elif test_ and count % 4 == 0:
                    # temp_dict.pop("sql")
                    # temp_dict.pop("query")
                    # temp_dict['query'] = ""
                    # temp_dict['sql'] = ""
                    result3.append(temp_dict)

                    temp_dict = {}
                    count += 1
                else:
                    result.append(temp_dict)
                    train_1.append(question + '#' + query + '\n')
                    temp_dict = {}
                    count += 1

        except Exception as e:
            print(traceback.format_exc())
            print(value)
            print(org_sql)
            print('random_value', random_value)
            print('input_data', input_data)
            print(e)
            print(query)
            sys.exit(1)
        finally:
            return count


def data_structer_generater_bba(list_of_info, result, schema_, result2, result3, train_1, test_2, test_, count):
    # result = []
    temp_dict = {}
    try:
        for item in list_of_info:
            path, table, usecols, others_, enum_, rp = item[0], item[1], item[2], item[3], item[4], item[5]
            wb = pd.read_excel(path, sheet_name=table, usecols=usecols, header=0)
            # attr1	attr2 module	attr1_relation	attr2_relation sql_
            for value in wb.values:
                # print(count)
                attr1 = value[0]
                attr2 = value[1]
                question = value[2]
                ar1 = rp[value[3]]
                ar2 = rp[value[4]]
                a_ = value[5]
                sql_ = value[6]
                random_value1 = None
                random_value2 = None
                ratio = 0

                if ar1 == 'enum':
                    if attr1 == '是否在销':
                        input_data1 = ''
                    else:
                        random_value1 = random.choice(enum_[attr1])
                        input_data1 = str(random_value1)
                # elif ar1 == 'max' or ar1 == 'min':
                #     input_data1 = ''
                else:
                    if ar1 == 'area_value':
                        random_value1 = random.choice(others_['value_ratio'])
                    else:
                        random_value1 = random.choice(others_[ar1])
                    input_data1 = 表格实例拆分.check_type_and_return(ar1, random_value1)
                if type(input_data1) == list and len(input_data1) == 2:
                    ratio = 1

                if ar2 == 'enum':
                    if attr2 == '是否在销':
                        input_data2 = ''
                    else:
                        random_value2 = random.choice(enum_[attr2])
                        input_data2 = str(random_value2)
                # elif ar2 == 'max' or ar2 == 'min':
                #     input_data2 = ''
                else:
                    if ar2 == 'area_value':
                        random_value2 = random.choice(others_['value_ratio'])
                    else:
                        random_value2 = random.choice(others_[ar2])
                    input_data2 = 表格实例拆分.check_type_and_return(ar2, random_value2)
                if type(input_data2) == list and len(input_data2) == 2:
                    ratio = 2
                # print(input_data1, input_data2)

                if re.findall('<\w*1\w*>', question):
                    question = re.split('<\w*1\w*>', question)
                    question.insert(1, str(random_value1))
                    question = "".join(question)

                if re.findall('<\w*2\w*>', question):
                    question = re.split('<\w*2\w*>', question)
                    question.insert(1, str(random_value2))
                    question = "".join(question)

                if '<a>' in question:
                    question = re.split('<a>', question)
                    if a_ == 'fund':
                        a_ = '基金公司'
                    elif a_ == 'agent':
                        a_ = '机构名称'
                    elif a_ == 'manager':
                        a_ = '基金经理'
                    question.insert(1, a_)
                    question = "".join(question)

                if re.findall('<attr[12]_area_[vr]a[lt][ui][eo]\d{1}>', sql_):
                    org_sql = re.split('<attr[12]_area_[vr]a[lt][ui][eo]\d{1}>', sql_)
                    if ratio == 1:
                        org_sql.insert(1, str(input_data1[0]))
                        org_sql.insert(3, str(input_data1[1]))
                        org_sql = "".join(org_sql)
                        if re.findall('<\w*>', org_sql):
                            if type(input_data2) == list:
                                org_sql = re.split('<\w*>', org_sql)
                                org_sql.insert(1, "'" + str(input_data2[0] + "'"))
                                org_sql = "".join(org_sql)
                            if type(input_data2) == float or type(input_data2) == int:
                                org_sql = re.split('<\w*>', org_sql)
                                org_sql.insert(1, str(input_data2))
                                org_sql = "".join(org_sql)
                            else:
                                org_sql = re.split('<\w*>', org_sql)
                                org_sql.insert(1, "'" + str(input_data2) + "'")
                                org_sql = "".join(org_sql)
                    elif ratio == 2:
                        org_sql.insert(1, input_data2[0])
                        org_sql.insert(3, input_data2[1])
                        org_sql = "".join(org_sql)
                        if re.findall('<\w*>', org_sql):
                            if type(input_data1) == list:
                                org_sql = re.split('<\w*>', org_sql)
                                org_sql.insert(1, "'" + str(input_data1[0] + "'"))
                                org_sql = "".join(org_sql)
                            elif type(input_data1) == float or type(input_data1) == int:
                                org_sql = re.split('<\w*>', org_sql)
                                org_sql.insert(1, str(input_data1))
                                org_sql = "".join(org_sql)
                            else:
                                org_sql = re.split('<\w*>', org_sql)
                                org_sql.insert(1, "'" + str(input_data1) + "'")
                                org_sql = "".join(org_sql)
                else:
                    org_sql = sql_
                    # print(org_sql)
                    if re.findall('<\w*1+\w*>', org_sql):
                        if type(input_data1) == list:
                            # print('1_1')
                            org_sql = re.split('<\w*1+\w*>', org_sql)
                            org_sql.insert(1, "'" + str(input_data1[0] + "'"))
                            org_sql = "".join(org_sql)
                        elif type(input_data1) == float or type(input_data1) == int:
                            # print('2_1')
                            org_sql = re.split('<\w*1+\w*>', org_sql)
                            org_sql.insert(1, str(input_data1))
                            org_sql = "".join(org_sql)
                        else:
                            # print('3_1')
                            org_sql = re.split('<\w*1+\w*>', org_sql)
                            org_sql.insert(1, "'" + str(input_data1) + "'")
                            org_sql = "".join(org_sql)
                    if re.findall('<\w*2+\w*>', org_sql):

                        if type(input_data2) == list:
                            # print('1_2')
                            org_sql = re.split('<\w*2+\w*>', org_sql)
                            org_sql.insert(1, "'" + str(input_data2[0] + "'"))
                            org_sql = "".join(org_sql)
                        elif type(input_data2) == float or type(input_data2) == int:
                            # print('2_2')
                            org_sql = re.split('<\w*2+\w*>', org_sql)
                            org_sql.insert(1, str(input_data2))
                            org_sql = "".join(org_sql)
                        else:
                            # print('3_2')
                            org_sql = re.split('<\w*2+\w*>', org_sql)
                            org_sql.insert(1, "'" + str(input_data2) + "'")
                            org_sql = "".join(org_sql)
                    # print(question)
                    temp_dict["db_id"] = "kg"
                    temp_dict["query"] = org_sql
                    temp_dict["question"] = question
                    temp_dict['question_id'] = 'qid' + str(count)
                    query = "".join(org_sql.split('kg.'))
                    temp_dict['sql'] = m_d.get_sql(schema_, query, 'kg')
                    # print(temp_sql)
                    if test_ and count % 5 == 0:
                        # temp_dict.pop("sql")
                        # temp_dict.pop("query")
                        # temp_dict['query'] = ""
                        # temp_dict['sql'] = ""
                        result2.append(temp_dict)
                        test_2.append(question + '#' + query + '\n')
                        temp_dict = {}
                        count += 1
                    elif test_ and count % 4 == 0:
                        # temp_dict.pop("sql")
                        # temp_dict.pop("query")
                        # temp_dict['query'] = ""
                        # temp_dict['sql'] = ""
                        result3.append(temp_dict)

                        temp_dict = {}
                        count += 1
                    else:
                        result.append(temp_dict)
                        train_1.append(question + '#' + query + '\n')
                        temp_dict = {}
                        count += 1

    except Exception as e:
        print(traceback.format_exc())
        print(value)
        print(org_sql)
        print(e)
        print(query)
        print(random_value2)
        print(random_value1)
        sys.exit(1)
    finally:
        return count


def generate_data_db(excel_xlsx, output_path, test_path, dev_path, train1_path, test2_path, db_schema):
    result = []
    result2 = []
    result3 = []
    train1 = []
    test2 = []
    try:
        enum, others, entity = entity_load.generate_dict(excel_xlsx)
        rp = entity_load.generate_relationship(excel_xlsx, "属性数值转换", "A:B")
        list1 = [excel_xlsx, '实体查单属性模板', 'B,C,D', entity, others]
        count = 0
        count = data_structer_generater_a([list1], result, db_schema, result2, result3, train1, test2, True, count)
        print('a完成', count)
        list2 = [excel_xlsx, '实体查多属性模板', "A:G", enum, entity, others]
        count = data_structer_generater_ab([list2], result, db_schema, result2, result3, train1, test2, True, count)
        print('b完成', count)
        # list3 = [excel_xlsx, '单属性查实体模板', "A:C, G", others, enum]
        # count = data_structer_generater_ba([list3], result, db_schema, result2, True, count)
        # print('c完成', count)
        # list4 = [excel_xlsx, '多属性查实体模板', "A:G", others, enum, rp]
        # count = data_structer_generater_bba([list4], result, db_schema, result2, True, count)
        # print('d完成', count)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        sys.exit(1)
    finally:
        f1 = open(output_path, mode='w', encoding="utf-8")
        f1.write(json.dumps(result))
        f2 = open(test_path, mode='w', encoding="utf-8")
        f2.write(json.dumps(result2))
        f3 = open(dev_path, mode='w', encoding="utf-8")
        f3.write(json.dumps(result3))
        f4 = open(train1_path, mode='w', encoding="utf-8")
        for item in train1:
            if '\n\n\n' in item:
                item = "\n\n".strip(item)
            f4.write(item)
        f5 = open(test2_path, mode='w', encoding="utf-8")
        for item in test2:
            if '\n\n\n' in item:
                item = "\n\n".strip(item)
            f5.write(item)
        # print(result)
        f1.close()
        f2.close()
        f3.close()
        print('导出成功')


if __name__ == "__main__":
    conn = pymysql.connect(host='192.168.209.110', port=3307, user='messi', password='messi', charset='utf8',
                           database='kg')
    cursor = conn.cursor()

    data_content_generate(['机构表', '基金表', '基金经理表', '基金与基金经理关联表'],
                          'E:\project\data\DuSQL\db_content.json')
    db_struct_generate(['机构表', '基金表', '基金经理表', '基金与基金经理关联表'],
                       'E:\project\data\DuSQL\db_schema.json')

    schema = m_d.get_schema_from_json2("E:\project\data\DuSQL\db_schema.json")[0]['kg']
    generate_data_db('C:/Users/yifan.zhao01/Desktop/模板.xlsx', 'E:/project/data/DuSQL/train.json',
                     'E:/project/data/DuSQL/test.json', 'E:/project/data/DuSQL/dev.json',
                     'E:/project/data/DuSQL/train.sql', 'E:/project/data/DuSQL/test.sql', schema, )
    #
    # cursor.close()
    # conn.close()
