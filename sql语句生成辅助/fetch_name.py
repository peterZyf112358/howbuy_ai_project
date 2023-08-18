import pymysql

def main():
    conn = pymysql.connect(host='192.168.209.110', port=3307, user='messi', password='messi', db='kg')
    cur = conn.cursor()

    cur.execute("select kg.基金表.基金全称 from kg.基金表")
    output = cur.fetchall()
    cur.execute("select kg.机构表.机构名称 from kg.机构表")
    output1 = cur.fetchall()
    cur.execute("select kg.基金经理表.经理姓名 from kg.基金经理表")
    output2 = cur.fetchall()
    cur.execute("select distinct kg.基金表.基金分类 from kg.基金表")
    output3 = cur.fetchall()
    cur.execute("select distinct kg.基金表.产品分类 from kg.基金表")
    output4 = cur.fetchall()
    cur.execute("select * from kg.基金经理表")

    f1_path = 'E:/project/data/DuSQL/fund_name.txt'
    f1 = open(f1_path, mode='w', encoding="utf-8")
    f1.write('[')

    for item in output:
        if item[0]:
            f1.write(str(item[0]) + ',')
    for item in output1:
        if item[0]:
            f1.write(str(item[0]) + ',')
    for item in output2:
        if item[0]:
            f1.write(str(item[0]) + ',')
    for item in output3:
        if item[0]:
            f1.write(str(item[0]) + ',')
    for item in output4:
        if item[0]:
            f1.write(str(item[0]) + ',')
    f1.write('销售')
    f1.write(']')
    f1.close()


if __name__ == '__main__':
    main()