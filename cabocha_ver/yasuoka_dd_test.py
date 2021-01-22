#coding: utf-8

import datetime
import time
import locale
import re
from collections import defaultdict
import jpholiday
import CaboCha
import requests
from bs4 import BeautifulSoup

def scrape(filename):
    soup = BeautifulSoup(open(filename), 'html.parser', from_encoding='shift-jis')
    list = []
    for tag in soup.find_all(['dd', 'dt']):
        t = tag.get_text(strip=True)
        if '休' in t or '年内' in t:
            list.append(t)
    return list

l = scrape('yasuoka_index.html')
print(l)