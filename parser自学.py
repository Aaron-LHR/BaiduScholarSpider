import re

from bs4 import BeautifulSoup

with open("douban.html", mode="r", encoding="utf-8") as file:
    html = file.read()

bs = BeautifulSoup(html, "html.parser")


# print(bs.title)
# print(bs.title.string)
# print(bs.a.attrs)
# print(bs.head.contents)  # list
# print(bs.find_all("a"))  # list
# print(bs.find_all(re.compile("a")))  # 正则表达式

def name_is_exists(tag):
    return tag.has_attr("name")


# print(bs.find_all(name_is_exists))  #有name属性的所有tag

# print(bs.find_all(id="kw")) # 找id

# print(bs.find_all(class_=True))  # 含有class属性

# print(bs.find_all(re.compile("\d")))    # 标签
# list = bs.find_all(text=re.compile('\\d'), limit=1)  # 文本内容
# list = bs.select("title")   # 标签
# list = bs.select(".xpath-log")  # class
# list = bs.select("#fm") # id
# list = bs.select("div[class='index_new_subject_rank_content']") # 属性
# list = bs.select("div > div >div")  # 嵌套
# list = bs.select("div ~ div")  # 兄弟标签
# list = bs.select("h3[class='t c_font']")
#
# for li in list:
#     print(li.a.attrs['href'])
print(bs.div[""])