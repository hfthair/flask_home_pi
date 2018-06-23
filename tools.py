#!python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

black_list = ('加入书架', '小说网', '加入书签', '投票推荐', '上一页', \
            '下一页', '错误举报', '上一章', '下一章')

def html2text(html):
    for script in html(["script", "style"]):
        script.extract()
    for br in html.find_all('br'):
        br.replace_with('\n' + br.text)
    text = html.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # truncate with blacklist
    def test(line):
        if len(line) > 30:
            return True
        for k in black_list:
            if k in line:
                return False
        return True
    chunks = filter(test, chunks)
    return '\n\n'.join(chunk for chunk in chunks if chunk)

def read_content_from_url(url):
    content = requests.get(url, timeout=1.5)

    soup = BeautifulSoup(content.content, 'html.parser')
    body = soup.find('body')
    if body != None:
        soup = body

    s = html2text(soup)
    return s

if __name__ == '__main__':
    u = "https://m.qidian.com/book/1011979931/0"
    s = read_content_from_url(u)
    print(s)
    # with open('c.txt', 'w', encoding='utf8') as f:
    #     f.write(s)
