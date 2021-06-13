import re
import datetime
import time
import sys
import requests
from bs4 import BeautifulSoup
import selenium
import wikipedia
import sqlite3
from contextlib import closing
from janome.tokenizer import Tokenizer
from PIL import Image
import pyocr
import pyocr.builders
import alkana.main as alk


"""
form class=gsc-search-box gsc-search-box-tools
    input name=search title=検索
    button class=gsc-search-button gsc-search-button-v2
"""
DIS_ALLOW_URL = (
    re.compile("https://www.youtube.com/.*"),
    re.compile("https://twitter.com/.*")
)

TWITTER_TREND_DATA = "twittertrend.db"
NIJISANJI_DATA = "nijisanji.db"
VTUBER_DATA = "vtuber.db"


def check_url(url):
    flag = False
    for pattern in DIS_ALLOW_URL:
        if pattern.match(url):
            flag = True
    return flag


def search_twitter_trend():
    trend_url = "https://twittrend.jp/"
    response = requests.get(trend_url)
    container = BeautifulSoup(response.content, "html.parser")

    timeline = container.find("div", class_="box box-solid")
    container = timeline.find("ul", class_="list-unstyled")
    trend_words = container.find_all("li")
    container = []

    for trend_data in trend_words:
        trend_word = trend_data.find("a")
        if trend_word is not None:
            if trend_word.string[0] == "#":
                container.append(trend_word.string[1:])
            else:
                container.append(trend_word.string)

    return container


def search_wiki(search_text):
    """
    TODO : 表記揺れの対策を行う
    https://ja.wikipedia.org/wiki/%E7%89%B9%E5%88%A5:%E3%81%8A%E3%81%BE%E3%81%8B%E3%81%9B%E8%A1%A8%E7%A4%BA
    :param search_text:
    :return:
    """
    wikipedia.set_lang("ja")
    response_string = ""

    search_response = wikipedia.search(search_text)

    if len(search_response) > 0:
        try:
            for res in search_response:
                wiki_page = wikipedia.page(res)
                if search_text in wiki_page.title:
                    return wiki_page.summary
                time.sleep(1)
            return None
        except Exception as e:
            print(e)
            return None
    else:
        print("{} は登録されていません".format(search_text))
        return None


def search_vtuber():
    vtuber_matome = "https://vtuber.atodeyo.com/"
    response = requests.get(vtuber_matome)
    soup = BeautifulSoup(response.content, "html.parser")

    timeline = soup.find("div", class_="timeline")
    for article in timeline.find_all("div"):
        time_data = article.find("p", class_="time")
        print(time_data.span.text)
        print(time_data.text[time_data.text.find("</span>"):])
        site_data = article.find("p", class_="article")
        print(site_data.a.text)
        print(site_data.a.get("href"))


def token_analytics(sentences):
    """
    文章やリストの中から名詞を返す
    :param sentences:
    :return:
    """
    tokenizer = Tokenizer()
    pattern_noun = re.compile(".*名詞.*")
    container = []

    if type(sentences) is str:
        for token in tokenizer.tokenize(sentences):
            token = str(token)
            if pattern_noun.match(token):
                container.append(token[0:token.find("名詞") - 1])
    if type(sentences) is list:
        for sentence in sentences:
            for token in tokenizer.tokenize(sentence):
                token = str(token)
                if pattern_noun.match(token):
                    container.append(token[0:token.find("名詞") - 1])

    return container


def controll_db(
        dbname, insert_data,
        query="insert into twitter_trend(word, summary, insert_date, Nouns) values(?, ?, ?, ?)"
):
    """
        query = "create table nijisanji(word string primary key, summary string, insert_date date)"
        query = "create table twitter_trend(word string primary key, summary string, insert_date date, nouns string)"
    :param dbname:
    :param insert_data:
    :param query:
    :return:
    """
    with closing(sqlite3.connect(dbname)) as conn:
        c = conn.cursor()
        check_unique_query = "select word from twitter_trend"
        inputed_word = c.execute(check_unique_query)
        flag = False
        for word in inputed_word:
            if insert_data[0] in word:
                flag = True
        if flag:
            pass
        else:
            c.execute(query, insert_data)
            conn.commit()


def search_db():
    dbname = TWITTER_TREND_DATA
    with closing(sqlite3.connect(dbname)) as conn:
        c = conn.cursor()
        query = "select * from twitter_trend"
        data = c.execute(query)
        for data_ in data:
            print(data_)
            nouns = str(token_analytics(data_[0]))
            query = ""  # TODO


def search_summary(search_text):
    pass


# TODO : 画像読み取り
def read_text():
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)

    tool = tools[0]
    print("Will use tool '%s'" % (tool.get_name()))

    txt = tool.image_to_string(
        # 文字認識対象の画像image.pngを用意する
        Image.open("./image.png"),
        lang="jpn",
        builder=pyocr.builders.TextBuilder(tesseract_layout=6)
    )

    print(txt)


def debug():
    # trend_words = search_twitter_trend()
    # for word in trend_words:
    #     controll_db(TWITTER_TREND_DATA, (word, None, datetime.datetime.today(), None))
    search_db()


if __name__ == '__main__':
    debug()
