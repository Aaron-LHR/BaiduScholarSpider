import json
import urllib.request

url = "https://kns.cnki.net/KNS8/Brief/GetGridTableHtml"
headers = {

    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",

}
data = {

    "QueryJson": {"Platform": "", "DBCode": "SCDB", "KuaKuCode": "CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CJFN,CCJD",
                  "QNode": {"QGroup": [{"Key": "Subject", "Title": "", "Logic": 1, "Items": [
                      {"Title": "主题", "Name": "SU", "Value": "计算机", "Operate": "%=", "BlurType": ""}],
                                        "ChildItems": []}]}},

}
# data = json.dumps(data).encode("utf-8")
data = urllib.parse.urlencode(data).encode('utf-8')
# print(data)
request = urllib.request.Request(url=url, data=data, headers=headers)
try:
    response = urllib.request.urlopen(request)
    html = response.read().decode("utf-8")
    print(html)
except Exception as e:
    print(str(e))

# with open("douban.html", mode="w", encoding="utf-8") as file:
#     file.write(html)
