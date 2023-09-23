# -*- coding: UTF-8 -*-
import pymysql
import config



class Query:
    def __init__(self):
        self.dbObj = pymysql.connect(
            host='127.0.0.1',
            # host='botserver',
            port=3306,
            user='root',
            passwd='root',
            db=config.data_database,
            autocommit=True
        )

    def query_name(self, keyword):
        sql_injection_keyword = ['union', 'select', 'from', 'where', 'group', "'"]
        for item in sql_injection_keyword:
            if item in keyword:
                return ''
        sql = f"select distinct name, idc, phone, address from hukou where name = '{keyword}'"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        return result

    def query_by_hukou(self, keyword, qtype):
        sql = f"select distinct name, idcard, phone, address from hukou where {qtype} = '{keyword}'"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        rlist = []

        for item in result:
            dic = {'name': item[0], 'idcard': item[1], 'phone': item[2], 'address': item[3]}

            rlist.append(dic)
        return rlist

    def query_by_chezhu(self, keyword, qtype):
        sql = f"select distinct name, idcard, phone, mail, address from chezhu where {qtype} = '{keyword}'"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        rlist = []

        for item in result:
            dic = {'name': item[0], 'idcard': item[1], 'phone': item[2], 'mail': item[3], 'address': item[4]}

            rlist.append(dic)

        return rlist

    def query_by_didi(self, keyword, qtype):
        sql = f"select distinct name, phone, idcard from didi where {qtype} = '{keyword}'"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        rlist = []

        for item in result:
            dic = {'name': item[0], 'phone': item[1], 'idcard': item[2]}

            rlist.append(dic)

        return rlist

    def query_by_kf(self, keyword, qtype):
        sql = f"select distinct name, idcard, address, phone from kf2000w where {qtype} = '{keyword}'"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        rlist = []

        for item in result:
            dic = {'name': item[0], 'idcard': item[1], 'address': item[2], 'phone': item[3]}

            rlist.append(dic)

        return rlist

    def query_phone_by_shunfeng(self, keyword):
        sql = f"select distinct name, phone, sheng, shi, qu, address from shunfeng where phone = '{keyword}'"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        rlist = []
        for item in result:
            dic = {'name': item[0], 'phone': item[1], 'sheng': item[2], 'shi': item[3], 'qu': item[4],
                   'address': item[5]}

            rlist.append(dic)
        return rlist

    def query_by_bilibili(self, keyword, qtype):
        sql = f"select distinct uid, phone from bilibili where {qtype} = '{keyword}'"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        rlist = []
        for item in result:
            dic = {'uid': item[0], 'phone': item[1]}

            rlist.append(dic)
        return rlist

    def query_qq(self, keyword, qtype):
        sql = f"select distinct username, mobile from 8eqq where {qtype} = '{keyword}'"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        rlist = []
        for item in result:
            dic = {'qq': item[0], 'phone': item[1]}

            rlist.append(dic)
        return rlist

    def query_lol(self, keyword):
        sql = f"select distinct uin, name, area from lol_bind where name = '{keyword}'"

        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        rlist = []
        for item in result:
            dic = {'qq': item[0], 'lol_name': item[1], 'area': item[2]}

            rlist.append(dic)
        return rlist

    def query_by_3ys(self, keyword, qtype):
        sql = f"select distinct name, idcard, phone from 3ys where {qtype} = '{keyword}'"

        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        rlist = []
        for item in result:
            dic = {'name': item[0], 'idcard': item[1], 'phone': item[2]}

            rlist.append(dic)
        return rlist

    def query_idcard_by_nameia(self, keyword):
        sql = f"select distinct name, idcard, address from nameia where idcard = '{keyword}'"

        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        rlist = []
        for item in result:
            dic = {'name': item[0], 'idcard': item[1], 'address': item[2]}

            rlist.append(dic)
        return rlist

    def query_by_zj1100w(self, keyword, qtype):
        sql = f"select distinct * from zj1100w where {qtype} = '{keyword}'"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        rlist = []
        for item in result:
            dic = {
                'name': item[0],
                'idcard': item[1],
                'address1': item[2],
                'parent': item[3],
                'phone': item[4],
                'address2': item[5],
                'grade': item[6],
                'school': item[7]
            }

            rlist.append(dic)
        return rlist
