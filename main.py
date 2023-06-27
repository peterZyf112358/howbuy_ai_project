# -*- coding: utf-8 -*-
import pymysql
import pandas as pd
import entity_load
import random
import re
import 表格实例拆分
import time_self


attr_ = [['<attr1_value>'], ['<attr1_topk>'], ['<attr1_ratio>'], ['<attr1_pos>'], ['<attr1_neg>'], ['<attr1_min>'], ['<attr1_max>'], ['<attr1_enum>'], ['<value>'], ['<attr1_date>'], ['<attr1_area_value>'], ['<attr1_area_ratio>']]

def test_all_a_ab_command(path, table, usecols, entity, others_):
    wb = pd.read_excel(path, sheet_name=table, usecols=usecols, header=1)
    time = 0
    count = 0
    try:
        for value in wb.values:
            if re.search('<topk>', value[1]):
                temp = re.split('<\w*>', value[1])
                sql = temp[0] + "'" + random.choice(entity[value[0]]) + "'" + temp[1] + random.choice(others_['topk'])
            else:
                temp = value[1].split('<e>')
                sql = temp[0] + "'" + random.choice(entity[value[0]]) + "'" + temp[1]
                cursor.execute(sql)
                count += 1
            if count % 100 == 0:
                print(count)
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close()
    #     conn.close()


def test_all_ba_bba_command(path, table, usecols_, others_, enum_):
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
    # finally:
    #     cursor.close()
    #     conn.close()

if __name__ == '__main__':
    conn = pymysql.connect(host='192.168.209.110', port=3307, user='messi', password='messi', charset='utf8',
                           database='kg')
    cursor = conn.cursor()
    enum, others, entity = entity_load.generate_dict()
    # test_all_a_ab_command('C:/Users/yifan.zhao01/Desktop/模板.xlsx', '实体查单属性模板', 'C:D', entity, others)
    # test_all_a_ab_command('C:/Users/yifan.zhao01/Desktop/模板.xlsx', '实体查多属性模板', 'F:G', entity, others)
    test_all_ba_bba_command('C:/Users/yifan.zhao01/Desktop/模板.xlsx', '单属性查实体模板', "A,C,G", others, enum)

    cursor.close()
    conn.close()