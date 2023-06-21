import re

chinese_number = ['零','一', '二', '三', '四', '五', '六', '七', '八', '九']

def ratio_to_value(data_):
    result = []
    if re.match('\d+个点', data_):
        return re.findall('\d+', data_)[0]
    if re.match('\d+%', data_):
        return re.findall('\d+', data_)[0]
    if re.match('百分之[\d+一二三四五六七八九十]', data_):
        if re.findall('\d+', data_):
            return re.findall('\d+', data_)
        else:
            for item in data_:
                if item in chinese_number:
                    result.append(chinese_number.index(item))
                if item == '十':
                    if not data_.index(item) == len(data_):
                        result.append(0)
            return result


if __name__ == '__main__':
    print(ratio_to_value('百分之九十'))
