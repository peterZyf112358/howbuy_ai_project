import unittest
from time_self import recognize_date as rd
import datetime

class test_my_function(unittest.TestCase):
    #常规日期
    def test_1(self):
        self.assertEqual(rd('1997-03-04'), ['1997-03-04'])
    def test2(self):
        self.assertEqual(rd('1997/03/04'), ['1997-03-04'])
    def test3(self):
        self.assertEqual(rd('10JAN1997'), ['1997-01-10'])
    def test4(self):
        self.assertEqual(rd('JAN111997'), ['1997-01-11'])
    def test5(self):
        self.assertEqual(rd('1997-10'), ['1997-10'])
    def test6(self):
        self.assertEqual(rd('1997/10'), ['1997-10'])
    def test7(self):
        self.assertEqual(rd('4月30号2023'), ['2023-04-30'])
    def test8(self):
        self.assertEqual(rd('2023年4月9日'), ['2023-04-09'])
    def test8(self):
        self.assertEqual(rd('2023年4月'), ['2023-04'])

    def test9(self):
        self.assertEqual(rd('今年'), [str(datetime.date.today().year)])

    def test10(self):
        self.assertEqual(rd('今年8月'), [str(datetime.date.today().year)+'-08'])
    def test11(self):
        self.assertEqual(rd('今年11月'), [str(datetime.date.today().year)+'-11'])
    def test12(self):
        self.assertEqual(rd('今年11月10号'), [str(datetime.date.today().year)+'-11-10'])

    def test10(self):
        self.assertEqual(rd('去年'), [str(datetime.date.today().year-1)])
    def test14(self):
        self.assertEqual(rd('上年8月'), [str(datetime.date.today().year-1)+'-08'])
    def test15(self):
        self.assertEqual(rd('去年11月'), [str(datetime.date.today().year-1)+'-11'])
    def test16(self):
        self.assertEqual(rd('上年11月10号'), [str(datetime.date.today().year-1)+'-11-10'])
    def test17(self):
        self.assertEqual(rd('20年前'), [str(datetime.date.today().year-20)])
    def test18(self):
        self.assertEqual(rd('20年前4月'), [str(datetime.date.today().year-20)+'-04'])
    def test19(self):
        self.assertEqual(rd('2020年初'), ['2020-01-01'])
    def test20(self):
        self.assertEqual(rd('2020年年末'), ['2020-12-31'])
    def test21(self):
        self.assertEqual(rd('前年'), [str(datetime.date.today().year-2)])
    def test22(self):
        self.assertEqual(rd('前年8月'), [str(datetime.date.today().year-2)+'-08'])
    def test23(self):
        self.assertEqual(rd('前年11月'), [str(datetime.date.today().year-2)+'-11'])
    def test24(self):
        self.assertEqual(rd('前年11月10号'), [str(datetime.date.today().year-2)+'-11-10'])
    def test25(self):
        self.assertEqual(rd('2023年上半年'), ['2023-01-01', '2023-06-30'])
    def test26(self):
        self.assertEqual(rd('2023下半年'), ['2023-07-01', '2023-12-31'])
    def test27(self):
        self.assertEqual(rd('2023年1季度'), ['2023-01-01', '2023-03-31'])
    def test28(self):
        self.assertEqual(rd('2002第二季度'), ['2002-04-01', '2002-06-30'])
    def test29(self):
        self.assertEqual(rd('1998三季度'), ['1998-07-01', '1998-09-30'])
    def test30(self):
        self.assertEqual(rd('2021年第4季度'), ['2021-10-01', '2021-12-31'])

if __name__ == "__main__":
    unittest.main()