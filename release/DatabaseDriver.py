# -*- coding:UTF-8 -*-
import pymysql


class DatabaseDriver:

    def __init__(self, host, port, user, passwd, database_name):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.database_name = database_name
        self.db = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=database_name)  # 打开数据库连接

        self.cursor = self.db.cursor()  # 使用 cursor() 方法创建一个游标对象 cursor

    def insertPapers(self, paperList):
        sql = "INSERT INTO document(title, experts, dtype, documentid, time_, doi, isbn, application_number, cited_quantity, summary, keywords, link, origin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        for item in paperList:
            try:
                self.cursor.execute(sql, (item["title"], ','.join(item["authors"]), item["category"], item["id"],
                                                  item["time"],
                                                  item["DOI"], item["ISBN"], item['patentNumber'],
                                                  item["citedQuantity"],
                                                  item["abstract"], ','.join(item["keywords"]), item["link"], item["source"]))
                self.db.commit()
                print(item)
                print("Insert successfully!")
            except Exception as e:
                self.db.rollback()
                print("Fail:", end="")
                print(e)

    def insertDocument(self, title, authors, category, id, time, DOI, ISBN, patentNumber, citedQuantity, abstract,
                       keywords, link, source):
        sql = "INSERT INTO document(title, experts, dtype, documentid, time_, doi, isbn, application_number, cited_quantity, summary, keywords, link, origin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # 使用 execute()  方法执行 SQL 查询
        try:
            self.cursor.execute(sql, (
            title, ','.join(authors), category, id, time, DOI, ISBN, patentNumber, citedQuantity, abstract,
            ','.join(keywords), link, source))
            self.db.commit()
            # print("Insert successfully!")
            return True
        except Exception as e:
            self.db.rollback()
            # print("Fail:", end="")
            # print(e)
            return str(e)
        # 关闭数据库连接
        # self.db.close()

    def getPageNumber(self, keyword):
        sql = "SELECT quantity FROM paper_spider_record WHERE name= %s"
        # 使用 execute()  方法执行 SQL 查询
        try:
            self.cursor.execute(sql, keyword)
            results = self.cursor.fetchall()
            if len(results) == 0:
                return 0
            for row in results:
                return row[0]
        except Exception as e:
            print("Fail:", end="")
            print(e)

    def keywordExists(self, keyword):
        sql = "SELECT name FROM paper_spider_record WHERE name= %s"
        # 使用 execute()  方法执行 SQL 查询
        try:
            self.cursor.execute(sql, keyword)
            results = self.cursor.fetchall()
            if len(results) == 0:
                return False
            else:
                return True
        except Exception as e:
            print("关键词数据库记录查询失败:", end="")
            print(e)

    def updateKeyword(self, keyword):
        sql = "SELECT name FROM paper_spider_record WHERE name= %s"
        # 使用 execute()  方法执行 SQL 查询
        try:
            self.cursor.execute(sql, keyword)
            results = self.cursor.fetchall()
            if len(results) == 0:
                sql = "INSERT INTO paper_spider_record(name) VALUES (%s)"
                self.cursor.execute(sql, keyword)
            self.db.commit()
            print("Update record successfully!")
        except Exception as e:
            self.db.rollback()
            print("数据库更新关键词失败:", end="")
            print(e)

    def setPageNumber(self, keyword, number):
        sql = "SELECT quantity FROM paper_spider_record WHERE name= %s"
        # 使用 execute()  方法执行 SQL 查询
        try:
            self.cursor.execute(sql, keyword)
            results = self.cursor.fetchall()
            if len(results) == 0:
                sql = "INSERT INTO paper_spider_record(name, quantity) VALUES (%s, %s)"
                self.cursor.execute(sql, (keyword, number))
            else:
                sql = "UPDATE paper_spider_record SET quantity = %s WHERE name = %s"
                self.cursor.execute(sql, (number, keyword))
            self.db.commit()
            print("Update record successfully!")
        except Exception as e:
            self.db.rollback()
            print("Fail:", end="")
            print(e)


if __name__ == '__main__':
    databaseDriver = DatabaseDriver(host="49.232.157.22", port=3306, user="BUAA", passwd="BUAA1821",
                                    database_name="BUAA")
    databaseDriver.updateKeyword('啊')
