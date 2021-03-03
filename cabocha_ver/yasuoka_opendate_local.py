#coding: utf-8

# http://www.yasuokaiin.jp/
# から定休日、臨時の休みをピックアップして、
# 今日は該当するか標準出力
# CaboChaで構文解析するver

#todo:cabochaでパースして得られた臨時休業の日付をjpholidayの祝日に追加する。

import datetime
import time
import locale
import re
import os
from collections import defaultdict
import jpholiday
import CaboCha
import requests
from bs4 import BeautifulSoup

class GetDate():
    """
    日付、曜日を扱うクラス
    """
    def __init__(self, dt_now, holiday):
        # locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
        self.dt_now = datetime.datetime.now().strftime('%Y,%-m,%-d,%p,%I,%M,%A').split(',')
        self.holiday = jpholiday.is_holiday(dt_now.date())

    def jp_weekday(self):
        """
        英語ロケール表記の曜日を日本語表記に変換して返す
        """
        week = {'Monday':'月', 'Tuseday':'火', 'Wednesday':'水', 'Thursday':'木',
                'Friday':'金', 'Saturday':'土', 'Sunday':'日'}
        wd = week[self.dt_now[-1]]
        return wd

class AppendHoliday(jpholiday.OriginalHoliday):
    """
    Cabochaでパースした臨時休業の日付を休日として追加する
    """
    def _is_holiday(self, date):
        #if 臨時休業日リスト in 指定された日付　として、該当する日付が存在するならfalseを返す
        if date == datetime.date(2020, 2, 9):
            return True
        return False

    def _is_holiday_name(self, date):
        return '臨時休業'


class Scraping():
    """
    bs4を使用してwebページをスクレイピングする。
    ファイルがすでに存在する→差分チェック→異なるなら再度ダウンロード
                                    　↪同じならsoupオブジェクトに変換
    ファイルが存在しない→ダウンロード→soupオブジェクトに変換してから整形して保存
    """
    def __init__(self, file_exist):
        self.file_exist = os.path.isfile('scraping.html')
        file_exist = self.file_exist

    def get_page(self, target_url, soup):
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)  \
                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}
        time.sleep(2)
        r = requests.get(target_url, headers=headers)                                             
        if r.status_code != 200:
            print('取得できませんでした。')
        if self.file_exist == True:
            #ファイルが存在する
            self.soup = BeautifulSoup(open('scraping.html'), 'html.parser', from_encoding='shift-jis')
            # soup = BeautifulSoup(open('scraping.html'), 'html.parser', from_encoding='utf-8')
        else:
            html = r.content
            self.soup = BeautifulSoup(html, 'html.parser')
            with open('scraping.html', mode = 'w', encoding='utf-8') as fw:
                fw.write(soup.prettify())
        return soup

    def scrape(self):
        soup = self.soup
        list = []
        for tag in soup.find_all(['dd', 'dt']):
            t = tag.get_text(strip=True)
            if '休' in t or '年内' in t:
                list.append(t)
        return list


