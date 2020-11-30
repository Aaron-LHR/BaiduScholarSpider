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

from DatabaseDriver import DatabaseDriver
from Parser import Parser


class Reptile:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.183 Safari/537.36"}
        self.databaseDriver = DatabaseDriver(host="49.232.157.22", port=3306, user="BUAA", passwd="BUAA1821",
                                             database_name="BUAA")
        self.numOfDriver = 10
        self.listOfDriver = {}
        for i in range(self.numOfDriver):
            driverAndLock = {
                "driver": DatabaseDriver(host="49.232.157.22", port=3306, user="BUAA", passwd="BUAA1821",
                                         database_name="BUAA"),
                "lock": threading.Lock()
            }
            self.listOfDriver[str(i)] = driverAndLock
            print(str(i) + "号成功连接数据库！")

    def urlEncode(self, keyword, page_number):
        keyword = quote(keyword, encoding="utf-8")
        path = "https://xueshu.baidu.com/s?wd=" + keyword + "&pn=" + str(
            page_number) + "&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&usm=1&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D&sc_hit=1"
        return path

    def getPageNumber(self, keyword):
        # return int(eval(self.databaseDriver.getPageNumber(keyword)) / 10) * 10
        # print(self.databaseDriver.getPageNumber(keyword))
        try:
            return eval(self.databaseDriver.getPageNumber(keyword))
        except:
            return 0

    def searchPaperListByKeyWord(self, keyword):
        if self.databaseDriver.keywordExists(keyword):
            return
        # page_number = self.getPageNumber(keyword)
        page_number = 0
        # print("\"" + keyword + "\"" + "领域已爬取到" + str(page_number) + "条数据，本次继续爬取")
        i = 0
        while True:
            request = urllib.request.Request(url=self.urlEncode(keyword, page_number), headers=self.headers)
            response = urllib.request.urlopen(request)
            html = response.read().decode("utf-8")
            self.listOfDriver[str(i)]["lock"].acquire()
            self.newThreadParse(html, str(i))
            page_number += 10
            i = (i + 1) % self.numOfDriver
            if page_number >= 800:
                break
            # self.databaseDriver.setPageNumber(keyword, str(page_number))
        self.databaseDriver.updateKeyword(keyword)

    def newThreadParse(self, html, i):
        thread = Parser(html, self.listOfDriver[i]["driver"], self.listOfDriver[i]["lock"])
        thread.start()


def GBK2312():
    head = random.randint(0xb0, 0xf7)
    body = random.randint(0xa1, 0xfe)
    val = f'{head:x}{body:x}'
    str = bytes.fromhex(val).decode('gb2312')
    return str


def echo():

        reptile = Reptile()
        while (True):
            keyword = GBK2312()
            print("开始爬取关键字：" + keyword)
            reptile.searchPaperListByKeyWord(keyword)



# if __name__ == '__main__':
#     field = {
#         '1': "计算机",
#         '2': "哲学",
#         '3': "经济",
#         '4': "法律",
#         '5': "文学",
#         '6': "艺术",
#         '7': "历史",
#         '8': "数学",
#         '9': "农学",
#         '10': "医药",
#         '11': "心理",
#         '12': "体育",
#         '13': "工程",
#     }
#
#     while True:
#         print("请选择要爬取的领域：输入阿拉伯数字")
#         for i in range(1, 14):
#             print(str(i) + ':' + field[str(i)])
#         i = input()
#         if i in field.keys():
#             print("开始爬取")
#             break
#     reptile = Reptile()
#     echo(field[i])

# reptile.savePaperByUrl("https://xueshu.baidu.com/usercenter/paper/show?paperid=25e67940fc9a3c7999ab272f72a2b2ab&site=xueshu_se")


def test(url):
    reptile = Reptile()
    reptile.savePaperByUrl(url)


if __name__ == '__main__':
    echo()
    # test(url="https://xueshu.baidu.com/usercenter/paper/show?paperid=ddb0dbbf0c74c23f793dd7fd85ce90c4&site=xueshu_se&hitarticle=1")
