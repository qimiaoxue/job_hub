from flask import Flask
from flask import request
from flask import render_template
from flask_bootstrap import Bootstrap
from pymongo import MongoClient
from datetime import datetime


app = Flask(__name__)
Bootstrap(app)


class PostModel(object):

    __db_str__ = 'python_jobs_server'
    __table_str__ = 'jobs'
    __table__ = MongoClient()[__db_str__][__table_str__]
    __posts_per_page__ = 9

    @classmethod
    def get_posts_by_now(cls):
        now = str(datetime.now())
        return cls.__table__.find({'createTime': {'$lt': now}})

    @classmethod
    def get_posts_by_range(cls, start, stop):
        for post in cls.get_posts_by_now()[start:stop]:
            post = cls.handle_logo_url(post)
            yield cls.handle_company_label(post)

    @classmethod
    def get_pages_num(cls):
        return cls.get_posts_by_now().count() / cls.__posts_per_page__ + 1

    @classmethod
    def get_posts_of_page(cls, num):
        num = int(num)
        return list(cls.get_posts_by_range(
            (num-1)*cls.__posts_per_page__,
            num*cls.__posts_per_page__
        ))

    @classmethod
    def handle_logo_url(cls, post):
        host = 'https://www.lgstatic.com/thumbnail_200x200/'
        path = post['companyLogo']
        stub = '{host}{path}'
        post['companyLogo'] = stub.format(host=host, path=path)
        return post

    @classmethod
    def handle_company_label(cls, post):
        label = post['companyLabelList']
        if label is None:
            post['companyLabelList'] = ''
        else:
            post['companyLabelList'] = ', '.join(label)
        return post


@app.route('/post')
def index():
    page = request.args.get('page', '1')
    page = int(page)
    max_page_num = PostModel.get_pages_num()
    if page < 1:
        page = 1
    if page > max_page_num:
        page = max_page_num
    per_page = 8
    page_num_range = [(page-1) / per_page * per_page + i + 1 for i in range(per_page)]
    posts = PostModel.get_posts_of_page(int(page))
    return render_template(
        'base.html', posts=posts, page_num_range=page_num_range)


if __name__ == '__main__':
    app.run(debug=True)