class SpecialHolidayPerse(Scraping):
    """
    臨時休診日を"お知らせ"からパースしてdefaultdict形式に変換する
    """
    def __init__(self):
        info_element = soup.find_all('div', class_='info')

    def dtddtag_tokeyvalue(self, elements):
        """
        defaultdictを使ってdtをkey、ddをvalueにする関数
        """
        info_contents = defaultdict(list)
        for e in elements.find_all(['dt', 'dd']):
            if e.name =='dt':
                # dt = e.text.rstrip('\u3000')
                # ここで\nを取る
                dt = e.text
                key = dt[0:3]
            if key and e.name == 'dd':
                dd = e.text.rstrip('\u3000')
                info_contents[key].append(dd)
        return info_contents

    def specialholiday_infoperse(self, contents):
        """
        臨時休診日の文字列をcabochaでパースする
        文字列をバラして形態素を結合しつつ[{c:文節, to:係り先id}]の形に変換して
        辞書配列chunksに格納する関数
        """
        c = CaboCha.Parser()
        tree = c.parse(contents)
        chunks = []
        text = ""
        toChunkId = -1
        for i in range(0, tree.size()):
            token = tree.token(i)
            if token.chunk != None:
                text = token.surface
                toChunkId = token.chunk.link
            else:
                text = text + token.surface

        # 文末かchunk内の最後の要素のタイミングで出力
            if i == tree.size() - 1 or tree.token(i+1).chunk:
                chunks.append({'c': text, 'to': toChunkId})
        return chunks

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー⇓分解して見直し⇓ーーーーーーーーーーーーーーーーーーーーーーーーーー
    # def absence_day(self, dt_nowday):
    #     """
    #     例えば　dt_now = 2016/4/5 am9:00 なら　返り値はリストで[診療中：※１, 11:00：※２]
    #     ①診療状態：渡された時間が午前か午後か確認して、その時間が診療中かどうかを返す
    #     ②診療終了時間：「臨時休業のお知らせ」本文内に臨時休診の時間が書いてある場合はそれを返す。通常の診療日は、その日の診療終了時間が何時か返す。

    #     診療中か終了しているかを判断する処理
    #     1.曜日を確認する。→日曜日ならbreakして、リスト['休診日', ':']を返す。→火曜日、土曜日且つ、12時以降ならbreakして、リストの先頭に'診察終了'を追加する
    #     2.時間を確認する。→8時半、14時半からそれぞれ210分以内なら'診療中'をリストの先頭に追加する　→それ以外の時間の場合'診察終了'をリストの先頭に追加する　
    #     終了時間を検索する処理　
    #         1.渡された日付の年度を見て、temp_closureの該当する年度keyのリストを検索する。
    #         2.文章をcc_dictに渡してパース
    #         3.文章の先頭から'4'月に該当する箇所をさがす
    #         4.一致する箇所がなければcontinueして2.に戻る
    #         5.一致したら4月がかかっている文字が'5'日と一致するか確認する
    #         6.受付終了時間が文章中に存在するか検索する
    #         7.無い場合は何も返さない
    #         8.存在する場合はリストに追加して返す（今回の場合１１：００を返す）
    #     """

    #     treat_status = {'status':'', 'endingtime':':'}
    #     meridiem = dt[3]
    #     dtweekday = dt_now.weekday()
    #     openminute = data['open_minute']

    #     amstarttime = openminute[0].split(':')
    #     am_start = datetime.datetime.combine(dt_now, datetime.time(hour=int(amstarttime[0]), minute=int(amstarttime[1])))

    #     pmstarttime = openminute[2].split(':')
    #     pm_start = datetime.datetime.combine(dt_now, datetime.time(hour=int(pmstarttime[0]), minute=int(pmstarttime[1])))

    #     pmclose = {'status':'午後休診', 'endingtime':'12:00'}
    #     closeday = {'status':'休診日', 'endingtime': ':'}

    #     # 本文中の臨時休業をcabochaで解釈する。
    #     for intext in in_text[dt_nowday[0]]:
    #         chunktext = ccdict(intext)
    #         md = 1
    #         for c in chunktext:
    #             closetime = []
    #             if (c['c'] == dt_nowday[md] and chunks[c['to']]['c'] == dt_nowday[md+1]):
    #                 treat_status['status'] = '臨時休診'

    #             if (c['c'] in '時' or c['c'] in '分'):
    #                 num = re.sub("\\D", "", c['c'])
    #                 closetime.append(num)

    #             temp_endingtime = ':'.join(closetime)
    #             treat_status['endingtime'] = temp_endingtime
    #             break

    #     #普段の日付の場合の診療時間チェック
    #     if dtweekday in data['close_day']:
    #         treat_status.update(closeday)

    #     if dtweekday in data['pm_close']:
    #         treat_status.update(pmclose)

    #     #診療時間の午前午後判定
    #     if treat_status['status'] == '':
    #         if meridiem == '午前':
    #             treat_status['endingtime'] = '12:00'
    #             am_timesub = (abs(dt_now - am_start).total_seconds())/60
    #             if am_timesub <= int(openminute[1]):
    #                 treat_status['status'] = '診療中'
    #             else:
    #                 treat_status['status'] = '診療時間外'

    #         if meridiem == '午後':
    #             treat_status['endingtime'] = '18:00'
    #             pm_timesub = (abs(dt_now - pm_start).total_seconds())/60
    #             if pm_timesub <= int(openminute[3]): 
    #                 treat_status['status'] = '診療中'
    #             else:
    #                 treat_status['status'] = '診療時間外'

    #     return treat_status
#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー⇑分解して見直し⇑ーーーーーーーーーーーーーーーーーーーーーーーーーー

