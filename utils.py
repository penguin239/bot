# -*- coding: UTF-8 -*-
import config
import pymysql
import time
import re
import random


class Utils:
    def __init__(self):
        self.dbObj = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            passwd='root',
            db=config.telebot_database,
            autocommit=True
        )
        self.user_table = 'user'
        self.invited_table = 'invited_user'

    def insert_user(self, user_id):
        # 添加用户
        cursor = self.dbObj.cursor()
        invite_code = self.generate_invite_code()

        sql = f"insert into {self.user_table} values ('{user_id}', {config.new_user_score}, '', '{invite_code}', '')"
        cursor.execute(sql)
        cursor.close()

        return True

    def query_user_info(self, user_id):
        # 用户个人信息查询
        cursor = self.dbObj.cursor()
        sql = f"select user_id, score, last_sign_time, invite_code, invited_user from {self.user_table} where user_id = '{user_id}'"
        cursor.execute(sql)
        response = cursor.fetchone()

        if not response:
            return None

        invited_user = response[4]
        if not invited_user:
            invite_count = 0
        else:
            invited_user_list = str(invited_user).split(',')
            invite_count = len(invited_user_list)

        response = {
            'user_id': response[0],
            'score': response[1],
            'last_sign_time': response[2],
            'invite_code': response[3],
            'invite_count': invite_count,
            'invited_list': str(invited_user)
        }
        cursor.close()

        return response

    def sign(self, user_id):
        # 签到功能
        local_time = time.localtime()
        local_day = local_time.tm_mday
        current_time = self.get_current_time()

        if self.today_already_sign(user_id, local_day):
            cursor = self.dbObj.cursor()
            sql = f"update {self.user_table} set last_sign_time = '{current_time}' where user_id = '{user_id}'"
            cursor.execute(sql)
            cursor.close()

            return True
        return False

    def today_already_sign(self, user_id, current_day):
        # 判断用户今日是否签到
        result = self.query_user_info(user_id)
        last_sign_time = result['last_sign_time']
        if not last_sign_time:
            return True

        pattern = r'\d{4}-\d*-(\d*) \d*:\d*'
        last_sign_day = re.search(pattern, last_sign_time)
        last_sign_day = int(last_sign_day.groups()[0])

        if last_sign_day >= int(current_day):
            return False
        return True

    def add_score(self, user_id, score):
        # 为用户增加积分
        result = self.query_user_info(user_id)
        current_score = result['score']
        sql = f"update {self.user_table} set score = {current_score + score} where user_id = {user_id}"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        cursor.close()

        return True

    def generate_invite_code(self):
        # 生成邀请码
        strs = '0123456789abcdefghijklmnopqrstuvwxyz'
        code_list = random.choices(strs, k=8)
        invite_code = ''.join(code_list)

        if self.check_invite_code(invite_code):
            return ''.join(code_list)
        self.generate_invite_code()

    def check_invite_code(self, invite_code):
        sql = f"select invite_code from {self.user_table} where invite_code = '{invite_code}'"
        cursor = self.dbObj.cursor()
        result = cursor.execute(sql)
        cursor.close()

        return True if not result else False

    def prompt(self, tips, info_type='INFO'):
        # 自定义日志打印
        current_time = self.get_current_time()
        reply_str = f'{current_time} [{info_type}]：{tips}'

        print(reply_str)

    def get_current_time(self):
        # 获取当前时间
        local_time = time.localtime()
        current_time = '%d-%d-%d %d:%02d' % (
            local_time.tm_year, local_time.tm_mon, local_time.tm_mday, local_time.tm_hour, local_time.tm_min)

        return current_time

    def get_invite_user(self, invite_code):
        sql = f"select user_id from {self.user_table} where invite_code = '{invite_code}'"

        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()[0]
        cursor.close()

        return int(result)

    def invite_check(self, invite_code, sender):
        # 用户邀请
        invite_user = self.get_invite_user(invite_code)

        invite_user_info = self.query_user_info(invite_user)
        origin_invited = invite_user_info['invited_list']

        # 判断被邀请者是否已经在使用机器人了
        cursor = self.dbObj.cursor()
        sql = f"select invited_user from {self.invited_table} where invited_user = '{sender}'"
        result = cursor.execute(sql)
        cursor.close()

        if result:
            return None

        origin_invited_list = origin_invited.split(',')
        if str(sender) in origin_invited_list:
            return None

        # 判断被邀请用户是否为自己
        if sender == invite_user:
            return None

        # 邀请成功，添加到用户的已邀请名单中
        self.add_score(invite_user, config.invite_add_score)
        new_invited = origin_invited + f',{sender}'
        if not origin_invited:
            new_invited = sender
        sql = f"update {self.user_table} set invited_user = '{new_invited}' where user_id = '{invite_user}'"

        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        cursor.close()

        # 将被邀请的用户添加到invited_user中
        cursor = self.dbObj.cursor()
        sql = f"insert into {self.invited_table} values ('{sender}')"
        cursor.execute(sql)
        cursor.close()

        return int(invite_user)

    def reduce_score(self, sender, score):
        # 为指定用户减少积分
        user = self.query_user_info(sender)
        current_score = user['score']

        sql = f"update {self.user_table} set score = {current_score - score} where user_id = '{sender}'"
        cursor = self.dbObj.cursor()
        cursor.execute(sql)
        cursor.close()

        return True

    def check_score(self, sender):
        sender_residue_score = self.query_user_info(sender).get('score')

        return sender_residue_score > 0

