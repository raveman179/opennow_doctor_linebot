"""#coding: utf-8"""

# http://kidsallergycl.jp/
# から、
# 休診日、診療時間変更
# をピックアップして、
# 今日は該当するか標準出力

import sys
import datetime
import requests
from bs4 import BeautifulSoup

target_url = 'http://kidsallergycl.jp/'
r = requests.get(target_url)                                                #requestsを使って、webから取得

if r.status_code != 200:
    print('取得できませんでした。')
    sys.exit()

now = datetime.date.today()                                                 #今日の日付を取得
now_date = now.day

html = r.content
soup = BeautifulSoup(html, 'lxml')                                          #BeautifulSoupオブジェクトの作成
div_element = soup.find_all('tbody')
tds = div_element[0].find_all('td')

calender = []                                                              
for t in tds:
    calender.extend(t['class'])

status = calender.index('sbc-today') - 1

# print(calender[status])
# print(calender)

print("今日の日付は" + now.strftime("%Y年%-m月%-d日") + "、")       #--年--月--日にformatする

if calender[status] == "sbc-status-booked":
    print("本日は休診日です")
elif calender[status] == "sbc-status-changeover":
    print("診療時間が変更になっています。詳細は http://kidsallergycl.jp/ を確認してください。")
elif calender[status] == "sbc-status-free":
    print("本日は診療日です")
