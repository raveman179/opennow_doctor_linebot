# coding: utf-8

import requests
from bs4 import BeautifulSoup

# r = requests.get("http://www.yasuokaiin.jp/index.html")
# soup = BeautifulSoup(r.content, 'html.parser')
# # aタグの取得
# print(soup.get("a"))
# # 整形後のhtml表示
# print(soup.prettify())


# https://naruport.com/blog/2019/7/13/how-to-use-of-beautiful-soup-4/ より

markup = '''
    <div class="box">
        <p>One</p>
        <p>Two</p>
    </div>
'''
soup = BeautifulSoup(markup, 'html.parser')

# CSSセレクタで要素を得る
# 結果はlistで返ってくる
tags = soup.select('.box > p')

print(type(tags))
# <class 'list'>

print(tags)
# [<p>One</p>, <p>Two</p>]

for tag in tags:
    print(type(tag))
    # <class 'bs4.element.Tag'>

print(tags[1].text)
# One