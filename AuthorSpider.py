# -*- coding:UTF-8 -*-
import hashlib
import random
import re
import threading
import urllib.request
import urllib.parse
from urllib.parse import quote
from bs4 import BeautifulSoup
from pinyin import pinyin
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from DatabaseDriver import DatabaseDriver
from AuthorParser import AuthorParser


class AuthorSpider:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.183 Safari/537.36"}
        self.databaseDriver = DatabaseDriver(host="49.232.157.22", port=3306, user="BUAA", passwd="BUAA1821",
                                             database_name="BUAA")
        self.numOfDriver = 1
        self.listOfDriver = {}
        for i in range(self.numOfDriver):
            driverAndLock = {
                "driver": DatabaseDriver(host="49.232.157.22", port=3306, user="BUAA", passwd="BUAA1821",
                                         database_name="BUAA"),
                "lock": threading.Lock()
            }
            self.listOfDriver[str(i)] = driverAndLock
            print(str(i) + "号成功连接数据库！")

    def authorSearchResultUrlEncode(self, author_name):
        author_name = quote(author_name, encoding="utf-8")
        path = "https://xueshu.baidu.com/usercenter/data/authorchannel?cmd=inject_page&author=" + author_name
        # print(path)
        return path

    def authorInformationPageUrlEncode(self, link):
        path = "https://xueshu.baidu.com " + link
        return path

    def getPageNumber(self, keyword):
        try:
            return eval(self.databaseDriver.getPageNumber(keyword))
        except:
            return 0

    def searchAuthorListByKeyWord(self, keyword):
        if self.databaseDriver.authorKeywordExists(keyword):
            return
        i = 0
        request = urllib.request.Request(url=self.authorSearchResultUrlEncode(keyword), headers=self.headers)
        response = urllib.request.urlopen(request)
        authorListHtml = response.read().decode("utf-8")
        # print(authorListHtml)
        with open("author.html", mode='w', encoding="utf-8") as file:
            file.write(authorListHtml)
        bs = BeautifulSoup(authorListHtml, "html.parser")
        try:
            personalSearchDiv = bs.select("#personalSearch_result")
            for personName in personalSearchDiv.select("a[class='personName']"):
                link = personName.get("href")
                self.listOfDriver[str(i)]["lock"].acquire()
                self.newThreadParse(link, str(i))
                i = (i + 1) % self.numOfDriver
                i += 1
            # self.databaseDriver.setPageNumber(keyword, str(page_number))
            self.databaseDriver.updateAuthorKeyword(keyword)
        except:
            return

    def newThreadParse(self, link, i):
        thread = AuthorParser(link, self.listOfDriver[i]["driver"], self.listOfDriver[i]["lock"])
        thread.start()


def GBK2312():
    head = random.randint(0xb0, 0xf7)
    body = random.randint(0xa1, 0xfe)
    val = f'{head:x}{body:x}'
    str = bytes.fromhex(val).decode('gb2312')
    return str


def echo():
    try:
        authorSpider = AuthorSpider()
        while (True):
            keyword = GBK2312()
            print("开始爬取关键字：" + keyword)
            authorSpider.searchAuthorListByKeyWord(keyword)
    except Exception as e:
        print("echoError" + str(e))
        echo()


if __name__ == '__main__':
    echo()
