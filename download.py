#encoding=utf-8
import time
import crawler
from datetime import datetime
#  from multiprocessing import Pool
import os
import threading
import gevent
from gevent.pool import Pool
from gevent import monkey
monkey.patch_all()



def get_city_keyword(citys, keywords):
    for city in citys:
        for key in keywords:
            yield city, key


def main():
    citys = ['北京', '上海', '广州', '深圳']
    keywords = ['python']
    while True:
        print 'Run task', datetime.now()
        start = datetime.now()
        start1 = time.time()
        '''
        process method and thread method
        p = Pool()
        for city, keyword in get_city_keyword(citys, keywords):
            p.apply_async(crawler.get_data_jobs, args=(city, keyword))
            t = threading.Thread(target=crawler.get_data_jobs, args=(city, keyword))
            t.start()
            t.join()
        p.close()
        p.join()
        '''
        pool = Pool(1000)
        for city, keyword in get_city_keyword(citys, keywords):
            pool.spawn(crawler.get_data_jobs, city, keyword)
        pool.join()
        end = datetime.now()
        end1 = time.time()
        tasks = end1 - start1
        print 'End task', datetime.now()
        print 'tasks time', tasks
        time.sleep(7200)


if __name__ == '__main__':
    main()
