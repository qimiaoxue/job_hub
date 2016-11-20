# encoding=utf-8
from send_mail import MailSender
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


def get_data_jobs(city, keyword, page_num=100):
    """crawl 100 page of lagou in city(beijing) under keyword(python)
    """
    crawler = Crawler()
    db = 'python_jobs_server'
    table = 'jobs'
    model = Model(db, table)
    count = 0
    get_insert_count = 0
    for json_data in crawler.get_json(city, keyword, page_num):
        time.sleep(1)
        num = 0
        for ele in crawler.get_data(json_data):
            if model.seen(ele):
                pass
            else:
                get_insert_count += 1
                insert_jobs.append(ele)
                mail_sender = MailSender()
                from_addr = 'test@sendcloud.org'
                to_addr = '15011272359@163.com'
                subject = get_subject(ele)
                html = get_html(ele)
                mail_sender.send(from_addr, to_addr, subject, html)
            num += 1
        count += num
    print '-' * 30
    print 'get_insert_count:', get_insert_count
    print 'count:', count
    print '-' * 30


def get_subject(ele):
    """
    :param ele: dict
    {
        'job': pass
    }
    """
    city = ele.get('city', 'None')
    position_name = ele.get('positionName', 'Python')
    return '%s %s' % (city, position_name)

def get_html(ele):
    return u"""
<ul>
    <li>{district}</li>
    <li>{companyLabelList}</li>
    <li>{companySize}</li>
    <li>{education}</li>
    <li>{financeStage}</li>
    <li>{industryField}</li>
    <li>{firstType}</li>
    <li>{secondType}</li>
    <li>{jobNature}</li>
    <li>{positionAdvantage}</li>
    <li>{salary}</li>
    <li>{workYear}</li>
</ul>
""".format(**ele)
