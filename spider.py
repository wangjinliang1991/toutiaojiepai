import requests, json, re
from urllib.parse import urlencode
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from config import *
import pymongo
from hashlib import md5
import os
from multiprocessing import Pool
from json.decoder import JSONDecodeError


client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.04; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/68.0.3440.106 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Host': 'www.toutiao..com'
    }

def get_page_index(offset, keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': 3,
        'from': 'search_tab'
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    response = requests.get(url, headers=headers)
    try:
        if response.status_code==200:
            return response.text
        return None
    except RequestException:
        print("请求索引页错误")
        return None

def parse_page_index(html):
    try:
        data = json.loads(html)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                    yield item.get('article_url')
    except JSONDecodeError:
        pass

def get_page_detail(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code==200:
            return response.text
        return None
    except RequestException:
        print("请求详情页错误", url)
        return None

def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.title.string
    print(title)
    images_pattern = re.compile('gallery: JSON.parse("(.*?)";)', re.S)
    result = re.search(images_pattern, html)
    if result:
        data = json.loads(result.group(1))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for image in images:
                download_image(image)
            return {
                'title': title,
                'url': url,
                'images': images
            }

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储到MongoDB成功', result)
        return True
    return False

def download_image(url):
    print('正在下载', url)
    response = requests.get(url, headers=headers)
    try:
        if response.status_code==200:
            save_image(response.content)
        return None
    except RequestException:
        print("请求索图片出错", url)
        return None

def save_image(content):
    file_path = '{0}/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()
def main(offset):
    html = get_page_index(offset, KEYWORD)
    for url in parse_page_index(html):
        # print(url)
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html)
            if result:
                save_to_mongo(result)

if __name__=="__main__":
    groups = [x*20 for x in range(GROUP_START, GROUP_END+1)]
    pool = Pool()
    pool.map(main, groups)