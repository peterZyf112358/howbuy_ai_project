# -*- coding: utf-8 -*-
import pymysql
import pandas as pd
import entity_load
import random
import re
import 表格实例拆分
import time_self
import 导出内容


attr_ = [['<attr1_value>'], ['<attr1_topk>'], ['<attr1_ratio>'], ['<attr1_pos>'], ['<attr1_neg>'], ['<attr1_min>'], ['<attr1_max>'], ['<attr1_enum>'], ['<value>'], ['<attr1_date>'], ['<attr1_area_value>'], ['<attr1_area_ratio>']]

def test_all_a_ab_command(path, table, usecols, entity, others_):
    wb = pd.read_excel(path, sheet_name=table, usecols=usecols, header=1)
    time = 0
    count = 0
    try:
        for value in wb.values:
            # if count <= 5700:
            #     count += 1
            #     # print(time)
            #     continue
            if re.search('<topk>', value[1]):
                temp = re.split('<\w*>', value[1])

                sql = temp[0] + "'" + random.choice(entity[value[0]]) + "'" + temp[1] + str(表格实例拆分.topk_to_value(random.choice(others_['topk'])))
            else:
                temp = value[1].split('<e>')
                sql = temp[0] + "'" + random.choice(entity[value[0]]) + "'" + temp[1]
            cursor.execute(sql)
            count += 1
            if count % 100 == 0:
                print(count)
    except Exception as e:
        print(value)
        print(temp)
        print(sql)
        print(e)
    # finally:
    #     cursor.close()
    #     conn.close()


def test_all_ba_command(path, table, usecols_, others_, enum_):
    """3列 第一列是 attr_name, 第二列是value_type, 第三列是 entity_type"""
    wb = pd.read_excel(path, sheet_name=table, usecols=usecols_, header=1)
    count = 0
    try:

        for value in wb.values:

            # if count < 450:
            #     count += 1
            #     continue
            # elif re.search('<\w{2,}>', value[2]):
            if re.search('<\w{2,}>', value[2]):
                print(count)
                # print(value[2])
                item = re.findall('<\w{2,}>', value[2])[0]
                if value[1] == 'area_ratio' or value[1] == 'value_ratio' or value[1] == 'area_value':
                    data_ = random.choice(others_['area_ratio'])
                    real_value = 表格实例拆分.value_ratio_to_value(data_)
                    # print(real_value)
                    temp = re.split('<\w{2,}>',value[2])
                    sql = temp[0] + real_value[0] + temp[1] + real_value[1] + temp[2]
                    cursor.execute(sql)
                elif value[1] == 'enum':
                    data_ = random.choice(enum_[value[0]])
                    # print(data_)
                    temp = re.split('<\w{2,}>', value[2])
                    sql = temp[0] + "'" + data_ + "'" + temp[1]
                    cursor.execute(sql)
                else:
                    temp = re.split('<\w{2,}>', value[2])
                    real_value = None
                    value_ = random.choice(others_[value[1]])
                    if value[1] == 'value':
                        real_value = 表格实例拆分.value_to_value(value_)
                    elif value[1] == 'ratio':
                        real_value = 表格实例拆分.ratio_to_value(value_)
                    elif value[1] == 'date':
                        real_value = time_self.recognize_date(value_)[0]
                        # print(real_value)
                    elif value[1] == 'area_ratio' or value[1] == 'value_ratio' or value[1] == 'area_value':
                        real_value = 表格实例拆分.value_ratio_to_value(value_)
                    elif value[1] == 'topk':
                        real_value = 表格实例拆分.topk_to_value(value_)

                    if real_value:
                        # print('进1')
                        sql = temp[0] + str(real_value) + temp[1]
                    else:
                        # print('进2')
                        sql = temp[0] + "'" + random.choice(others_[value[1]]) + "'" + temp[1]
                    cursor.execute(sql)

                count += 1
                # if count % 10 == 0:
                #     print(count)
    except Exception as e:
        print(data_)
        print(value, value_)
        print('问题', e)

