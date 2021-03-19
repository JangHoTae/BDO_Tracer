import requests
from bs4 import BeautifulSoup
import re
import schedule
import time
from time import sleep
import os
import glob
import csv
import pandas as pd
from openpyxl import Workbook
import numpy as np
import unicodedata
from numpy import nan as NA

count = 1

def koreaFormat (string, width, align='<', fill=' '):
    count = (width - sum(1 + (unicodedata.east_asian_width(c) in "WF")
                         for c in string))
    return {
        '>': lambda s: fill * count + s,
        '<': lambda s: s + fill * count,
        '^': lambda s: fill * (count / 2) + s + fill * (count / 2 + count % 2)
    }[align](string)
def guild_trace_init():

    f = open("AudiTestVersion.csv", 'w')
    f.write("캐릭명,박제 링크,가입 상태,상태 변경일\n")

    source = requests.get(
        "https://www.kr.playblackdesert.com/Adventure/Guild/GuildProfile?guildName=%EC%99%9C%EC%9D%B4%EB%A6%AC%EC%8B%9C%EB%81%84%EB%9F%AC%EC%9A%B4%EA%B2%83%EC%9D%B4%EB%83%90").text
    soup = BeautifulSoup(source, "html.parser")
    members = soup.select(".character_desc")

    for keys in members:
        nickname = keys.select_one(".text").text.strip()
        profileLink = keys.find("a")["href"]
        f.write(nickname + "," + profileLink + "\n")

    f.close()

def csv_to_excel():
    global count
    wb = Workbook()
    ws = wb.active
    with open('AudiTestVersion.csv', 'r', encoding='utf8') as f:
        for row in csv.reader(f):
            ws.append(row)

    wb.save('Audi_Test_'+str(count)+'.xlsx')
    #wb.save('Audi_Test.xlsx')


def record_trace():
    global count
    now = time.localtime()
    current = "%04d - %02d - %02d" % (now.tm_year, now.tm_mon, now.tm_mday)


    excel_standard = pd.read_excel('Audi_Test.xlsx')

    print(excel_standard)
    #excel_new = pd.read_excel('Audi_Test.xlsx')

    for i in excel_standard['캐릭명']:
        if i is not None:
            excel_standard['가입 상태']='가입중'

    #이제 데이터 비교해서 값 바꿀 예정
    excel_new = pd.read_excel('Audi_Test_2.xlsx')

    id_dropped = set(excel_standard['캐릭명']) - set(excel_new['캐릭명'])
    id_added = set(excel_new['캐릭명']) - set(excel_standard['캐릭명'])

    df_dropped = excel_standard[excel_standard['캐릭명'].isin(id_dropped)].iloc[:]
    df_added = excel_new[excel_new['캐릭명'].isin(id_added)].iloc[:]



    #런한쓰레기들 가입 상태 변경
    df_dropped['가입 상태'] = '탈주하는쓰레기'
    for i in excel_standard.index:
        for j in df_dropped.index:
            if df_dropped.loc[j,'캐릭명'] == excel_standard.loc[i, '캐릭명']:
                excel_standard.loc[i,'가입 상태'] = '탈주하는쓰레기'

    #새로온쓰레기들 추가
    df_added['가입 상태'] = '새로온 쓰레기'

    df_added['상태 변경일'] = current
    excel_standard=excel_standard.append(df_added)



    """ 데이터 값 None 인지 체크하기 
    if excel_standard.loc[27, '상태 변경일']:
        print(excel_standard.loc[27, '상태 변경일'])
    else:
        print('Not none')
    if excel_standard.loc[25, '상태 변경일']:
        print(excel_standard.loc[25, '상태 변경일'])
    else:
        print('Not none')
    """

    excel_standard.fillna('0')

    print(excel_standard.loc[27,'상태 변경일'])

    print(excel_standard.loc[3,'상태 변경일'])
    #상태 변경일 입력
    for i in df_dropped.index:
        if excel_standard.loc[i,'상태 변경일'].isna().any() == False:
            df_dropped.loc[i,'상태 변경일'] = current

    for i in df_added.index:
        if excel_standard.loc[i, '상태 변경일'].bool() == False:
             df_added.loc[i, '상태 변경일'] = current

    """
    print('니하오' + df_dropped.loc[27, '상태 변경일'])
    print('니하오' + df_dropped.loc[28, '상태 변경일'])
    print('니하오' + excel_standard.loc[27, '상태 변경일'])
    """
    #깔끔하게 출력
    if df_dropped.empty:
        print('There is no more Betrayer')
    else:
        print('   [가 문 명]           |    [가 입 상 태]    |    [상 태 변 경 일 자]   ')
        for i in df_dropped.index:
            print("   %s |    %s   |    %s " % (koreaFormat(df_dropped.loc[i, '캐릭명'], 20), koreaFormat(df_dropped.loc[i, '가입 상태'], 10), df_dropped.loc[i,'상태 변경일']))
            #print("   %s |    %s" % (koreaFormat(df_dropped.loc[i, '캐릭명'], 20), koreaFormat(df_dropped.loc[i, '가입 상태'], 10)))
    if df_added.empty:
        print('There is no more fresh man')
    else:
        print('   [가 문 명]           |    [가 입 상 태]    |    [상 태 변 경 일 자]   ')
        for i in df_added.index:
            print("   %s |    %s    | %s " % (koreaFormat(df_added.loc[i, '캐릭명'], 20), koreaFormat(df_added.loc[i, '가입 상태'], 10), koreaFormat(df_added.loc[i,'상태 변경일'],20)))


    excel_standard.to_excel(excel_writer='AUDI_TEST.xlsx', index=False)
def print_time():
    now = time.localtime()
    current = "%04d - %02d - %02d  %02d : %02d : %02d" % (
        now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)

    print('-----' + current + '-----')
def trace_start():
    global count
    guild_trace_init()
    csv_to_excel()
    for i in range(1,3500):
        record_trace()
        print_time()
        sleep(1)
    count+=1

trace_start()
#csv_to_excel()
#guild_trace_init()
schedule.every(12).hours.do(trace_start)
#schedule.every().seconds.do(trace_start)


while True:
    schedule.run_pending()
    time.sleep(1)