class DefaultConsultimePerse(Scraping):
        """
        通常診療日を判定するクラス
        """
        def __init__(self):
            self.right_div = soup.find('div', id='right')


        def make_holidaydecison(self):
            """
            休日判定用リストを作る関数
            """
            pass


class OfficehourDecison(GetDate):
        """
        作成した臨時休診日リスト、通常休診日リストを使用して
        現在の日時が休診日か判定して画面に出力する
        """
        def during_officehour(self):
            """
            holiday_decisonリストを使って診療時間内か確認する
            診療時間内→True
            診療時間外→False
            """
            pass
        def print_decisonresult(self):
            """
            判定した結果を整形して出力する
            """
            print("やすおか小児科医院 今やってる？クローラー (旧版)\n\n今日の日付は" + dt_now.strftime("%Y年%-m月%-d日、%p%I時%M分" +  + "です。"))
            treat = absence_day(dt)
            if treat['status'] not in ['診療中', '診療時間外']:
                print('本日は'+ treat['status'] + 'です。')
                if treat['endingtime'] != ':':
                    print('診療時間は' + treat['endingtime'] + 'までです。')
            else:
                print('只今の時間は'+ treat['status'] + 'です。診療時間は' + treat['endingtime'] + 'までです。')

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーここからスクレイピングの処理

#ページ右側のdivを取得
right_div = soup.find('div', id='right')                                    
consul_element = right_div.find('dl')

data = dtdd_dict(consul_element)

#診療時間keyのvalueから午前の診療時間、午後の診療時間を計算してopen_minuteに入れる
open_hour = data["診療時間"]

for i in range(len(open_hour)):
    #開始時刻のみを抽出
    openhour = open_hour[i].split('-')[0]
    data["open_minute"].append(openhour) 

    #それぞれの開始時刻から何分開いているか計算する
    t = re.split('[:-]', open_hour[i])
    for j in range(len(t)):
        t[j] = int(t[j])
    total = (t[2] * 60 + t[3]) - (t[0] * 60 + t[1]) 
    data["open_minute"].append(total) 
else:
    del data['診療時間']

# cabochaを使って休診日を{'close_day': ['日曜', '祝日', '年末年始']に。
weekday = data["休診日"]
chunks = ccdict(weekday[0])

#「火曜日土曜日午後」をdata辞書に'pm_close': ['火曜日', '土曜日']の形で持つ
#それ以外のものでpm_closeに含まれないものはclose_dayに格納する
for chunk in chunks:
    if (chunk['to'] >= 0 and '午後' in chunks[chunk['to']].values()):
        #午後休診の曜日の処理
        data["pm_close"].append(chunk['c'])
        pm = re.findall(".*?日", data["pm_close"][0])
        for p in range(len(pm)):
            pmtmp = dayofweek(pm[p])
            data['pm_close'].append(pmtmp)
        else:
            data['pm_close'].pop(0)

#一日休診の曜日の処理
pm_close = data['pm_close']
for c in range(len(chunks)):
    for p in range(len(pm_close)-1):
        #午後休診の曜日の場合はclose_dayに追加しない
        if chunks[c].get('c').startswith(pm[p]) or chunks[c].get('c') == '午後':    
            continue
        else:
            closetmp = dayofweek(chunks[c].get('c').strip("、"))
            data['close_day'].append(closetmp)
else:
    del data['休診日']

#臨時休診日を”お知らせ”から取得する処理
#余分な文章を削除して、年度と本文だけにする
info_element = soup.find_all('div', class_='info')

#本文に休診を意味する文字列が含まれる文章を抽出する。
info_txt = info_element[0].find_all(['dt', 'dd'])
match_str = re.compile('休診|診察受付|外来受付|年末年始|年内の診療')
un_match_str = re.compile('お知らせ|おしらせ')
last_str = re.compile('御了承|ご了承|お願い致します')

in_text = defaultdict(list)
num = 0

for element in info_txt:
    if element.name == 'dt':
        year = element.text
        key = re.sub(r'/.*$', '', year)
    if key and element.name == 'dd':
        if (match_str.search(info_txt[num].text) and not un_match_str.search(info_txt[num].text)):
            text = info_txt[num].text.split('。')
            for texts in range(len(text)):
                if last_str.search(text[texts]) or not text[texts]:
                    continue
                in_text[key].append(text[texts])
    num += 1

if __name__ == '__main__':
    PrintOpenDate()