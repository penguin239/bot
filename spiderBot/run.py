from telethon import TelegramClient, events
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from datetime import datetime

import requests
import asyncio
import models
import conf
import re

if conf.proxy_on:
    client = TelegramClient('session', conf.api_id, conf.api_hash, proxy=conf.proxy)
else:
    client = TelegramClient('session', conf.api_id, conf.api_hash)


def post_article(title, content):
    param = {
        'access_token': conf.j_data['access_token'],
        'title': title,
        'author_name': conf.j_data['author_name'],
        'author_url': conf.j_data['author_url'],
        'content': content,
        'return_content': True
    }
    response = requests.get('https://api.telegra.ph/createPage', params=param, proxies=conf.proxies)

    if response.status_code == 200:
        response = response.json()

    if response['ok']:
        return response['result']['title'], response['result']['url']
    return False


def ox2dec(ox: str):
    return int(ox, 16)


def decode_email(to_decode: str):
    decode_ = []
    key = ox2dec(to_decode[:2])
    for i in range(2, len(to_decode), 2):
        to_decode_i = ox2dec(to_decode[i:i + 2])
        decode_i = to_decode_i ^ key
        decode_.append(chr(decode_i))
    return "".join(decode_)


def log_formatter(log_content, level):
    return f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]-[{level}]：{log_content}\n'


def spider():
    try:
        response = requests.get(conf.url, headers=conf.headers, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')

        newUrl = soup.find('h3', class_='title').find_next('a')['href']
        if models.session.query(models.NodeConf).filter(models.NodeConf.url == newUrl).first():
            with open('run.log', 'a', encoding='utf8') as f:
                f.write(log_formatter(f'{newUrl}', 'PASS'))
            return
        newNodeUrl = models.NodeConf(url=newUrl)
        models.session.add(newNodeUrl)
        models.session.commit()

        detail_page = requests.get(newUrl, headers=conf.headers, timeout=10)
        soup = BeautifulSoup(detail_page.text, 'lxml')
        blockquote = soup.find('blockquote')
        result_list = re.findall('(trojan://.*?(?:<br/>|</p>))', str(blockquote))

        node_list = ['{"tag":"p","children":["关注我们的频道 @penguinSGK 每天更新节点，分享技术。"]}']
        for item in result_list:
            item_str = str(item).replace('<br/>', '').replace('</p>', '')
            protected_str = decode_email(re.findall('data-cfemail="(.*?)"', item_str)[0])
            result = re.sub('<a.*?>.*?</a>', protected_str, item_str, flags=re.IGNORECASE)
            node_list.append('{"tag":"p","children":["' + result + '"]}')
            if len(node_list) > 10:
                break

        content = f'[{",".join(node_list)}]'
        title = f'{datetime.now().strftime("%Y-%m-%d")}-trojan节点'
        r_title, r_url = post_article(title, content)
        reply_msg = f'''
\ud83d\udfe2 !! **notice** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

\ud83d\udd17源链接: {newUrl}

· 标题: {r_title}
· 原文长度: {len(result_list)}

· 实际长度: {len(node_list) - 1}
· 文章链接: {r_url}
        '''
        reply_channel_msg = f'''
\ud83d\udfe2 !! **notice** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

· 标题: {r_title}
· 长度: {len(node_list) - 1}
· 文章链接: {r_url}
        '''
        asyncio.run_coroutine_threadsafe(client.send_message(conf.administrators, reply_msg, link_preview=False), loop)
        asyncio.run_coroutine_threadsafe(client.send_message(conf.channel, reply_channel_msg, link_preview=False), loop)

        with open('run.log', 'a', encoding='utf8') as f:
            f.write(log_formatter(f'{newUrl}', 'SAVE'))
    except Exception as error:
        asyncio.run_coroutine_threadsafe(client.send_message(
            conf.administrators,
            f'\ud83d\udd34 !! **error**\n{str(error)}'
        ), loop)
    finally:
        models.session.close()


if __name__ == '__main__':
    client.start(bot_token=conf.bot_token)
    print('Bot started!')

    loop = asyncio.get_event_loop()
    scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(spider, 'interval', seconds=30)
    spider()
    scheduler.start()

    client.run_until_disconnected()
