#coding: utf-8

"""
scrapingで取得したwebページをparseでJSON形式に変換して、
herokuのpostgresqlに登録するflaskアプリ。
"""

import flask
import os
import requests
import psycopg2
import time
from html_parse import parse

jps = ["あ","い","う","え","お","か","き","く","け","こ","さ","し","す","せ","そ",\
      "た","ち","つ","て","と","な","に","ぬ","ね","の","は","ひ","ふ","へ","ほ",\
      "ま","み","む","め","も","や","ゆ","よ","ら","り","る","れ","ろ","わ","を","ん"]

page = parse.PageFormatting()
# 50音順でURLを取得する
for jp in jps: 
    url_list = page.get_url(jp)
#     for url in url_list:
          