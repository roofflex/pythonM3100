from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)

engine = create_engine("sqlite:///news.db")
Base.metadata.create_all(bind=engine)
session = sessionmaker(bind=engine)
s = session()

Base1 = declarative_base()

class Word(Base1):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True)
    word= Column(String)
    num_word = Column(Integer)
    author = Column(String)
    num_auth = Column(Integer)
    url = Column(String)
    num_url = Column(Integer)
    label = Column(String)

engine1 = create_engine("sqlite:///words.db")
Base1.metadata.create_all(bind=engine1)

session1 = sessionmaker(bind=engine1)
s1 = session1()

def word_to_number(label):
    num_of_words = {}
    num_of_authors = {}
    num_of_urls = {}
    a = s.query(News).filter(News.label == '{}'.format(label)).all()
    for string in a:
        for word in string.title.split():
            try:
                num_of_words[word] += 1
            except:
                num_of_words[word] = 1
        try:
            num_of_authors[string.author] += 1
        except:
            num_of_authors[string.author] = 1
        try:
            num_of_urls[string.url] += 1
        except:
            num_of_urls[string.url] = 1
    for i in num_of_words:
        one = Word(word = i , num_word = num_of_words[i], label = label)
        s1.add(one)
        s1.commit()
    for i in num_of_urls:
        one = Word(url=i, num_url=num_of_urls[i], label = label)
        s1.add(one)
        s1.commit()
    for i in num_of_authors:
        one = Word(author=i, num_auth=num_of_authors[i], label = label)
        s1.add(one)
        s1.commit()

labels = ['good', 'maybe', 'never']
for i in labels:
    word_to_number(i)




