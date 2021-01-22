import re
import datetime

def dayofweek(day):
    """
    日本語の曜日をdatetimeのweekday表記にして返す
    '月':0, '火':1, '水':2, '木':3, '金':4, '土':5, '日':6
    祝日：７　年末年始：８
    """
    week = {'月':0, '火':1, '水':2, '木':3, '金':4, '土':5, '日':6}
    if day == '祝日':
        tmpday = 7
    elif day == '年末年始':
        tmoday = 8
    else:
        tmp = day[0]
        tmpday = week[tmp]
    return tmpday


print(dayofweek('祝日'))