def test_al_bba_command(path, table, usecols_, others_, enum_, relationship_path):
    """3列 第一列是 attr_name, 第二列是value_type, 第三列是 entity_type"""
    wb = pd.read_excel(path, sheet_name=table, usecols=usecols_, header=1)
    count = 0
    try:

        rp = relationship_path
        # attr1	attr2 module	attr1_relation	attr2_relation sql
        for value in wb.values:
            print(count)
            attr1 = value[0]
            attr2 = value[1]
            question = value[2]
            ar1 = rp[value[3]]
            ar2 = rp[value[4]]
            sql = value[5]
            ratio = 0

            # if count <= 700:
            #     count+=1
            #     continue
            if ar1 == 'enum':
                if attr1 == '是否在销':
                    input_data1 = ''
                else:
                    random_value = random.choice(enum_[attr1])
                    input_data1 = str(random_value)
            elif ar1 == 'max' or ar1 == 'min':
                input_data1 = ''
            else:
                if ar1 == 'area_value':
                    random_value = random.choice(others_['value_ratio'])
                else:
                    random_value = random.choice(others_[ar1])
                input_data1 = 表格实例拆分.check_type_and_return(ar1, random_value)
            if type(input_data1) == list and len(input_data1) == 2:
                ratio = 1
            if ar2 == 'enum':
                if attr2 == '是否在销':
                    input_data2 = ''
                else:
                    random_value = random.choice(enum_[attr2])
                    input_data2 = str(random_value)
            elif ar2 == 'max' or ar2 == 'min':
                input_data2 = ''
            else:
                if ar2 == 'area_value':
                    random_value = random.choice(others_['value_ratio'])
                else:
                    random_value = random.choice(others_[ar2])
                input_data2 = 表格实例拆分.check_type_and_return(ar2, random_value)
            if type(input_data2) == list and len(input_data2) == 2:
                ratio = 2
            # print(input_data1, input_data2)

            if re.findall('<attr[12]_area_[vr]a[lt][ui][eo]\d{1}>', sql):
                org_sql = re.split('<attr[12]_area_[vr]a[lt][ui][eo]\d{1}>', sql)
                if ratio == 1:
                    org_sql.insert(1, input_data1[0])
                    org_sql.insert(3, input_data1[1])
                    org_sql = "".join(org_sql)
                    if re.findall('<\w*>', org_sql):
                        if type(input_data2) == list:
                            org_sql = re.split('<\w*>', org_sql)
                            org_sql.insert(1, input_data2[0])
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
                            org_sql.insert(1, input_data1[0])
                            org_sql = "".join(org_sql)
                        elif type(input_data1) == float or type(input_data1) == int:
                            org_sql = re.split('<\w*>', org_sql)
                            org_sql.insert(1, str(input_data1))
                            org_sql = "".join(org_sql)
                        else:
                            org_sql = re.split('<\w*>', org_sql)
                            org_sql.insert(1, "'" + str(input_data1) + "'")
                            org_sql = "".join(org_sql)
                cursor.execute(org_sql)
            else:
                org_sql = sql
                # print(org_sql)
                if re.findall('<\w*1+\w*>',org_sql):
                    if type(input_data1) == list:
                        # print('1_1')
                        org_sql = re.split('<\w*1+\w*>', org_sql)
                        org_sql.insert(1, input_data1[0])
                        org_sql = "".join(org_sql)
                    elif type(input_data1) == float or type(input_data1) == int:
                        #print('2_1')
                        org_sql = re.split('<\w*1+\w*>', org_sql)
                        org_sql.insert(1, str(input_data1))
                        org_sql = "".join(org_sql)
                    else:
                        #print('3_1')
                        org_sql = re.split('<\w*1+\w*>', org_sql)
                        org_sql.insert(1, "'" + str(input_data1) + "'")
                        org_sql = "".join(org_sql)
                if re.findall('<\w*2+\w*>', org_sql):

                    if type(input_data2) == list:
                        #print('1_2')
                        org_sql = re.split('<\w*2+\w*>', org_sql)
                        org_sql.insert(1, input_data2[0])
                        org_sql = "".join(org_sql)
                    elif type(input_data2) == float or type(input_data2) == int:
                        #print('2_2')
                        org_sql = re.split('<\w*2+\w*>', org_sql)
                        org_sql.insert(1, str(input_data2))
                        org_sql = "".join(org_sql)
                    else:
                        #print('3_2')
                        org_sql = re.split('<\w*2+\w*>', org_sql)
                        org_sql.insert(1, "'" + str(input_data2) + "'")
                        org_sql = "".join(org_sql)

                cursor.execute(org_sql)
            count += 1

    except Exception as e:
        print(input_data1,input_data2,attr1, attr2, ar1, ar2)
        print(sql)
        print(org_sql)
        print(question)
        print('问题', e)
    # finally:
    #     cursor.close()
    #     conn.close()

if __name__ == '__main__':
    conn = pymysql.connect(host='192.168.209.110', port=3307, user='messi', password='messi', charset='utf8',
                           database='kg')
    cursor = conn.cursor()
    enum, others, entity = entity_load.generate_dict()
    rp = 导出内容.generate_relationship('C:/Users/yifan.zhao01/desktop/转换.txt')
    test_all_a_ab_command('C:/Users/yifan.zhao01/Desktop/模板.xlsx', '实体查单属性模板', 'C:D', entity, others)
    test_all_a_ab_command('C:/Users/yifan.zhao01/Desktop/模板.xlsx', '实体查多属性模板', 'F:G', entity, others)
    test_all_ba_command('C:/Users/yifan.zhao01/Desktop/模板.xlsx', '单属性查实体模板', "A,C,G", others, enum)
    test_al_bba_command('C:/Users/yifan.zhao01/Desktop/模板.xlsx', '多属性查实体模板', "A:E, G", others, enum, rp)

    cursor.close()
    conn.close()