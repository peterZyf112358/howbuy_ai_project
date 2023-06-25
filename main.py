import pymysql
import pandas as pd
import entity_load
import random
import re
import 表格实例拆分

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
    finally:
        cursor.close()
        conn.close()
    # return result


def test_all_ba_bba_command(path, table, usecols, others_):
    """3列 第一列是 attr_name, 第二列是value_type, 第三列是 entity_type"""
    wb = pd.read_excel(path, sheet_name=table, usecols=usecols, header=1)
    time = 0
    count = 0
    try:
        for value in wb.values:
            if re.search('<\w{2,}>', value[1]):
                # if value[0] == 'enum':
                ###从这开始写
                item = re.findall('<\w{2,}>', value[1])[0]
                temp = "".split(value[1])
                sql = temp[0] + "'" + 表格实例拆分.check_value(random.choice(others_[item])) + "'" + temp[1]
                cursor.execute(sql)
            else:
                temp = "".split(value[1])



    except Exception as e:
        print(sql)
        print(e)
    finally:
        cursor.close()
        conn.close()



if __name__ == '__main__':
    conn = pymysql.connect(host='192.168.209.110', port=3307, user='messi', password='messi', charset='utf8',
                           database='kg')
    cursor = conn.cursor()
    enum, others, entity = entity_load.generate_dict()
    # test_all_a_ab_command('C:/Users/yifan.zhao01/Desktop/模板.xlsx', '实体查单属性模板', 'C:D', entity, others)
    test_all_a_ab_command('C:/Users/yifan.zhao01/Desktop/模板.xlsx', '实体查多属性模板', 'F:G', entity, others)