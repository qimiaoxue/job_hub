# encoding=utf-8
import requests
import json
import time
from pymongo import MongoClient


class Crawler(object):

    def get_url(self):
        return 'https://www.lagou.com/jobs/positionAjax.json'

    def get_headers(self):
        return {
            "Origin": "https://www.lagou.com",
            "Host": "www.lagou.com",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "X-Anit-Forge-Token": "None",
            "X-Anit-Forge-Code": "0",
            "Referer": "https://www.lagou.com/jobs/list_python?labelWords=sug&fromSearch=true&suginput=py",
            "Content-Length": "25",
            "Connection": "keep-alive",
        }

    def get_post_data(self, page_num, keyword):
        if str(page_num) == '1':
            first = 'true'
        else:
            first = 'false'
        return {
            'first': first,
            'pn': str(page_num),
            'kd': keyword,
        }

    def get_params(self, city):
        return {
            'city': city,
            'needAddtionalResult': 'false',
        }

    def get_response(self, city, keyword, page_num):
        resp = requests.post(
            url=self.get_url(),
            data=self.get_post_data(page_num, keyword),
            params=self.get_params(city),
            headers=self.get_headers(),
        )
        if resp.status_code == 200:
            json_data = resp.json()
            if json_data['success']:
                return json_data

    def get_json(self, city, keyword, page_num):
        for i in range(1, int(page_num+1)):
            json_data = self.get_response(city, keyword, i)
            if json_data:
                yield json_data

    def get_data(self, json_data):
        results = json_data['content']['positionResult']['result']
        for ele in results:
            yield ele


class Model(object):

    def __init__(self, db, table):
        self._db = db
        self._table = table

    @property
    def client(self):
        return MongoClient()

    @property
    def db(self):
        return self.client[self._db]

    @property
    def table(self):
        return self.db[self._table]


    def save(self, item):
        if self.seen(item):
            pass
        else:
            self.table.insert(item)

    def seen(self, item):
        res = self.table.find(
            {
                u'publisherId': item['publisherId'],
                u'companyId': item['companyId'],
                u'positionId': item['positionId'],
            }
        )
        if res.count() > 0:
            return True


if __name__ == '__main__':
    crawler = Crawler()
    city = '北京'
    keyword = 'python'
    page_num = 100
    db = 'python_jobs_server'
    table = 'jobs'
    model = Model(db, table)
    for json_data in crawler.get_json(city, keyword, page_num):
        time.sleep(2)
        for ele in crawler.get_data(json_data):
            print '-' * 30
            print ele
            print '-' * 30
            model.save(ele)
