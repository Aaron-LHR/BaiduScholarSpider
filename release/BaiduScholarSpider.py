# -*- coding:UTF-8 -*-
import hashlib
import random
import re
import urllib.request
import urllib.parse
from urllib.parse import quote
from bs4 import BeautifulSoup
from pinyin import pinyin

from DatabaseDriver import DatabaseDriver


class Reptile:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.183 Safari/537.36"}
        self.databaseDriver = DatabaseDriver(host="49.232.157.22", port=3306, user="BUAA", passwd="BUAA1821",
                                             database_name="BUAA")

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
        while True:
            request = urllib.request.Request(url=self.urlEncode(keyword, page_number), headers=self.headers)
            response = urllib.request.urlopen(request)
            html = response.read().decode("utf-8")
            bs = BeautifulSoup(html, "html.parser")
            paper_link = bs.select("h3[class='t c_font']")
            # max_page_number = eval(
            #     bs.select("span[class='nums']")[0].string.lstrip().rstrip().replace('\n', '').replace('\r', '')[
            #     3: -5].replace(',', ""))
            for li in paper_link:
                self.savePaperByUrl("https:" + li.a.attrs['href'])
            page_number += 10
            if page_number >= 800:
                break
            # self.databaseDriver.setPageNumber(keyword, str(page_number))
        self.databaseDriver.updateKeyword(keyword)

    def getTitle(self, main_info):
        try:
            title = main_info.h3.a.string
        except:
            try:
                title = main_info.h3.span.string
            except:
                title = ""
        return title.lstrip().rstrip().replace('\n', '').replace('\r', '')

    def getAuthors(self, main_info):
        authorList = []
        try:
            for author in main_info.select("p[class='author_text']", limit=1)[0].select("span"):
                authorList.append(author.a.string.lstrip().rstrip().replace('\n', '').replace('\r', ''))
        except:
            try:
                for author in main_info.select("p[class='author_text kw_main_s']", limit=1)[0].select("span"):
                    authorList.append(author.a.string.lstrip().rstrip().replace('\n', '').replace('\r', ''))
            except:
                try:
                    for author in main_info.select(".author_wr", limit=1)[0].select(".kw_main_l")[0].select("span"):
                        authorList.append(author.a.string.lstrip().rstrip().replace('\n', '').replace('\r', ''))
                except:
                    authorList = []
        return authorList

    def getAbstract(self, main_info):
        try:
            abstract = main_info.select(".abstract", limit=1)[0].string
        except:
            abstract = ""
        return abstract.lstrip().rstrip().replace('\n', '').replace('\r', '')

    def getKeyWord(self, main_info):
        keywordList = []
        try:
            for keyword in main_info.select(".kw_wr", limit=1)[0].select(".kw_main", limit=1)[0].select("span"):
                keywordList.append(keyword.a.string.lstrip().rstrip().replace('\n', '').replace('\r', ''))
        except:
            try:
                for keyword in main_info.select(".kw_wr", limit=1)[0].select(".kw_main_s", limit=1)[0].select("span"):
                    keywordList.append(keyword.a.string.lstrip().rstrip().replace('\n', '').replace('\r', ''))
            except:
                keywordList = []
        return keywordList

    def getLink(self, main_info):
        try:
            link = main_info.h3.a["href"]
        except:
            link = ""
        return link

    def getTime(self, main_info):
        try:
            time = main_info.select(".year_wr", limit=1)[0].select(".kw_main", limit=1)[
                0].string.lstrip().rstrip().replace('\n', '').replace('\r', '').replace('年', '-').replace('月',
                                                                                                          '-').replace(
                '日', '').replace('.', '-').replace('/', '-')
        except:
            try:
                time = main_info.select(".year_wr", limit=1)[0].select(".kw_main_s", limit=1)[
                    0].string.lstrip().rstrip().replace('\n', '').replace('\r', '').replace('年', '-').replace('月',
                                                                                                              '-').replace(
                    '日', '').replace('.', '-').replace('/', '-')
            except:
                try:
                    for t in main_info.select("div[class='common_wr']"):
                        if t.p.string.lstrip().rstrip().replace('\n', '').replace('\r', '') == "会议时间：":
                            if len(t.select(".kw_main_s", limit=1)) > 0:
                                time = t.select(".kw_main_s", limit=1)[0].string
                            else:
                                time = t.select(".kw_main", limit=1)[0].string
                            break
                        elif t.p.string.lstrip().rstrip().replace('\n', '').replace('\r', '') == "申请日期：":
                            time = t.select(".kw_main_l", limit=1)[0].string
                            break
                    else:
                        time = ""
                except:
                    try:
                        time = main_info.select(".year_wr", limit=1)[0].select(".kw_main_s", limit=1)[
                            0].string
                    except:
                        time = ""
        time = time.lstrip().rstrip().replace('\n', '').replace('\r', '').replace('\r', '').replace('年', '-').replace('月', '-').replace('日', '').replace('.', '-').replace('/', '-')
        time = re.sub("[^0-9-]", "", time)
        if len(time) == 4:
            time = time + "-00-00"
        elif len(time) == 7 or len(time) == 6:
            time = time + "-00"
        return time

    def getDOI(self, main_info):
        try:
            DOI = main_info.select(".doi_wr", limit=1)[0].select(".kw_main", limit=1)[0].string
        except:
            DOI = ""
        return DOI.lstrip().rstrip().replace('\n', '').replace('\r', '')

    def getISBN(self, main_info):
        try:
            ISBN = main_info.select(".doi_wr", limit=1)[0].select(".kw_main", limit=1)[0].string
        except:
            ISBN = ""
        return ISBN.lstrip().rstrip().replace('\n', '').replace('\r', '')

    def getPatentNumber(self, main_info):
        try:
            for t in main_info.select("div[class='common_wr']"):
                if t.p.string.lstrip().rstrip().replace('\n', '').replace('\r', '') == "申请(专利)号：":
                    patentNumber = t.select(".kw_main_l", limit=1)[0].string
                    break
            else:
                patentNumber = ""
        except:
            patentNumber = ""
        return patentNumber.lstrip().rstrip().replace('\n', '').replace('\r', '').replace('\r', '')

    def getCitedQuantity(self, main_info):
        try:
            cited_quantity = main_info.select(".ref_wr", limit=1)[0].select(".ref-wr-num", limit=1)[0].a.string
        except:
            cited_quantity = ""
        return cited_quantity.lstrip().rstrip().replace('\n', '').replace('\r', '')

    def getCategory(self, dtl_journal):
        try:
            if dtl_journal.h3.string == "来源期刊":
                return "期刊"
            elif dtl_journal.h3.string == "来源出版社" or dtl_journal.h3.string == "来源图书":
                return "图书"
            elif dtl_journal.h3.string == "来源会议":
                return "会议"
            elif dtl_journal.h3.string == "来源学校":
                return "学位"
            else:
                return ""
        except:
            return ""

    def getSource(self, dtl_journal):
        try:
            return dtl_journal.select(".journal_title")[0].string
        except:
            return ""

    def getID(self, title, authors, category):
        return pinyin.get_initial(category, '').upper() + '-' + hashlib.md5(
            str(title + ',' + ','.join(authors)).encode('utf-8')).hexdigest()

    def savePaperByUrl(self, url):
        request = urllib.request.Request(url=url, headers=self.headers)
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        bs = BeautifulSoup(html, "html.parser")
        main_info = bs.select("div[class='main-info']", limit=1)
        dtl_journal = bs.select("div[class='dtl_journal']", limit=1)
        title = self.getTitle(main_info[0])
        authors = self.getAuthors(main_info[0])
        try:
            category = self.getCategory(dtl_journal[0])
        except:
            category = "专利"
        try:
            source = self.getSource(dtl_journal[0])
        except:
            source = ""
        item = {
            "title": title,
            "authors": authors,
            "category": category,
            "id": self.getID(title, authors, category),
            "time": self.getTime(main_info[0]),
            "DOI": self.getDOI(main_info[0]),
            "ISBN": self.getISBN(main_info[0]),
            "patentNumber": self.getPatentNumber(main_info[0]),
            "citedQuantity": self.getCitedQuantity(main_info[0]),
            "abstract": self.getAbstract(main_info[0]),
            "keywords": self.getKeyWord(main_info[0]),
            "link": self.getLink(main_info[0]),
            "source": source
        }
        print("")
        print("已爬取：")
        for key in item.keys():
            print(key + ': ', end='')
            print(item[key])
        # self.databaseDriver.insertDocument(item)
        self.databaseDriver.insertDocument(item["title"], item["authors"], item["category"], item["id"], item["time"],
                                           item["DOI"], item["ISBN"], item['patentNumber'], item["citedQuantity"],
                                           item["abstract"], item["keywords"], item["link"], item["source"])


def GBK2312():
    head = random.randint(0xb0, 0xf7)
    body = random.randint(0xa1, 0xfe)
    val = f'{head:x}{body:x}'
    str = bytes.fromhex(val).decode('gb2312')
    return str


def echo():
    try:
        while (True):
            keyword = GBK2312()
            print("开始爬取关键字：" + keyword)
            reptile = Reptile()
            reptile.searchPaperListByKeyWord(keyword)
    except Exception as e:
        print(e)
        echo()


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
