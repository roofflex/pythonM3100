import requests
import math
from bs4 import BeautifulSoup
from sqlalchemy.ext.declarative import declarative_base
from bottle import route, run, template
from bottle import redirect, request
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer
from sqlalchemy import create_engine


def get_news(page):
    tbl_list = page.table.findAll('table')
    news = tbl_list[1]
    titles = news.findAll('a', 'storylink')
    title_list = [titles[i].text for i in range(len(titles))]
    links_list = [title.attrs['href'] for title in titles]
    points = news.findAll('span', class_='score')
    points_list = [point.text for point in points]
    authors = news.findAll('a', 'hnuser')
    authors_list = [authors[i].text for i in range(len(authors))]
    news_inf = news.findAll('td', class_='subtext')
    comments_list = [inf.text.split('|')[4] for inf in news_inf]
    for i in range(len(comments_list)):
        if comments_list[i].find('comment') == -1:
            comments_list[i] = 0
        else:
            comments_list[i], _ = comments_list[i].split()
            comments_list[i] = int(comments_list[i])
        points_list[i], _ = points_list[i].split()
        points_list[i] = int(points_list[i])
    sorted_news = []
    for i in range(len(titles)):
        sorted_news.append({'author': authors_list[i],
                            'comments': comments_list[i],
                            'points': points_list[i],
                            'title': title_list[i],
                            'url': links_list[i]})
    return sorted_news


Base = declarative_base()
Base1 = declarative_base()


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)


class Word(Base1):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True)
    word = Column(String)
    num_word = Column(Integer)
    author = Column(String)
    num_auth = Column(Integer)
    url = Column(String)
    num_url = Column(Integer)
    label = Column(String)


engine = create_engine("sqlite:///news.db")
Base.metadata.create_all(bind=engine)
engine1 = create_engine("sqlite:///Words.db")
Base.metadata.create_all(bind=engine1)
session = sessionmaker(bind=engine)
session1 = sessionmaker(bind=engine1)
s = session()
s1 = session1()

news_list = []
for i in range(1):
    r = requests.get("https://news.ycombinator.com/newest?" + 'i*30+1')
    page = BeautifulSoup(r.text, 'html.parser')
    news_list += get_news(page)

for i in range(len(news_list)):
    one = News(title=news_list[i]['title'],
               author=news_list[i]['author'],
               url=news_list[i]['url'],
               comments=news_list[i]['comments'],
               points=news_list[i]['points'])
    s.add(one)
    s.commit()



@route('/add_label/', method='GET')
def add_label():
    label = request.GET.get('label').strip()
    id1 = request.GET.get('id').strip()
    s = session()
    record = s.query(News).filter(News.id == id1)
    record[0].label = label
    s.commit()
    redirect('/news')

labels = ['good', 'maybe', 'never']

@route('/')
@route('/news')
def new_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=rows)


@route('/update_news')
def update_news():
    r = requests.get('https://news.ycombinator.com/newest')
    news_list = get_news(r.text)
    s = session()
    for n in news_list:
        rows = s.query(News).filter(News.author == n['author']).filter(News.title == n['title']).all()
        if rows == []:
            news = News(**n)
            s.add(news)
            s.commit
    redirect('/news')


# run(host='localhost', port=8080)


def possibility(label):
    num_of_all = len(s.query(News).filter(News.label != None).all())
    label_rate = len(s.query(News).filter(News.label == label).all())
    result = label_rate / num_of_all
    return result


def possibility_author(label, author):
    num_of_all = len(s.query(News).filter(News.label == label).filter(News.author != None).all())
    author_rate = s1.query(Word).filter(Word.label == label).filter(Word.author == author).first()
    try:
        return author_rate.num_auth / num_of_all
    except AttributeError:
        return 1


def possibility_url(label, url):
    num_of_all = len(s.query(News).filter(News.label == label).filter(News.url != None).all())
    url_rate = s1.query(Word).filter(Word.label == label).filter(Word.url == url).first()
    try:
        return url_rate.num_url / num_of_all
    except AttributeError:
        return 1


def possibility_word(label, word_):
    num_of_all = 0
    query = s1.query(Word).filter(Word.label == label).filter(Word.word != None).all()
    for word in query:
        num_of_all += word.num_word
    word_rate = s1.query(Word).filter(Word.label == label).filter(Word.word == word_).first()
    try:
        return word_rate.num_word / num_of_all
    except AttributeError:
        return 1

def classificator():
    un_news = s.query(News).filter(News.label == None).all()
    for news in un_news:
        label_count = {'good': 0,
                      'maybe': 0,
                      'never': 0}
        for label in labels:
            rate_auth = math.log(possibility_author(label, news.author))
            rate_word = 0
            words = [word for word in news.title.split()]
            for word in words:
                rate_word += math.log(possibility_word(label, word))
            rate_url = math.log(possibility_url(label, news.url))
            label_count[label] = rate_auth + rate_url + rate_word + possibility(label)
        max = -1000000000
        for label in label_count:
            if label_count[label] > max:
                max = label_count[label]
                key = label
        if key == 'good':
            news.label = 'good!'
        elif key == 'maybe':
            news.label = 'maybe!'
        else:
            news.label = 'never!'
        s.commit()

classificator()

@route('/')
@route('/news1')
def new_list1():
    s = session()
    rows1 = s.query(News).filter(News.label == 'good!').all()
    rows2 = s.query(News).filter(News.label == 'maybe!').all()
    rows3 = s.query(News).filter(News.label == 'never!').all()
    return template('news_template1.tpl', rows1=rows1, rows2=rows2, rows3=rows3)

run(host='localhost', port=8080)
