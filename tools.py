#!python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen
from bs4 import BeautifulSoup

def read_str_from_url(url):
    content = urlopen(url).read()
    
    soup = BeautifulSoup(content, "html.parser")
    body = soup.find('body')
    if body != None:
        soup = body

    s = soup.get_text('\n', True)
    s = s.replace('\n\r', '\n')
    s = s.replace('\r\n', '\n')
    for i in [5, 5, 4, 4, 4, 3, 3, 3, 3]:
        s = s.replace('\n'*i, '\n\n')

    s = s.replace('&nbsp;',' ')
    return s


def main():
    s = read_str_from_url('http://xs.dmzj.com/1122/3990/24478.shtml')
    with open('c.txt', 'w', encoding='utf-8') as f:
        f.write(s)


if __name__ == '__main__':
    main()
