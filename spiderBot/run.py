from telethon import TelegramClient, events
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image
from io import BytesIO

import requests
import asyncio
import models
import conf
import re
import json

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


def node_spider():
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
\ud83d\udfe2 **notice** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

\ud83d\udd17源链接: {newUrl}

· 标题: {r_title}
· 原文长度: {len(result_list)}

· 实际长度: {len(node_list) - 1}
· 文章链接: {r_url}
        '''
        reply_channel_msg = f'''
\ud83d\udfe2 **每日免费节点更新** {datetime.now().strftime('%Y-%m-%d')}

\ud83c\udf88 **{r_title}**

\ud83c\udf97长度: {len(node_list) - 1}
\ud83d\udd17文章链接: {r_url}

标签：#节点 #免费节点
        '''
        # asyncio.run_coroutine_threadsafe(client.send_message(conf.administrators, reply_msg, link_preview=False), loop)
        asyncio.run_coroutine_threadsafe(client.send_message(conf.channel, reply_channel_msg, link_preview=False), loop)

        with open('run.log', 'a', encoding='utf8') as f:
            f.write(log_formatter(f'{newUrl}', 'SAVE'))
    except Exception as error:
        asyncio.run_coroutine_threadsafe(client.send_message(
            conf.administrators,
            f'''
\ud83d\udd34 !! **error**

报错来源：节点爬虫
报错时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
报错内容：
{error}
            '''
        ), loop)
    finally:
        models.session.close()


def webp2data(webp_bytes):
    image = Image.open(BytesIO(webp_bytes))
    image_buffer = BytesIO()
    image.save(image_buffer, format='PNG')
    image_data = image_buffer.getvalue()
    image_buffer.close()

    return image_data


def it_home_spider():
    try:
        url = 'https://www.ithome.com/blog/'
        response = requests.get(url, headers=conf.headers)
        soup = BeautifulSoup(response.text, 'lxml')

        ul = soup.find('ul', class_='bl')

        for item in ul.find_all('div', class_='c'):
            tags = ''
            article_time = item['data-ot']
            a_item = item.find_next('a', class_='title')
            title = a_item.text
            item_url = a_item['href']
            if 'lapin' in item_url:
                continue
            if models.session.query(models.NodeConf).filter(models.NodeConf.url == item_url).first():
                break

            newNodeUrl = models.NodeConf(url=item_url)
            models.session.add(newNodeUrl)
            models.session.commit()

            intro = item.find_next('div', class_='m').text.strip()
            tag = item.find_next('div', class_='tags').find_all('a')
            for t in tag:
                tags += f'#{t.text.replace(" ", "")} '

            img_url = item.find_previous_sibling('a', class_='img').find('img')['data-original']
            jpg_url = img_url.split('?')[0]

            reply_channel_msg = f'''
**{title}**

发布时间：{article_time}
原文链接：{item_url}

{intro}

标签：{tags}
            '''

            asyncio.run_coroutine_threadsafe(
                # file参数可接受一个外部URL
                client.send_message(conf.channel, reply_channel_msg, file=jpg_url,
                                    link_preview=False), loop)
    except Exception as error:
        asyncio.run_coroutine_threadsafe(client.send_message(
            conf.administrators,
            f'''
\ud83d\udd34 !! **error**

报错来源：IT之家爬虫
报错时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
报错内容：
{error}
            '''
        ), loop)
    finally:
        models.session.close()


if __name__ == '__main__':
    client.start(bot_token=conf.bot_token)
    print('Bot started!')

    loop = asyncio.get_event_loop()
    scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(node_spider, 'interval', hours=1)
    scheduler.add_job(it_home_spider, 'interval', seconds=30)
    node_spider()
    it_home_spider()
    scheduler.start()

    client.run_until_disconnected()
