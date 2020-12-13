# -*- coding:UTF-8 -*-
import hashlib
import re
import threading
import urllib
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup
from pinyin import pinyin
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

from DatabaseDriver import DatabaseDriver


class AuthorParser(threading.Thread):
    def __init__(self, link, databaseDriver, lock):
        super().__init__()
        self.link = link
        self.databaseDriver = databaseDriver
        self.lock = lock
        self.paperList = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.183 Safari/537.36"}

    def run(self):
        try:
            request = urllib.request.Request(url=self.link, headers=self.headers)
            response = urllib.request.urlopen(request)
            authorInformation = response.read().decode("utf-8")
            bs = BeautifulSoup(authorInformation, "html.parser")
            self.saveAuthor(bs)
            self.databaseDriver.insertPapers(self.paperList)
        finally:
            self.lock.release()

    def getAuthorName(self, person_baseinfoDive):
        try:
            name = person_baseinfoDive.select("div[class='p_name']", limit=1)[0].string
        except:
            # try:
            #     name = main_info.h3.span.string
            # except:
            name = ""
        return name.lstrip().rstrip().replace('\n', '').replace('\r', '')

    def getAffiliate(self, person_baseinfoDive):
        try:
            affiliate = person_baseinfoDive.select("div[class='p_affiliate']", limit=1)[0].string
        except:
            # try:
            #     name = main_info.h3.span.string
            # except:
            affiliate = ""
        return affiliate.lstrip().rstrip().replace('\n', '').replace('\r', '')

    def getDomain(self, person_baseinfoDive):
        try:
            domain = person_baseinfoDive.select("div[class='person_domain person_text']", limit=1)[0].a.string
        except:
            # try:
            #     name = main_info.h3.span.string
            # except:
            domain = ""
        return domain.lstrip().rstrip().replace('\n', '').replace('\r', '')

    def getExpertID(self, name, affiliate):
        return 'EX-' + hashlib.md5(str(name + ',' + affiliate).encode('utf-8')).hexdigest()

    def saveAuthor(self, bs):
        person_baseinfoDive = bs.select("div[class='person_baseinfo']", limit=1)[0]
        name = self.getAuthorName(person_baseinfoDive)
        affiliate = self.getAffiliate(person_baseinfoDive)
        item = {
            "name": name,
            "affiliate": affiliate,
            "id": self.getExpertID(name, affiliate),
            "domain": self.getDomain(person_baseinfoDive),
        }
        self.paperList.append(item)
