import requests
from bs4 import BeautifulSoup
import selenium
import re
import sqlite3
from contextlib import closing
import util


def main():
    trend_datas = util.search_twitter_trend()
    for data in trend_datas:
        print(data)


if __name__ == '__main__':
    main()
