# -*- coding: UTF-8 -*-
import pymysql
import config


class Query:
    def __init__(self):
        self.dbObj = pymysql.connect(
            host='127.0.0.1',
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
        sql = f"select name, idc, phone, address from hukou where name = '{keyword}'"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        return result

    def query_by_hukou(self, keyword, qtype):
        sql = f"select name, idc, phone, address from hukou where {qtype} = '{keyword}'"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        rlist = []
        dic = {}
        for item in result:
            dic['name'] = item[0]
            dic['idcard'] = item[1]
            dic['phone'] = item[2]
            dic['address'] = item[3]

            rlist.append(dic)
        return rlist

    def query_by_chezhu(self, keyword, qtype):
        sql = f"select name, idcard, phone, mail, address from chezhu where {qtype} = '{keyword}'"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        rlist = []
        dic = {}
        for item in result:
            dic['name'] = item[0]
            dic['idcard'] = item[1]
            dic['phone'] = item[2]
            dic['mail'] = item[3]
            dic['address'] = item[4]

            rlist.append(dic)

        return rlist

    def query_by_didi(self, keyword, qtype):
        sql = f"select name, phone, idcard from didi where {qtype} = '{keyword}'"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        rlist = []
        dic = {}
        for item in result:
            dic['name'] = item[0]
            dic['phone'] = item[1]
            dic['idcard'] = item[2]

            rlist.append(dic)

        return rlist

    def query_by_kf(self, keyword, qtype):
        sql = f"select name, idcard, address, phone from kf2000w where {qtype} = '{keyword}'"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        rlist = []
        dic = {}
        for item in result:
            dic['name'] = item[0]
            dic['idcard'] = item[1]
            dic['address'] = item[2]
            dic['phone'] = item[3]

            rlist.append(dic)

        return rlist

