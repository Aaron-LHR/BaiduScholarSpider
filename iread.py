import json

path = "..\数据\\aminer_papers_0.txt"
file1 = open("data",  mode='a', encoding="utf-8")
with open(path,  mode='r', encoding="utf-8") as file:
    for i in range(300):
        line = file.readline()
        file1.write(line)
