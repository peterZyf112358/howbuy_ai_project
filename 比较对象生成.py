import pandas as pd

def transpose(X):
    m,n = len(X), len(X[0])
    return [[X[i][j] for i in range(m)] for j in range(n)]


def generate_sql(path, written_file):
    wb = pd.read_excel(path, sheet_name='Sheet1', usecols="A:Q", header=1)
    f2 = open(written_file, mode="w", encoding="utf-8")
    header = []
    list_ = transpose(wb.values)
    for value in wb:
        header.append(value)
    # print(header)
    # print(list_)
    for i in range(len(list_)):
        for j in range(len(list_[i])):
            if list_[i][j] == list_[i][j]:
                for x in range(i + 1, len(list_)):
                    for y in range(len(list_[x])):
                        if list_[x][y] == list_[x][y]:

                            if type(list_[x][y]) == float:
                                a_result = str(list_[x][y])
                            else:
                                a_result = "'" + list_[x][y] + "'"
                            if type(list_[i][j]) == float:
                                b_result = str(list_[i][j])
                            else:
                                b_result = "'" + list_[i][j] + "'"
                            f2.write("#select 基金全称 from 基金表 where " + header[i]
                                  + ' = ' + b_result + ' and ' + header[x] + ' = ' + a_result +'\r')
    f2.close()

def check_include(path, sheet_name):
    wb = pd.read_excel(path, sheet_name=sheet_name, usecols="A:G", header=1)
    header = []
    list_ = transpose(wb.values)
    for value in wb:
        header.append(value)
    # print(header)
    # print(list_)
    for i in range(len(list_[0])-1):
        if list_[6][i] == list_[6][i]:
            if list_[0][i] not in list_[6][i]:
                print(str(i+3) + ' ' + list_[0][i] + ' ' + list_[6][i])
            # if list_[1][i] not in list_[6][i]:
            #     print(str(i+3) + ' ' + list_[1][i] + ' ' + list_[6][i])



if __name__ == '__main__':

    file1 = 'C:/Users/yifan.zhao01/Desktop/模板.xlsx'
    check_include(file1, '单属性查实体模板')
    # file1 = 'C:/Users/yifan.zhao01/Desktop/可重复.xlsx'
    # file2 = 'C:/Users/yifan.zhao01/desktop/test3.txt'
    # generate_sql(file1,file2)