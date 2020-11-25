# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

driver = webdriver.Chrome()
driver.get("https://xueshu.baidu.com/")
driver.find_element_by_id("kw").click()
driver.find_element_by_id("kw").clear()
driver.find_element_by_id("kw").send_keys(u"计算机")
driver.find_element_by_id("su").click()
content = driver.page_source.encode('utf-8')
driver.close()
soup = BeautifulSoup(content, 'lxml')
print(soup.select(".sc_content"))
