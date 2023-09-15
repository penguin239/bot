from telethon import TelegramClient, events
from telethon import Button
from query import Query
from utils import Utils

import os
import time
import asyncio
import socks
import config

first_start_time = time.time()

api_id = config.api_id
api_hash = config.api_hash
bot_token = config.bot_token

utils = Utils()
query = Query()
client = TelegramClient('penguin', api_id, api_hash, proxy=(socks.SOCKS5, '127.0.0.1', 7891)).start(bot_token=bot_token)

connected_time = time.time()
utils.prompt(f'机器人启动成功，在{round(connected_time - first_start_time, 2)}s内')

if not os.path.exists('./reply_data'):
    os.mkdir('./reply_data')

custom_buttons = [
    [
        Button.url('加入我们的频道', config.channel_url),
        Button.url('联系作者', config.consultant_url)
    ],
    [
        Button.url('社工库使用教程', config.help_telegraph_url)
    ]
]
telegraph_button = [
    [
        Button.url('社工库使用教程', config.help_telegraph_url)
    ]
]


# async def ismember(sender):
#     entity = await client.get_entity(config.channel_name)
#     users = await client.get_participants(entity)
#
#     for user in users:
#         if user.id == sender:
#             return True
#     return False


@client.on(events.NewMessage(pattern='.*'))
async def log_save(event):
    current_time = utils.get_current_time()
    sender = await event.get_sender()

    sender_id = sender.id
    name = f'{sender.first_name} {sender.last_name}'
    if not (sender.first_name and sender.last_name):
        name = sender.last_name if sender.last_name else sender.first_name

    username = f'@{sender.username}'
    phone = sender.phone
    lang_code = sender.lang_code

    message = event.message

    result = f'{current_time} [INFO] User({sender_id}, {name}, {username}, {phone}, {lang_code}, message={message.message})'

    localtime = time.localtime()
    current_time_to_log = f'{localtime.tm_year}-{localtime.tm_mon}-{localtime.tm_mday}'

    if not os.path.exists('logs'):
        os.mkdir('logs')
    with open(f'logs/{current_time_to_log}.log', 'a', encoding='utf8') as logfile:
        logfile.write(result)
        logfile.write('\n')


@client.on(events.NewMessage(pattern='(?i)/start'))
async def start_bot(event):
    sender = event.sender_id
    user_info = await event.get_sender()

    result = utils.query_user_info(sender)
    if not result:
        utils.insert_user(sender)

    user_name = f'{user_info.first_name} {user_info.last_name}'
    if not user_info.first_name:
        user_name = f'{user_info.last_name}'
    elif not user_info.last_name:
        user_name = f'{user_info.first_name}'

    # 使用者用户名 @test
    # account = user_info.username

    reply_str = f'''
\uD83C\uDF89您好 {user_name}，欢迎使用penguin社工库机器人！

✍请发送任意关键词查询

- 机器人使用一次仅消耗1积分，未查询到不会扣除积分
- 邀请一名奖励5积分，每日签到奖励3积分，新用户赠送10积分
- 每人都有一次被邀请的机会，即使你正在使用它！

\uD83D\uDD28常用指令：
     /start   开始使用
     /sign    每日签到
     /info    账户信息
     /help    帮助

\uD83D\uDD14声明：搭建此机器人主要目的为检验学习成果以及提高公民隐私保护意识，不以此牟利，机器人完全免费，不会开放任何充值接口。
'''

    await client.send_message(sender, reply_str, buttons=custom_buttons)


@client.on(events.NewMessage(pattern='(?i)/start (.*)?'))
async def via_invite_start(event):
    sender = event.sender_id
    invite_code = event.pattern_match.groups()[0]
    invite_user = utils.invite_check(invite_code, sender)

    if invite_user:
        reply_str = f'''
\uD83D\uDD14用户{sender}已经接受了你的邀请！

\uD83C\uDF81奖励积分：{config.invite_add_score}
'''
        await client.send_message(invite_user, reply_str)


@client.on(events.NewMessage(pattern='(?i)/info'))
async def sender_info(event):
    # 获取发送者永久id
    sender = event.sender_id

    result = utils.query_user_info(sender)
    last_sign_time = result['last_sign_time']
    if not last_sign_time:
        last_sign_time = '从未签到！'
    reply_str = f'''
\uD83D\uDC64您的帐号：{result['user_id']}

⭕剩余积分：{result['score']}
\uD83D\uDD54上次签到时间：{last_sign_time}

\uD83D\uDC9E邀请人数：{result['invite_count']}
\uD83C\uDFA8您的邀请码：{result['invite_code']}
\uD83C\uDF88您的邀请链接：{config.bot_url}?start={result['invite_code']}
'''
    await client.send_message(sender, reply_str)


