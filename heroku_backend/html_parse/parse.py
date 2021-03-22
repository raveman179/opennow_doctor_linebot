#coding: utf-8

"""
取得したページを解析して、登録用JSONを返す
JSONのフォーマットはmemoに記述したテーブルの定義に沿って作成する。
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# import chromedriver_binary
from webdriver_manager.chrome import ChromeDriverManager

from dataclasses import dataclass, field, asdict
from typing import ClassVar, List, Dict, Tuple

from dataclasses_json import dataclass_json

from bs4 import BeautifulSoup
import requests
from ginza import *
import spacy
import os
import time
import json
import re
import copy
import jaconv
from collections import OrderedDict

from pprint import pprint

# todo : info_extractionで抽出したlistから必要な要素の検索方法とjsonへパースする処理 
@dataclass
class opentime:
    am_start : str = ""
    am_end : str = ""
    pm_start : str = ""
    pm_end : str = ""

@dataclass
class clinic_openday:
        mon : opentime = opentime()
        tus : opentime = opentime()
        wed : opentime = opentime()
        thu : opentime = opentime()
        fri : opentime = opentime()
        sat : opentime = opentime()
        sun : opentime = opentime()
        holiday : opentime = opentime()

@dataclass
class closetime:
    am : bool = False
    pm : bool = False

@dataclass
class clinic_closeday:
    '''
    一日休診の曜日を持つdataclass
    休診日：True 診療日：True
    '''
    mon : closetime = closetime()
    tus : closetime = closetime()
    wed : closetime = closetime()
    thu : closetime = closetime() 
    fri : closetime = closetime() 
    sat : closetime = closetime()
    sun : bool = False
    hol : bool = False

@dataclass_json
@dataclass
class clinic_info:
    name: str = None
    openday: clinic_openday = clinic_openday()
    # openday: str = None
    closeday: clinic_closeday = clinic_closeday()
    med_service: str = None
    address: str = None
    telephone: str = None

class PageFormatting:
    """
    # 一日休診の場合:True 午後休診の場合:am_only
                # "祝祭日"、"祝日"、"お盆"等々、祝祭日を意味する言葉はすべてholidayをTrueにする。

     # 診療科目コードを作ってエンコードした値を入れる


     https://horomary.hatenablog.com/entry/2019/11/24/033557
    """
    def __init__(self):
        op = Options()
        op.add_argument("--disable-gpu")
        op.add_argument("--disable-extensions")
        op.add_argument("--proxy-server='direct://'")
        op.add_argument("--proxy-bypass-list=*")
        op.add_argument("--start-maximized")
        op.add_argument('--headless')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=op)
        self.clinic_openday = clinic_openday()
       
    def extraction(self, url:str) -> list:
        """
        渡されたURLをbs4でパースして必要な情報
        （医院名、診療受付時間、休診日、住所、電話番号、診療科目等）を抽出する
        """
        self.driver.get(url)
        time.sleep(2)
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        text = soup.get_text()
        text = re.sub(r"[\u3000 \t \xa0]", "", text)
        self.driver.quit()
        return text.strip().split()

    def set_openday(self, openday:list) -> dict:
        """
        '月・火・木・金曜日', '午前9：00～12：00午後2：00～6：30', '土曜日', '午前9：00～12：00午後1：00～3：30','祝日(不定期)', '午前9：00～12：00午後1：00～3：00
        ↓
       {"openday": {"mon": {"am_start": "9:00","am_end": "","pm_start": "","pm_end": ""},"tus": {"am_start": "","am_end": "","pm_start": "","pm_end": ""・・・・}

        """
        openday = [jaconv.z2h(op, ascii=True, digit=True) for op in openday]
        dow_d = {"月":"mon", "火":"tus", "水":"wed", "木":"thu", "金":"fri", "土":"sat","日":"sun", "祝":"holiday"}
        dow_l = ["月", "火", "水", "木", "金", "土", "日"]
        week_pat = re.compile(r"月|火|水|木|金|土|日")
        comp_pat = re.compile(r"(午[前|後][0-9]{1,2}:[0-9]{1,2}~[0-9]{1,2}:[0-9]{1,2})")

        am_pat = re.compile(r"午前(?P<am_start>[0-9]{1,2}:[0-9]{1,2})~(?P<am_end>[0-9]{1,2}:[0-9]{1,2})")
        pm_pat = re.compile(r"午後(?P<pm_start>[0-9]{1,2}:[0-9]{1,2})~(?P<pm_end>[0-9]{1,2}:[0-9]{1,2})")

        opentime_dict = {}
        # 診療受付日の表現に邪魔なので"曜"、"曜日"をstripして、残った月、火、水・・を正規表現でマッチさせる
        openday = [s.replace(' ', '') for s in openday]
        # '月〜金'のような表記を展開してリストにする
        weekday_ext = lambda start, end : dow_l[dow_l.index(start):dow_l.index(end)+1]

        for i,e in enumerate(openday):
            # 曜日の処理
            if week_pat.match(e):
                day = re.sub(r'曜日|曜', "", e)
                
                # 月・金のような表記の場合
                if '･' in day:
                    day = day.split('･') 

                # 月～水・金曜日のような表記の場合
                if (any(['~' in d for d in day]) or any(['〜' in d for d in day])) and isinstance(day, List):
                    tilda = list(filter(lambda i : '~' in i or '〜' in i, day))
                    
                    # ex 月~水・木~土のような表記の対策として、tildaの要素のインデックスをリストにする
                    tilda_index = [day.index(t) for t in tilda]
                
                    between_day = [re.split(r'〜|~', day[t]) for t in tilda_index]
                    day.remove(tilda[0])
                 
                    for b in between_day:  
                        tmp = weekday_ext(b[0], b[1])  
                        day.extend(tmp)
                    ext_day = day

                # 月〜金のような表記の場合
                elif isinstance(day, str):
                    between_day = re.split(r'〜|~', day)            
                    ext_day = weekday_ext(between_day[0], between_day[1])

                # '月火水木'のように区切り文字がない場合
                else:
                    ext_day = list(day)

            elif '祝日' in e:
                ext_day = ['祝']

            else:    
                # 診療時間の処理
                # '午前9：00～12：00午後2：00～6：30' -> am_start:'9:00', am_end:'12:00', pm_start:'2:00', pm_end:'6:30'
         
                if '午前' in e and '午後' in e:
                    timelist = comp_pat.findall(e)
                else:
                    timelist = [e]
                
                for t in timelist:
                    if '午前' in t:
                        am = am_pat.search(t).groupdict()
                        opentime_dict.update(am)
                    elif '午後' in t:
                        pm = pm_pat.search(t).groupdict()
                        opentime_dict.update(pm)

                # clinic_opendayに曜日ごとの開院時間を追加
                ext_day = [dow_d[ext_day[ext]] for ext in range(len(ext_day))]
                
                for ext in ext_day:
                    od = opentime_dict.copy()
                    setattr(self.clinic_openday, ext, od)

    def set_closeday(self, closeday:list) -> dict:
        holiday = re.compile(r'祝.?日|.盆.?|年末年始')
        


        pass


        



    def info_perse(self, item:list) -> dict:
        """
        extractionで抽出した情報をJSON形式に加工する
        """
        name = item[0]
        openday = [item[i] for i in range(item.index('【診療受付時間】')+1, item.index('【休診日】'))]
        self.set_openday(openday)
        
        closeday = item[item.index('【休診日】')+1].split('、')        
        
        
        # for c in closeday:
        #     info_json[closeday][weekday[c]] = "True"

        #     if holiday.search(c) != None:
        #         info_json[closeday][c] = "True"
            
         # 番地が全角の場合、半角に変換する
         # 住所と番地のみにする
        address = jaconv.z2h(item[18], kana=False, ascii=True, digit=True)[8::]

        tel_re = re.search(r'0\d{1,5}-\d{0,4}-\d{4}', item[20])
        telephone = tel_re.group()
       
        med_service = item[item.index("【診療科目】")+1].split() 



        
        
        return name, openday, closeday, address, telephone, med_service


    def get_url(self, word):
        """
        秋田県医師会のページをseleniumでスクレイピングして、保存する。
        1.定期実行する(月一回 一度に取得するページは少なくする)
        2.検索のページ(http://www.acma.or.jp/map/50onIndex.cfm)

        保存したwebページが更新されていたら上書きして保存する。
        更新されていなければ動作をスキップ

        1.scrapingに渡された50音のページを開く
        2.開いたページの上からURLを取得する
        wordには"あ"〜"ん"の五十音が入る
        ループで回してページを取得する
        """
        
        url_regx = re.compile(r'^\.\.\/profile\/details\.cfm\?cd\=')

        TARGET_URL = "http://www.acma.or.jp/map/vu_50onlist.cfm?kw={}".format(word)

        self.driver.get(TARGET_URL)
        pagesource = self.driver.page_source

        soup = BeautifulSoup(pagesource, 'lxml')
        url_list = []

        for a in soup.find_all('a'):
            link = a.get('href')
            if "../profile/details.cfm?cd=" in a.attrs['href']:
                prof = url_regx.sub('http://www.acma.or.jp/profile/details.cfm?cd=', link)
                url_list.append(prof)

        self.driver.quit()
        return url_list


if __name__ == "__main__":
    PageFormatting = PageFormatting()
    # clinic_info = clinic_info()
    # clinic_info.openday.mon.am_start = "9:00"

    # info_json = clinic_info.to_json(indent=4, ensure_ascii=False)
    # print(info_json)

    # item = PageFormatting.extraction("http://www.acma.or.jp/profile/details.cfm?cd=219")
    # print(item)

    opendaylist1 = ['月・火・木・金曜日', '午前9：00～12：00午後2：00～6：30', '土曜日', '午前9：00～12：00午後1：00～3：30','祝日(不定期)', '午前9：00～12：00午後1：00～3：00']
    opendaylist2 = ['月〜金曜', '午前9：00～12：00午後2：00～6：30', '土曜日', '午前9：00～12：00']
    opendaylist3 = ['月火木金曜', '午前 8：30～12：30 午後 2：30～ 6：00', '水・土曜日', '午前9：00～12：00']
    opendaylist4 = ['月・火・木・金', '	午前 8：30～12：00 午後 2：00～ 6：00', '水・土', '午前9：00～12：00']
    opendaylist5 = ['火〜土曜日', '午前 ９：０0～12：０0 午後 2：０0～ 6：00', '第１・３・５月曜日', '午前9：00～12：00']
    # 第１・３・５月曜日がパースできない
    opendaylist6 = ['月～水・金曜日','午前 8：30～12：30 午後 2：30～ 7：00','木曜日','午前 8：30～12：30','土曜日','午前 8：30～12：30 午後 2：00～ 3：00']
    opendaylist7 = ['月～金曜日','午前 8：30～12：30 午後 2：00～ 6：00','土曜日','午前 8：30～12：30','往診（水曜日）','午後2：30～4：00']
    # 「往診」をパースすると水曜日の診療時間が上書きされる
    opendaylist8 = ['月・火･水・金曜日','午前 9：00～12：00','午後 2：00～ 6：00','木・土・祝日','午前 9：00～13：00']

    openday = [opendaylist1, opendaylist2, opendaylist3, opendaylist4, opendaylist5, opendaylist6, opendaylist7, opendaylist8]
    
    PageFormatting.set_openday(opendaylist2)
    # PageFormatting.info_perse(item)

    closeday1 = ['木曜日、祝祭日']
    closeday2 = ['月曜日以外、祝日']
    closeday3 = ['日曜、祝祭日水・土曜日午後']
    closeday4 = ['日曜、祝日４月１日(開業記念日)']
    closeday5 = ['日曜、祝日']
    closeday6 = ['木曜午後、日曜、祝祭日']
    closeday7 = []
    closeday8 = ['水曜・日曜・祝日・お盆休み・年末年始']



    # for c in closeday:
