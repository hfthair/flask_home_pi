'''this file is highly inspired by @tychxn:
    https://github.com/tychxn/baidu-wangpan-parse
    4e8e1177f297712eb51b2d960d58d39d9b129e9c'''
import time
import re
import json
import random
import requests
import urllib.parse as parse

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7',
    'Host': 'pan.baidu.com',
    'Origin': 'https://pan.baidu.com',
}

session = requests.Session()


def verifyPassword(src, password):  # verify file password
    match = re.match(r'http[s]?://pan.baidu.com/s/1(.*)', src)
    if not match:
        print('Link match error!')
        return False

    url = 'https://pan.baidu.com/share/verify'
    surl = match.group(1)
    params = {
        'surl': surl,
        't': '%d' % (time.time() * 1000),
        'bdstoken': 'null',
        'channel': 'chunlei',
        'clienttype': '0',
        'web': '1',
        'app_id': '250528',
    }
    data = {
        'pwd': password,
        'vcode': '',
        'vcode_str': '',
    }
    headers['Referer'] = src
    response = session.post(url=url, data=data, params=params, headers=headers)
    js = json.loads(response.text)
    return True if js['errno'] == 0 else False

def get_params(src):
    try:
        response = session.get(src, headers=headers)
        response.encoding = 'utf8'
        m = re.search('\"sign\":\"(.+?)\"', response.text)
        sign = m.group(1)
        m = re.search('\"timestamp\":(.+?),\"', response.text)
        timestamp = m.group(1)
        m = re.search('\"shareid\":(.+?),\"', response.text)
        primary_id = m.group(1)
        m = re.search('\"uk\":(.+?),\"', response.text)
        uk = m.group(1)
        m = re.search('\"fs_id\":(.+?),\"', response.text)
        fid_list = '[' + m.group(1) + ']'
        return sign, timestamp, primary_id, uk, fid_list
    except:
        return None

def create_form(sign, timestamp, primary_id, uk, fid_list):
    url = 'http://pan.baidu.com/api/sharedownload'
    payload = {
        'sign': sign,
        'timestamp': timestamp,
        'bdstoken': 'null',
        'channel': 'chunlei',
        'clienttype': '0',
        'web': '1',
        'app_id': '250528',
    }
    data = {
        'encrypt': '0',
        'product': 'share',
        'type': 'nolimit',
        'uk': uk,
        'primaryid': primary_id,
        'fid_list': fid_list,
    }

    return url, payload, data

def get_code_and_img():
    print('Start downloading the verification code...')

    url = "http://pan.baidu.com/api/getvcode"
    payload = {
        'prod': 'pan',
        't': random.random(),
        'bdstoken': 'null',
        'channel': 'chunlei',
        'clienttype': '0',
        'web': '1',
        'app_id': '250528',
    }
    response = session.get(url=url, params=payload, headers=headers)
    js = json.loads(response.text)
    vcode = js['vcode']

    response = session.get(
        url="http://pan.baidu.com/genimage?%s" % vcode,
        headers=headers
    )
    return vcode, response

def get_true_link(src, password, is_folder):
    session.get(url='http://pan.baidu.com', headers=headers)
    if password:
        res = verifyPassword(src, password)
        if not res:
            return None
    r = get_params(src)
    if not r:
        return None
    sign, timestamp, primary_id, uk, fid_list = r
    url, param, data = create_form(sign, timestamp, primary_id, uk, fid_list)

    if is_folder:
        data['type'] = 'batch'

    if password:
        data['extra'] = '{"sekey":"' + parse.unquote(session.cookies['BDCLND']) + '"}'

    while True:
        response = session.post(url=url, params=param, data=data, headers=headers)
        js = json.loads(response.text)

        if js['errno'] == 0:
            return js['dlink'] if is_folder else js["list"][0]['dlink']
        elif js['errno'] == -20: # need verify code
            vcode, img_response = get_code_and_img()

            import os
            with open('v.jpg', 'wb') as f:
                for chunk in img_response.iter_content(chunk_size=1024):
                    f.write(chunk)
            os.system('start v.jpg')
            vcodei = input('Please enter the verification code (return change):')

            data['vcode_input'] = vcodei
            data['vcode_str'] = vcode
        else:
            print('Unknown error, the error code is as follows:')
            print(js)
            return None

r = get_true_link('https://pan.baidu.com/s/1c2JEhhu', 'fxid', False)
print(r)
