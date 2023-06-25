import re

chinese_number = ['零','一', '二', '三', '四', '五', '六', '七', '八', '九']
unit = ['亿','千','万']

def ratio_to_value(data_):
    result = []
    if re.match('\d+个点', data_):
        result.append(re.findall('\d+', data_)[0])
    if re.findall('[一二三四五六七八九]十{0,1}[一二三四五六七八九]{0,1}个点',data_):
        for item in re.findall('[一二三四五六七八九]十{0,1}[一二三四五六七八九]{0,1}',data_)[0]:
            if item in chinese_number:
                result.append(chinese_number.index(item))
            if item == '十':
                if data_.index(item) == len(data_):
                    result.append(0)
    if re.match('\d+%', data_):
        result.append(re.findall('\d+', data_)[0])
    if re.match('百分之[\d+一二三四五六七八九十]', data_):
        if re.findall('\d+', data_):
            result.append(re.findall('\d+', data_)[0])
        else:
            for item in data_:
                if item in chinese_number:
                    result.append(chinese_number.index(item))
                if item == '十':
                    if data_.index(item) == len(data_):
                        result.append(0)
    if re.match('0.\d+',data_):
        result.append((float(re.findall('0.\d+',data_)[0]) * 100))
    else:
        return None
    return float("".join([str(x) for x in result]))


def value_to_value(value):
    result = []
    if re.match('\d+[亿万千]*个{0,1}[亿万千]*', value):
        for item in re.findall('\d+[亿万千]*个{0,1}[亿万千]*',value)[0]:
            if item.isdigit():
                result.append(item)
            if item == '亿':
                result.append('00000000')
            if item == '万':
                result.append('00000')
            if item == '千':
                result.append('000')
    else:
        return None
    return float("".join([str(x) for x in result]))


def value_ratio_to_value(value):
    result = []
    if re.match('\d+-\d+[亿万千]+',value):
        units = re.findall('[亿万千]+', value)[0]
        for item in re.findall('\d+',value):
            result.append(value_to_value(item+units))
    if re.match('\d+[%]{0,1}[亿万千]*', value):
        for item in re.findall('\d+[%]{0,1}[亿万千]*', value):
            result.append(value_to_value(item))
    else:
        return None
    return result

def topk_to_value(value: str):
    result = []
    for item in value:
        if item.isdigit():
            result.append(item)
    return ''.join(result)

def check_value(item_):
    ratio = ratio_to_value(item_)
    value = value_to_value(item_)
    value_ratio = value_ratio_to_value(item_)
    if not ratio:
        return ratio
    if not value:
        return value
    if not value_ratio:
        return value_ratio
    else:
        raise 'the input cannot translate to any form'


if __name__ == '__main__':
    print(ratio_to_value('百分之50'))
    print(value_ratio_to_value('21-30万亿'))
    print(topk_to_value('前100'))