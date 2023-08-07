# -*- coding: utf-8 -*-
import re
import cn2an
from 转译文件 import time_self

chinese_number = ['零','一', '二', '三', '四', '五', '六', '七', '八', '九']
unit = ['亿','千','万']

def ratio_to_value(data_):
    result = []
    data_ = str(data_)
    if re.match('\d+个点', data_):
        result.append(re.findall('\d+', data_)[0])
    elif re.findall('[一二三四五六七八九]十{0,1}[一二三四五六七八九]{0,1}个点',data_):
        for item in re.findall('[一二三四五六七八九]十{0,1}[一二三四五六七八九]{0,1}',data_)[0]:
            if item in chinese_number:
                result.append(chinese_number.index(item))
            if item == '十':
                if data_.index(item) == len(data_):
                    result.append(0)
    elif re.match('\d+%', data_):
        result.append(re.findall('\d+', data_)[0])
    elif re.match('百分之[一二三四五六七八九十]*\d*', data_):
        if re.findall('\d+', data_):
            result.append(re.findall('\d+', data_)[0])
        else:
            count = 0
            for item in data_:
                if item in chinese_number:
                    result.append(chinese_number.index(item))
                elif item == '十':
                    if data_[count-1] not in chinese_number and count == len(data_)-1:
                        result.append(10)
                    elif data_.index(item) == len(data_)-1:
                        result.append(0)
                    elif data_[count-1] not in chinese_number:
                        result.append(1)
                count += 1
    elif re.match('0.\d+',data_):
        result.append((float(re.findall('0.\d+',data_)[0])*100))
    else:
        return None
    return float("".join([str(x) for x in result]))/100


def value_to_value(value):
    result = []
    value = str(value)
    if re.findall("[一二三四五六七八九十]{1,}个?[亿万千百]*", value):
        temp = re.findall("[一二三四五六七八九十]{1,}个?[亿万千百]*", value)[0]
        if '个' in temp:
            # print(temp)
            temp = "".join(re.split('个', temp))
            # print(temp)
        result.append(cn2an.cn2an(temp))
    elif re.match('\d+[亿万千百]*个{0,1}\d*[亿万千百]*', value):
        for item in re.findall('\d+[亿万千百]*个{0,1}\d*[亿万千百]*',value)[0]:
            if item.isdigit():
                result.append(item)
            if item == '亿':
                result.append('00000000')
            if item == '万':
                result.append('0000')
            if item == '千':
                result.append('000')
            if item == '百':
                result.append('00')
    else:
        return None
    return float("".join([str(x) for x in result]))

def value_ratio_to_value(value):
    result = []
    value = str(value)

    if re.search('百分之[\u4e00-\u9fa5]+-?[\u4e00-\u9fa5]?', value):
        units = re.findall('[一二三四五六七八九十]十?[一二三四五六七八九]?', value)
        if len(units) == 1:
            result.append('0')
            result.append(str(cn2an.cn2an(units[0])/100))
        else:
            for item in units:
                result.append(str(cn2an.cn2an(item)/100))
    elif re.search('百分之\d{2}-?\d{2}\d?', value):
        units= re.findall('百分之\d{2}-?\d{2}\d?', value)[0]
        if '-' not in units:
            numbers = re.findall('\d+', units)[0]
            result.append('0')
            result.append(str(int(numbers)/100))
        else:
            numbers = re.findall('\d+', units)
            for item in numbers:
                result.append(str(int(item)/100))
    elif re.match('\d+[-至到]+\d+[亿万千]+',value):
        units = re.findall('[亿万千]', value)[0]
        for item in re.findall('\d+',value):
            result.append(str(value_to_value(item+units)))
    elif re.match('\d+[亿万千]+[-至到]+\d+[亿万千]+',value):
        units = re.findall('[亿万千]+', value)
        units1 = units[0]
        units2 = units[1]
        index = 0
        for item in re.findall('\d+',value):
            if index == 0:
                result.append(str(value_to_value(item+units1)))
            elif index == 1:
                result.append(str(value_to_value(item + units2)))
            index += 1
    elif re.match('\d+-\d+个点',value) or re.match('\d+%?[-至到]+\d+%',value):
        for item in re.findall('\d+',value):
            result.append(str(value_to_value(item)/100))
    # elif re.match('\d+[%]{0,1}[亿万千]*', value):
    #     print(4)
    #     for item in re.findall('\d+[%]{0,1}[亿万千]*', value):
    #         result.append(str(value_to_value(item)))
    else:
        return None
    return result

def topk_to_value(value: str):
    result = []
    for item in value:
        if item.isdigit():
            result.append(item)
    return int(''.join(result))

def check_type_and_return(type, value):
    result = None
    if type == 'topk':
        result = topk_to_value(value)
    elif type == 'ratio':
        result = ratio_to_value(value)
    elif type == 'value':
        result = value_to_value(value)
    elif type == 'date':
        result = time_self.recognize_date(value)
    elif type == 'area_ratio' or type == 'value_ratio' or type == 'area_value':
        result = value_ratio_to_value(value)
    return result


if __name__ == '__main__':
    print(ratio_to_value('0.7'))
    # print(value_ratio_to_value('21-30万'))
    # print(topk_to_value('前6'))
    # output = cn2an.cn2an('五千万')
    # print(check_value('五千万'))
    print(value_ratio_to_value('1千万至25亿'))
