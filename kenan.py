# Author : ZhangTong
import requests
import re
import json
from urllib.parse import urlencode


def structure_urls():
    '''
    构建请求地址
    :return: 返回地址
    '''
    urls = []
    base_url = 'https://s.video.qq.com/get_playsource?id=53q0eh78q97e4d1&'
    for i in range(1,1000,100):
        params = {
            'plat': 2,
            'type': 4,
            'data_type': 2,
            'video_type': 3,
            'plname': 'qq',
            'range': '%d-%d' % (i, i+99),
            'otype': 'json',
            'uid': '890b4bd6-e89d-47a9-acef-00a7d964ac27',
            # 'callback': '_jsonp_17_077c',
            # '_t': 1545627048649,
        }
        url = base_url + urlencode(params)
        urls.append(url)
    return urls

def download(url):
    '''
    发送请求
    :param url: 请求地址
    :return: 响应内容
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response.encoding = response.apparent_encoding
            if ('getkey' or 'getinfo') in url:
                return response.content
            return response.text
    except:
        pass


def parse(html):
    '''
    解析播放列表，获得所有剧情
    :param html: 响应内容
    :return: 播放链接和剧情名称
    '''
    dct = {}
    text = re.search('"videoPlayList":(.*?)},"error"', html, re.S)
    text = text.group(1)
    text = json.loads(text)
    for item in text:
        dct['playUrl'] = item['playUrl']
        dct['title'] = item['title']
        dct['vid'] = item['id']
        # episode_number = item['episode_number']
        # pic = item['pic']
        yield dct

def get_info(vid):
    for definition in ('shd', 'hd', 'sd'):
        params = {
            'isHLS': False,
            'charge': 0,
            'vid': vid,
            'defn': definition,
            'otype': 'json',
            'platform': 10901,
            'sdtfrom': 'v1010',
            'host': 'v.qq.com',
            'fhdswitch': 0,
            'show1080p': 1,
        }
        base_url = 'http://h5vv.video.qq.com/getinfo?'
        get_info_url = base_url + urlencode(params)
        content = download(get_info_url)
        data = json.loads(content[len('QZOutputJson='):-1])
        url_prefix = data['vl']['vi'][0]['ul']['ui'][0]['url']
        for stream in data['fl']['fi']:
            if stream['name'] != definition:
                continue
            stream_id = stream['id']
            urls = []
            for d in data['vl']['vi'][0]['cl']['ci']:
                keyid = d['keyid']
                filename = keyid.replace('.10', '.p') + '.mp4'
                get_key(vid, url_prefix, stream_id, urls, filename)
            print('stream', stream['name'])
            for url in urls:
                print(url)


def get_key(vid, url_prefix, stream_id, urls, filename):
    params = {
        'otype': 'json',
        'vid': vid,
        'format': stream_id,
        'filename': filename,
        'platform': 10901,
        'vt': 217,
        'charge': 0
    }
    base_url = 'http://h5vv.video.qq.com/getkey?'
    get_key_url = base_url + urlencode(params)
    # print(get_key_url)
    content = download(get_key_url)
    data = json.loads(content[len('QZOutputJson='):-1])
    url = '%s/%s?sdtfrom=v1010&vkey=%s' % (url_prefix, filename, data['key'])
    urls.append(url)

def save():
    pass

def main():
    urls = structure_urls()
    for url in urls:
        text = download(url)
        dct = parse(text)
        for i in dct:
            print(i['playUrl'], i['title'], i['vid'])
            get_info(i['vid'])

if __name__ == '__main__':
    main()