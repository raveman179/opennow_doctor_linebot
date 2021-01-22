#coding: utf-8

# http://www.yasuokaiin.jp/
# から、
# 通常休診日、 臨時休診日
# をピックアップして、
# 今日は該当するか標準出力

import datetime
import locale
import re
from collections import defaultdict
import jpholiday
import requests
import time
from bs4 import BeautifulSoup

target_url = 'http://www.yasuokaiin.jp/index.html'

#requestsを使って、webから取得
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}

time.sleep(2)
r = requests.get(target_url, headers = headers)                                                 

if r.status_code != 200:
    print('取得できませんでした。')

#今日の日付を取得
dt_now = datetime.datetime.now()
dt = dt_now.strftime('%Y,%-m,%-d,%p,%I,%M,%A').split(',')

#今日の日付が祝日か確認する
holiday = jpholiday.is_holiday(dt_now.date())

#BeautifulSoupオブジェクトの作成
html = r.content
soup = BeautifulSoup(html, 'html.parser')

#改行コードを消す処理
soup = [tag.extract() for tag in soup(string='\n')]      

def dtdd_dict(elements):
    """
    defaultdictを使ってdtをキー、ddを値にする関数
    """
    data = defaultdict(list)
    for element in elements.find_all(['dt','dd']):
        if element.name =='dt':
            key = element.text.rstrip('\u3000')
        if key and element.name == 'dd':
            data[key].append(element.text)
    return data

def dayofweek(day):
    """
    日本語の曜日をdatetimeのweekday表記にして返す
    '月':0, '火':1, '水':2, '木':3, '金':4, '土':5, '日':6
    祝日：'holiday'　年末年始：'newyear'
    """
    week = {'月':0, '火':1, '水':2, '木':3, '金':4, '土':5, '日':6}
    if day == '祝日':
        tmpday = 'holiday'
    elif day == '年末年始':
        tmpday = 'newyear'
    else:
        tmp = day[0]
        tmpday = week[tmp]
    return tmpday

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーここからスクレイピングの処理

# todo:休診’、’休診日’と入っているdivを取得する処理


# todo:ページの中に”年末年始”が入っていた場合、問答無用で12/29〜1/3は休診日にする処理　→他のページでも流用して使う





# todo:休診日の表をリストに変換する処理


c_body = soup.find_all('div', id="bk34649350")

c_body_td = c_body[0].find_all('td')

# todo:cbodytdをループで回して、text要素に○があればリストに１を追加する
# 　 　○がなければ0を追加する


print(c_body_td)


#臨時休診日を”お知らせ”から取得する処理
#余分な文章を削除して、年度と本文だけにする
# info_element = soup.find_all('div', class_='info')

# print("やすおか小児科医院 今やってる？クローラー (旧版)\n\n今日の日付は" + dt_now.strftime("%Y年%-m月%-d日、%p%I時%M分 %Aです。"))

# treat = absence_day(dt)
# if treat['status'] not in ['診療中', '診療時間外']:
#     print('本日は'+ treat['status'] + 'です。')
#     if treat['endingtime'] != ':':
#         print('診療時間は' + treat['endingtime'] + 'までです。')
# else:
#     print('只今の時間は'+ treat['status'] + 'です。診療時間は' + treat['endingtime'] + 'までです。')

# print(data)
# print(in_text)