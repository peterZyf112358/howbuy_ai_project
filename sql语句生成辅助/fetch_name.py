import pymysql

if __name__ == '__main__':
    conn = pymysql.connect(host='192.168.209.110', port=3307, user='messi', password='messi', db='kg')
    cur = conn.cursor()
    cur.execute("select kg.基金表.基金全称 from kg.基金表")
    output = cur.fetchall()
    cur.execute("select kg.机构表.机构名称 from kg.机构表")
    output1 = cur.fetchall()
    cur.execute("select kg.基金经理表.经理姓名 from kg.基金经理表")
    output2 = cur.fetchall()

    f1_path = '/data/DuSQL/fund_name.txt'
    f1 = open(f1_path, mode='w', encoding="utf-8")
    f1.write('[')
    for item in output:
        f1.write(str(item[0])+ ',')
    for item in output1:
        f1.write(str(item[0])+ ',' )
    for item in output2:
        f1.write(str(item[0])+ ',' )
    f1.write(']')
    f1.close()
