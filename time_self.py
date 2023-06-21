import datetime
import re
import json


def recognize_date(date_: str):
    """
    时间表达有4类
    1.日月年表示法：日期表示方式可以是日、月和年，如28Jan2021。
    2.月日年表示法：将日月年表示法中，日和月进行调换，显示为月、日和年，如Jan202020。
    3.带有横杠法：带有横杆表示日期，如2021-02-14。
    4.带有斜杠法：使用斜杠表示日期，如2021/1/31。
    具体输入不一定存在具体日期，只有年份或者月份
    #2021-02， 2021/3, 4月2023, 2020年5月，今年4月，去年2月，5年前，年末
    或者当前时间倒推或正推
    #上周，半年前，上个月，上半年，
    还有可能是时间段(时间段分段处理)
    #去年年底到今年年初，2年前至今，2021年4月1号之后20天
    """
    date_ = date_ + ' '
    result = []

    month_ = ['JAN', 'FEB', 'MAR', 'APR',
              'MAY', 'JUN', 'JUL', 'AUG',
              'SEP', 'OCT', 'NOV', 'DEC']
              # 'January', 'February', 'March',
              # 'April', 'June', 'July', 'August',
              # 'September', 'October', 'November', 'December'
    rel_month_ = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    # month_C = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月',
    #            '月', 'yue']

    # 先提取传统格式日期
    if re.search('\d{4}[-]+\d{1,2}[-]+\d{1,2}', date_):
        result += re.findall('\d{4}[-]+\d{1,2}[-]+\d{1,2}', date_)
    if re.search('\d{4}[/]\d{1,2}[/]+\d{1,2}', date_):
        for i in re.findall('\d{4}[/]\d{1,2}[/]+\d{1,2}', date_):
            new_ = i.replace('/', '-')
            result.append(new_)
    if re.search("\d{1,2}\D{3}\d{4}", date_):
        for i in re.findall("\d{1,2}\D{3}\d{4}", date_):
            temp_ = re.match(r'(\d{1,2})(\D{3})(\d{4})', i)
            if month_.index(temp_.group(2).upper()) + 1 <= 10:
                mon_ = str(0) + str(month_.index(temp_.group(2).upper())+1)
            result.append(str(temp_.group(3)) + '-' + mon_ + '-' + str(temp_.group(1)))


    if re.search("\D{3}\d{2}\d{4}", date_):
        for i in re.findall("\D{3}\d{2}\d{4}", date_):
            temp_ = re.match(r'(\D{3})(\d{2})(\d{4})', i)
            if month_.index(temp_.group(1).upper()) + 1 <= 10:
                mon_ = str(0) + str(month_.index(temp_.group(1).upper())+1)
            result.append(str(temp_.group(3)) + '-' + mon_ + '-' + str(temp_.group(2)))
    # 提取非传统格式日期(只有年月的）
    if re.search('\d{4}[-]+\d{1,2}[^-\d]', date_):
        temp = re.findall('\d{4}[-]+\d{1,2}[^-\d]', date_)
        for elements_ in temp:
            result.append(elements_[0:len(elements_) - 1])
    if re.search('\d{4}[/]+\d{1,2}[^/\d]', date_):
        temp = re.findall('\d{4}[/]+\d{1,2}[^/\d]', date_)
        for elements_ in temp:
            result.append(elements_.replace('/', '-')[0:len(elements_) - 1])
    # 中文年月日
    if re.search('\d{1,2}[月]\d{1,2}[日号]\d{4}[年]?', date_):
        temp = re.findall('\d{1,2}[月]\d{1,2}[日号]\d{4}[年]?', date_)
        for i in temp:
            temp_ = re.match(r'(\d{1,2})(\D)(\d{2})(\D)(\d{4})', i)
            mon_ = str(temp_.group(1))
            day_ = str(temp_.group(3))
            if int(temp_.group(1)) <= 10:
                mon_ = str(0) + str(temp_.group(1))
            if int(temp_.group(3)) <= 10:
                day_ = str(0) + str(temp_.group(3))
            result.append(str(temp_.group(5)) + '-' + mon_+'-' + day_)
    if re.search('\d{4}[年]\d{1,2}[月]\d{1,2}[日号]', date_):
        temp = re.findall('\d{4}[年]\d{1,2}[月]\d{1,2}[日号]', date_)
        for i in temp:
            temp_ = re.match(r'(\d{4})(\D)(\d{1,2})(\D)(\d{1,2})', i)
            mon_ = str(temp_.group(3))
            day_ = str(temp_.group(5))
            if int(temp_.group(3)) <= 10:
                mon_ = str(0) + str(temp_.group(3))
            if int(temp_.group(5)) <= 10:
                day_ = str(0) + str(temp_.group(5))
            result.append(str(temp_.group(1)) + '-' + mon_ + '-' + day_)
    if re.search('\d{4}[年]\d{1,2}[月][^\d]', date_):
        temp = re.findall('\d{4}[年]\d{1,2}[月][^\d]', date_)
        for i in temp:
            temp_ = re.match(r'(\d{4})(\D)(\d{1,2})', i)
            mon_ = str(temp_.group(3))
            if int(temp_.group(3)) <= 10:
                mon_ = str(0) + str(temp_.group(3))
            result.append(str(temp_.group(1)) + '-' + mon_)
    # 今年不带具体日期或者不带月份
    if re.search('今年[^\d]', date_):
        temp = re.findall('今年[^\d]', date_)
        for item in temp:
            result.append(str(datetime.date.today().year))
    if re.search('今年\d{0,2}[月][^\d]', date_):
        temp = re.findall('今年\d{0,2}[月][^\d]', date_)
        print()
        for item in temp:
            if len(item)-1 >= 4:
                if len(item)-1 >= 5:
                    result.append(str(datetime.date.today().year) + '-' + item[2:4])
                else:
                    result.append(str(datetime.date.today().year) + '-0' + item[2:3])
            else:
                result.append(str(datetime.date.today().year))
    # 今年带月份日期
    if re.search('今年\d{1,2}[月]\d{1,2}[号日]', date_):
        temp = re.findall('今年\d{1,2}[月]\d{1,2}[号日]', date_)
        for item in temp:
            temp_ = re.match(r'(\D{2})(\d{1,2})(\D)(\d{1,2})(\D)', item)
            mon_ = str(temp_.group(2))

            day_ = str(temp_.group(4))
            if int(temp_.group(2)) < 10:
                mon_ = str(0) + str(temp_.group(2))
            if int(temp_.group(4)) < 10:
                day_ = str(0) + str(temp_.group(4))
            result.append(str(datetime.date.today().year) + '-' + mon_ + '-' + day_)
    # 去年代月份
    if re.search('[去上]年[^\d]', date_):
        temp = re.findall('[去上]年[^\d]', date_)
        for item in temp:
            result.append(str(datetime.date.today().year-1))
    if re.search('[去上]年\d{0,2}[月][^\d]', date_):
        temp = re.findall('[去上]年\d{0,2}[月][^\d]', date_)
        print()
        for item in temp:
            if len(item) - 1 >= 4:
                if len(item) - 1 >= 5:
                    result.append(str(datetime.date.today().year-1) + '-' + item[2:4])
                else:
                    result.append(str(datetime.date.today().year-1) + '-0' + item[2:3])
            else:
                result.append(str(datetime.date.today().year-1))
    # 去年代月份日期
    if re.search('[去上]年\d{1,2}[月]\d{1,2}[号日]', date_):
        temp = re.findall('[去上]年\d{1,2}[月]\d{1,2}[号日]', date_)
        for item in temp:
            temp_ = re.match(r'(\D{2})(\d{1,2})(\D)(\d{1,2})(\D)', item)
            mon_ = str(temp_.group(2))

            day_ = str(temp_.group(4))
            if int(temp_.group(2)) < 10:
                mon_ = str(0) + str(temp_.group(2))
            if int(temp_.group(4)) < 10:
                day_ = str(0) + str(temp_.group(4))
            result.append(str(datetime.date.today().year-1) + '-' + mon_ + '-' + day_)
    # x年前不带月份
    if re.search('\d{1,3}年前[^\d]', date_):
        temp = re.findall('\d{1,3}年前[^\d]', date_)
        for item in temp:
            result.append(str(datetime.date.today().year - int(item[:-3])))
    # x年前带月份
    if re.search('\d{1,3}年前\d{1,2}月', date_):
        temp = re.findall('\d{1,3}年前\d{1,2}月', date_)
        for item in temp:
            list_ = item.split('年前')
            mon_ = list_[1][:-1]
            if len(mon_) < 2:
                mon_ = str(0) + str(mon_)

            result.append(str(datetime.date.today().year - int(list_[0])) + '-' + mon_)
    # 年初年末转换日期
    if re.search('\d{4}[年]?年初', date_):
        temp = re.findall('\d{4}[年]?年初', date_)
        for item in temp:
            result.append(item[0:4] + '-01-01')
    if re.search('\d{4}[年]?年末', date_):
        temp = re.findall('\d{4}[年]?年末', date_)
        for item in temp:
            result.append(item[0:4] + '-12-31')
    # 前年代月份
    if re.search('前年[^\d]', date_):
        temp = re.findall('前年[^\d]', date_)
        for item in temp:
            result.append(str(datetime.date.today().year - 2))
    if re.search('前年\d{0,2}[月][^\d]', date_):
        temp = re.findall('前年\d{0,2}[月][^\d]', date_)
        for item in temp:
            if len(item) - 1 >= 4:
                if len(item) - 1 >= 5:
                    result.append(str(datetime.date.today().year - 2) + '-' + item[2:4])
                else:
                    result.append(str(datetime.date.today().year - 2) + '-0' + item[2:3])
            else:
                result.append(str(datetime.date.today().year - 2))
    if re.search('前年\d{1,2}[月]\d{1,2}[号日]', date_):
        temp = re.findall('前年\d{1,2}[月]\d{1,2}[号日]', date_)
        for item in temp:
            temp_ = re.match(r'(\D{2})(\d{1,2})(\D)(\d{1,2})(\D)', item)
            mon_ = str(temp_.group(2))

            day_ = str(temp_.group(4))
            if int(temp_.group(2)) < 10:
                mon_ = str(0) + str(temp_.group(2))
            if int(temp_.group(4)) < 10:
                day_ = str(0) + str(temp_.group(4))
            result.append(str(datetime.date.today().year - 2) + '-' + mon_ + '-' + day_)

    # 上半年，下半年
    if re.search('\d{4}年?上半年', date_):
        temp = re.findall('\d{4}年?上半年', date_)
        for item in temp:
            result.append(str(item[:4])+'-01-01')
            result.append(str(item[:4])+'-06-30')

    if re.search('\d{4}年?下半年', date_):
        temp = re.findall('\d{4}年?下半年', date_)
        for item in temp:
            result.append(str(item[:4])+'-07-01')
            result.append(str(item[:4])+'-12-31')

    if re.search('\d{4}年?第?[一1]季度', date_):
        temp = re.findall('\d{4}年?第?[一1]季度', date_)
        for item in temp:
            result.append(str(item[:4])+'-01-01')
            result.append(str(item[:4])+'-03-31')

    if re.search('\d{4}年?第?[二2]季度', date_):
        temp = re.findall('\d{4}年?第?[二2]季度', date_)
        for item in temp:
            result.append(str(item[:4])+'-04-01')
            result.append(str(item[:4])+'-06-30')
    if re.search('\d{4}年?第?[三3]季度', date_):
        temp = re.findall('\d{4}年?第?[三3]季度', date_)
        for item in temp:
            result.append(str(item[:4])+'-07-01')
            result.append(str(item[:4])+'-09-30')
    if re.search('\d{4}年?第?[四4]季度', date_):
        temp = re.findall('\d{4}年?第?[四4]季度', date_)
        for item in temp:
            result.append(str(item[:4])+'-10-01')
            result.append(str(item[:4])+'-12-31')
    return result


def analysis_date(list_date_: [datetime]):
    # 分析具体日期是上半年/下半年，第几季度，第几个月的，第几周
    result = []
    for item in list_date_:
        data_ = str(item).split('-')
        first_half_year = True
        season = 0
        month = data_[1]
        if data_[1] >= '07':
            first_half_year = False
        if data_[1] < '04':
            season = 1
        if '03' <= data_[1] < '07':
            season = 2
        if '07' <= data_[1] < '10':
            season = 3
        if '10' <= data_[1] < '13':
            season = 4
        tempresult = {'first_half_year': first_half_year, 'month': month, 'season': season,
                      'week': (item.strftime('%Y,%W,%w'))}
        result.append(tempresult)

    return json.dumps(result)

def datetime_transform(date_list: list):
    result = []
    for item in date_list:
        temp = item.split('-')
        result.append(datetime.date(int(temp[0]), int(temp[1]), int(temp[2])))
    return result

if __name__ == '__main__':
    data = recognize_date('2023-02-12')
    data_ = datetime_transform(data)

    print(analysis_date(data_))


    # example = [datetime.date(2018, 4, 26),datetime.date(2018, 5, 26)]
    # print(analysis_date(example))