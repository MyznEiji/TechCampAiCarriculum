# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 21:44:48 2017

@author: takma

"""

from selenium import webdriver
# python2.X系の場合はurllibを使う
import urllib.request
import xlsxwriter
from datetime import datetime
#import urllib2
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import xlrd
import os
import time

# 取得対象のURLリスト
URL_list = ["https://news.bitcoin.com/",
            "https://www.cs.com/"]

# phantomjs_pathとworkbookのパスは適宜修正して使うこと!

# phantomjsのexeファイルのpath(ここからダウンロード：http://phantomjs.org/download.html)
phantomjs_path = "/Users/miyazonoeiji/Desktop/phantomjs-2.1.1-macosx"

current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
site_name = "coindesk"
workbook_path = ("/Users/miyazonoeiji/Desktop/kenbitcoinin_%s.xlsx") % (site_name)
workbook = xlsxwriter.Workbook(workbook_path)
worksheet = workbook.add_worksheet()

# カラム名を設定
worksheet.write(0, 0, "URL")
worksheet.write(0, 1, "article")
worksheet.write(0, 2, "author")
worksheet.write(0, 3, "time")

if __name__ == "__main__":

    # PhantomJSのドライバー作成
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",
    }
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87")
    driver = webdriver.PhantomJS()

    # len(URL_list)
    # このコードではhttps://news.coindesk.com/のみ試しに取得
    for i in range(1):
        startPageURL = URL_list[0]
        print("startPageURL : " + startPageURL)
        driver.get(startPageURL)
        for xxx in range(10):
            site_URL = "https://news.bitcoin.com/page/xxx/"
            driver.get(site_URL)
            time.sleep(5)  # ページが読み込まれるまで待機
        data = driver.page_source.encode('utf-8')
        time.sleep(10)  # ページが読み込まれるまで待機
        html = BeautifulSoup(data, "lxml")
#        print (data)
        print("get each article ...")
        # ニュース記事へのリンク一覧を取得
        links = html.find_all("a", class_="fade")
        print(len(links))
        for j in range(int(len(links))):
            link = links[j]
            articlepageURL = link.get('href')
            print(articlepageURL)
            worksheet.write(j + 1, 0, articlepageURL)
            try:
                # phantomjsでやると、メインコンテンツがとれなかったのでurllibで対応
                request = urllib.request.Request(
                    url=articlepageURL, headers=headers)
                time.sleep(10)  # ページが読み込まれるまで待機
                response = urllib.request.urlopen(request)
                time.sleep(10)  # ページが読み込まれるまで待機
                # connection reset error対策
                while True:
                    try:
                        # htmlを変換（html.parserを付けないとメインコンテンツが読み込めない）
                        arti_html = BeautifulSoup(
                            response.read().decode('utf-8'), 'html.parser')
                        print("yeah!")
                        break
                    except ConnectionResetError as e:
                        print("ConnectionResetError occurred")
                        break
                text_article = ""
                # メインコンテンツが含まれているclassを取得
                article = arti_html.find(class_="td-module-thumb")
                # textがpタグで区切られているので、pタグ毎にテキストを取得
                for each_content in article.find_all("bookmark"):
                    text_article = text_article + each_content.text
                worksheet.write(j + 1, 1, text_article)
                # 著者名を取得
                author_ = arti_html.find(
                    "a", class_="td-author-name vcard author")
                worksheet.write(j + 1, 2, author_.text)
                # 投稿日時情報を取得
                time_info = arti_html.find("span", class_="btc-post-meta")
                worksheet.write(j + 1, 3, time_info.text.replace("\n", ""))
#                if not time_info is None:
#                time_info_str = [x.strip() for x in time_info.text.split("|\r\n")]
#                worksheet.write(j+1, 3, time_info_str[0])
            except Exception as e:
                print("ERROR:%s" % (e))
        workbook.close()
