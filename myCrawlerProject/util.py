import re
import requests
from bs4 import BeautifulSoup
import selenium
import wikipedia
import sqlite3
from contextlib import closing
from janome.tokenizer import Tokenizer


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
    https://ja.wikipedia.org/wiki/%E7%89%B9%E5%88%A5:%E3%81%8A%E3%81%BE%E3%81%8B%E3%81%9B%E8%A1%A8%E7%A4%BA
    :param search_text:
    :return:
    """
    wikipedia.set_lang("ja")
    response_string = ""

    search_response = wikipedia.search(search_text)

    if len(search_response) > 0:
        try:
            wiki_page = wikipedia.page(search_response[0])
            wiki_content = wiki_page.content
            # response_string += wiki_content[0:wiki_content.find("。")]
            # print(response_string)
            print(wiki_page.title)
            print(wiki_page.summary)
            print(wiki_page.url)
            return wiki_page.summary
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
    tokenizer = Tokenizer()
    pattern_noun = re.compile(".*名詞.*")

    for sentence in sentences:
        for token in tokenizer.tokenize(sentence):
            if pattern_noun.match(str(token)):
                print(str(token))


def controll_db(dbname, query):
    with closing(sqlite3.connect(dbname)) as conn:
        c = conn.cursor()
        c.execute(query)
        conn.commit()


if __name__ == '__main__':
    data = search_twitter_trend()
