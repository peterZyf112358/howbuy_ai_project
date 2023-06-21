import random
def generate_item(file1, file2):
    f1 = open(file1, mode='w', encoding="utf-8")
    f2 = open(file2, mode="r", encoding="utf-8")
    content = f2.readlines()
    temp_list = []
    i = 0
    j = 1
    for item in content:
        n_item = item.replace('\n', '')
        temp_list.append(n_item)
    for item in temp_list:
        while i <= j < len(temp_list):
            f1.write(item + ', ')
            f1.write(temp_list[j])
            f1.write('\r')
            j += 1
        i += 1
        j = i + 1
    f1.close()
    f2.close()

def generate_sql_code(file1, file2, file3):
    f1 = open(file1, mode='w', encoding="utf-8")
    f2 = open(file2, mode="r", encoding="utf-8")
    f3 = open(file3, mode="r", encoding="utf-8")
    content = f2.readlines()
    content2 = f3.readlines()
    temp_list = []
    temp_list2 = []
    for item in content:
        n_item = item.replace('\n', '')
        temp_list.append(n_item)
    for item in content2:
        n_item = item.replace('\n', '')
        temp_list2.append(n_item)
    for item in temp_list:
        f1.write('#select '+ item + " from 基金表 where 基金全称 = " + random.choice(temp_list2))
        f1.write('\r')
    f1.close()
    f2.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    file1 = 'C:/Users/yifan.zhao01/desktop/sql.txt'
    file2 = 'C:/Users/yifan.zhao01/desktop/new.txt'
    file3 = 'C:/Users/yifan.zhao01/desktop/基金全称.txt'
    # generate_item(file1, file2)
    generate_sql_code(file1, file2, file3)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