@client.on(events.NewMessage(pattern='(?i)/sign'))
async def sign(event):
    sender = event.sender_id

    if utils.sign(sender):
        reply_str = f'''
✅签到成功！

\uD83C\uDF81奖励积分：{config.sign_add_score}
'''
        # 为签到的用户增加积分
        utils.add_score(sender, config.sign_add_score)
        await client.send_message(sender, reply_str)
    else:
        reply_str = '''
        ⚠️你今天已经签到过了！
        '''
        await client.send_message(sender, reply_str)


@client.on(events.NewMessage(pattern='(?i)/idcard (\d{18}|\d{17}X)?'))
async def query_idcard(event):
    sender = event.sender_id
    message_id = event.message.id

    if not utils.check_score(sender):
        reply_str = f'''
\uD83D\uDC4B您的积分不足！

__每次查询仅需{config.query_per_score}积分__
'''
        await event.reply(reply_str)
        return
    keyword = event.pattern_match.groups()[0]
    if not keyword:
        await client.send_message(sender, '⚠️请输入正确的身份证号，参考使用说明', buttons=telegraph_button,
                                  reply_to=message_id)
        return

    reply_str = query_all(sender, keyword, qtype='idcard')
    await client.send_message(sender, reply_str, reply_to=message_id)


@client.on(events.NewMessage(pattern='(?i)/help'))
async def help_and_support(event):
    reply_str = '''
\uD83D\uDC96#帮助

本机器人可查询到：身份户籍、开房记录、电话机主、学籍信息、常用密码、QQ/手机/微博/LOL绑定，以及身份证，户籍地址等公开信息。

常用查询关键词：QQ、手机号、身份证号、用户名、邮箱、姓名
__详细使用说明见下方按钮链接__
'''
    await client.send_message(event.sender_id, reply_str, buttons=telegraph_button)


@client.on(events.NewMessage(pattern='(?i)/phone (\d{11})?'))
async def query_phone(event):
    sender = event.sender_id
    message_id = event.message.id

    if not utils.check_score(sender):
        reply_str = f'''
    \uD83D\uDC4B您的积分不足！

    __每次查询仅需{config.query_per_score}积分__
    '''
        await event.reply(reply_str)
        return
    keyword = event.pattern_match.groups()[0]

    if not keyword:
        await client.send_message(sender, '⚠️请输入正确的手机号，参考使用说明', buttons=telegraph_button,
                                  reply_to=message_id)
        return

    reply_str = query_all(sender, keyword, qtype='phone')
    await client.send_message(sender, reply_str, reply_to=message_id)


@client.on(events.NewMessage(pattern='(?i)/bili (\d*)'))
def query_uid(event):
    sender = event.get_sender
    keyword = event.pattern_match.groups()[0]

    result = query.query_by_bilibili(keyword, 'uid')
    result_len = len(result)

    if result_len:
        utils.reduce_score(sender, config.query_per_score)
        return format_reply(result_len, result)
    return '''
\uD83D\uDE45机器人暂未收录该数据

✨机器人未查询到结果：积分未扣除
'''


def query_all(sender, keyword, qtype):
    result = []
    a = query.query_by_chezhu(keyword, qtype)
    b = query.query_by_didi(keyword, qtype)
    c = query.query_by_hukou(keyword, qtype)
    d = query.query_by_kf(keyword, qtype)

    [result.append(item) for item in a if a]
    [result.append(item) for item in b if b]
    [result.append(item) for item in c if c]
    [result.append(item) for item in d if d]

    if qtype == 'phone':
        # 库中只有手机号，没有身份证号
        e = query.query_phone_by_shunfeng(keyword)
        f = query.query_by_bilibili(keyword, 'phone')
        [result.append(item) for item in e if e]
        [result.append(item) for item in f if f]
    result_count = len(result)

    if result_count:
        # 查询到内容，减去积分
        utils.reduce_score(sender, config.query_per_score)
        return format_reply(result_count, result)
    return '''
\uD83D\uDE45机器人暂未收录该数据

✨机器人未查询到结果：积分未扣除
'''


def format_reply(count, result):
    reply_str = f'''
查询到{count}个结果
机器人查询到结果：扣除{config.query_per_score}积分\n
'''
    for item in result:
        name = item.get('name', None)
        reply_str += f'姓名：{name}\n' if name else ''

        phone = item.get('phone', None)
        reply_str += f'手机号：{phone}\n' if phone else ''

        idcard = item.get('idcard', None)
        reply_str += f'身份证号：{idcard}\n' if idcard else ''

        sheng = item.get('sheng', None)
        reply_str += f'省：{sheng}\n' if sheng else ''

        shi = item.get('shi', None)
        reply_str += f'市：{shi}\n' if shi else ''

        qu = item.get('qu', None)
        reply_str += f'区：{qu}\n' if qu else ''

        address = item.get('address', None)
        reply_str += f'地址：{address}\n' if address else ''
        reply_str += '\n'

        uid = item.get('uid', None)
        reply_str += f'Bilibili Uid：{uid}\n' if uid else ''
        reply_str += '\n'

    return reply_str


if __name__ == '__main__':
    client.start()
    client.run_until_disconnected()
