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


class Spider:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.183 Safari/537.36"}

    def urlEncode(self, starting_city, destination, date):
        starting_city = quote(starting_city, encoding="utf-8")
        destination = quote(destination, encoding="utf-8")
        path = "https://flights.ctrip.com/itinerary/oneway/" + starting_city + "-" + destination + "?date=" + date
        return path

    def searchFlight(self, keyword):
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
                        time = main_info.select(".year_wr", limit=1)[0].select(".kw_main_s", limit=1)[0].string
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
            reptile = Spider()
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
#     reptile = Spider()
#     echo(field[i])

# reptile.savePaperByUrl("https://xueshu.baidu.com/usercenter/paper/show?paperid=25e67940fc9a3c7999ab272f72a2b2ab&site=xueshu_se")

city = {
    '阿勒泰': 'AAT', '阿克苏': 'AKU', '鞍山': 'AOG', '安庆': 'AQG', '安顺': 'AVA', '阿拉善左旗': 'AXF', '澳门': 'MFM', '阿里': 'NGQ',
    '阿拉善右旗': 'RHT', '阿尔山': 'YIE', '巴中': 'BZX', '百色': 'AEB', '包头': 'BAV', '毕节': 'BFJ', '北海': 'BHY', '北京': 'BJS',
    '北京(南苑机场)': 'NAY', '北京(首都国际机场)': 'PEK', '博乐': 'BPL', '保山': 'BSD', '白城': 'DBC', '布尔津': 'KJI', '白山': 'NBS',
    '巴彦淖尔': 'RLK', '昌都': 'BPX', '承德': 'CDE', '常德': 'CGD', '长春': 'CGQ', '朝阳': 'CHG', '赤峰': 'CIF', '长治': 'CIH',
    '重庆': 'CKG', '长沙': 'CSX', '成都': 'CTU', '沧源': 'CWJ', '常州': 'CZX', '池州': 'JUH', '潮州': 'SWA', '潮汕': 'SWA',
    '大同': 'DAT', '达县': 'DAX', '达州': 'DAX', '稻城': 'DCY', '丹东': 'DDG', '迪庆': 'DIG', '大连': 'DLC', '大理': 'DLU',
    '敦煌': 'DNH', '东营': 'DOY', '大庆': 'DQA', '德令哈': 'HXD', '德宏': 'LUM', '鄂尔多斯': 'DSN', '额济纳旗': 'EJN', '恩施': 'ENH',
    '二连浩特': 'ERL', '福州': 'FOC', '阜阳': 'FUG', '抚远': 'FYJ', '富蕴': 'FYN',
    '广州': 'CAN', '果洛': 'GMQ', '格尔木': 'GOQ', '广元': 'GYS', '固原': 'GYU', '高雄': 'KHH', '赣州': 'KOW', '贵阳': 'KWE',
    '桂林': 'KWL', '红原': 'AHJ', '海口': 'HAK', '河池': 'HCJ', '邯郸': 'HDG', '黑河': 'HEK', '呼和浩特': 'HET', '合肥': 'HFE',
    '杭州': 'HGH', '淮安': 'HIA', '怀化': 'HJJ', '海拉尔': 'HLD', '哈密': 'HMI', '衡阳': 'HNY', '哈尔滨': 'HRB', '和田': 'HTN',
    '花土沟': 'HTT', '花莲': 'HUN', '霍林郭勒': 'HUO', '惠阳': 'HUZ', '惠州': 'HUZ', '汉中': 'HZG', '黄山': 'TXN', '呼伦贝尔': 'XRQ',
    '嘉义': 'CYI', '景德镇': 'JDZ', '加格达奇': 'JGD', '嘉峪关': 'JGN', '井冈山': 'JGS', '景洪': 'JHG', '金昌': 'JIC', '九江': 'JIU',
    '晋江': 'JJN', '荆门': 'JM1', '佳木斯': 'JMU', '济宁': 'JNG', '锦州': 'JNZ', '建三江': 'JSJ', '鸡西': 'JXA', '九寨沟': 'JZH',
    '金门': 'KNH', '揭阳': 'SWA', '济南': 'TNA',
    '库车': 'KCA', '康定': 'KGT', '喀什': 'KHG', '凯里': 'KJH', '昆明': 'KMG', '库尔勒': 'KRL', '克拉玛依': 'KRY', '黎平': 'HZH',
    '澜沧': 'JMJ', '连城': 'LCX', '龙岩': 'LCX', '临汾': 'LFQ', '兰州': 'LHW', '丽江': 'LJG', '荔波': 'LLB', '吕梁': 'LLV',
    '临沧': 'LNJ', '陇南': 'LNL', '六盘水': 'LPF', '拉萨': 'LXA', '洛阳': 'LYA', '连云港': 'LYG', '临沂': 'LYI', '柳州': 'LZH',
    '泸州': 'LZO', '林芝': 'LZY', '芒市': 'LUM', '牡丹江': 'MDG', '马祖': 'MFK', '绵阳': 'MIG', '梅县': 'MXZ', '梅州': 'MXZ',
    '马公': 'MZG', '满洲里': 'NZH', '漠河': 'OHE', '南昌': 'KHN', '南竿': 'LZN', '南充': 'NAO', '宁波': 'NGB', '南京': 'NKG',
    '宁蒗': 'NLH', '南宁': 'NNG', '南阳': 'NNY', '南通': 'NTG',
    '澎湖列岛': 'MZG', '攀枝花': 'PZI', '普洱': 'SYM', '琼海': 'BAR', '秦皇岛': 'BPE', '祁连': 'HBQ', '且末': 'IQM', '庆阳': 'IQN',
    '黔江': 'JIQ', '泉州': 'JJN', '衢州': 'JUZ', '齐齐哈尔': 'NDG', '青岛': 'TAO', '日照': 'RIZ', '日喀则': 'RKZ', '若羌': 'RQA',
    '神农架': 'HPG', '石狮': 'JJN', '莎车': 'QSZ', '上海': 'SHA', '上海(浦东国际机场)': 'PVG', '上海(虹桥国际机场)': 'SHA', '沈阳': 'SHE',
    '石河子': 'SHF', '石家庄': 'SJW', '上饶': 'SQD', '三明': 'SQJ', '汕头': 'SWA', '三亚': 'SYX', '深圳': 'SZX', '十堰': 'WDS',
    '邵阳': 'WGN', '松原': 'YSQ', '台州': 'HYN', '台中': 'RMQ', '塔城': 'TCG', '腾冲': 'TCZ', '铜仁': 'TEN', '通辽': 'TGO',
    '天水': 'THQ', '吐鲁番': 'TLQ', '通化': 'TNH', '台南': 'TNN', '台北': 'TPE', '天津': 'TSN', '台东': 'TTT', '唐山': 'TVS',
    '太原': 'TYN', '泰州': 'YTY', '五大连池': 'DTU', '乌兰浩特': 'HLH', '乌兰察布': 'UCB', '乌鲁木齐': 'URC', '潍坊': 'WEF', '威海': 'WEH',
    '文山': 'WNH', '温州': 'WNZ', '乌海': 'WUA', '武汉': 'WUH', '武夷山': 'WUS', '无锡': 'WUX', '梧州': 'WUZ', '万州': 'WXN',
    '乌拉特中旗': 'WZQ',
    '兴义': 'ACX', '香格里拉': 'DIG', '夏河': 'GXH', '香港': 'HKG', '西双版纳': 'JHG', '新源': 'NLT', '西安': 'SIA', '咸阳': 'SIA',
    '忻州': 'WUT', '信阳': 'XAI', '襄阳': 'XFN', '西昌': 'XIC', '锡林浩特': 'XIL', '厦门': 'XMN', '西宁': 'XNN', '徐州': 'XUZ',
    '延安': 'ENY', '银川': 'INC', '伊春': 'LDS', '永州': 'LLF', '榆林': 'UYN', '宜宾': 'YBP', '运城': 'YCU', '宜春': 'YIC',
    '宜昌': 'YIH', '伊犁': 'YIN', '伊宁': 'YIN', '义乌': 'YIW', '营口': 'YKH', '延吉': 'YNJ', '烟台': 'YNT', '盐城': 'YNZ',
    '扬州': 'YTY', '玉树': 'YUS', '岳阳': 'YYA', '郑州': 'CGO', '张家界': 'DYG', '芷江': 'HJJ', '舟山': 'HSN', '扎兰屯': 'NZL',
    '张掖': 'YZY', '昭通': 'ZAT', '湛江': 'ZHA', '中卫': 'ZHY', '张家口': 'ZQZ', '珠海': 'ZUH', '遵义': 'ZYI',
}


def test(url):
    reptile = Spider()
    reptile.savePaperByUrl(url)


if __name__ == '__main__':
    echo()
    # test(url="https://xueshu.baidu.com/usercenter/paper/show?paperid=ddb0dbbf0c74c23f793dd7fd85ce90c4&site=xueshu_se&hitarticle=1")
