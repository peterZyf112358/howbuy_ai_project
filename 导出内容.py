
def generate_twin(file1, file2):
    f1 = open(file1, mode='w', encoding="utf-8")
    f2 = open(file2, mode="r", encoding="utf-8")
    content = f2.readlines()

    list_ = content[0].split(',')
    print(list_)
    temp_list = []
    i = 0
    j = 1
    for item in list_:
        while i <= j < len(list_):
            f1.write("select distinct " + item + ', ' + list_[j] + ' from kg.基金表; \r')
            j += 1
        i += 1
        j = i + 1
    f1.close()
    f2.close()

def generate_single(file1, file2):
    f1 = open(file1, mode='w', encoding="utf-8")
    f2 = open(file2, mode="r", encoding="utf-8")
    content = f2.readlines()

    list_ = content[0].split(',')
    print(list_)
    temp_list = []
    for item in list_:
        f1.write("select distinct " + item + ' from kg.基金表; \r')

    f1.close()
    f2.close()


if __name__ == '__main__':
    file1 = 'C:/Users/yifan.zhao01/desktop/new.txt'
    file2 = 'C:/Users/yifan.zhao01/desktop/测试.txt'
    generate_single(file2, file1)