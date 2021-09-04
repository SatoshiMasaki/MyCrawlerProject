import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd

"""
Nijisanji_dic.csv
    ライバー名
    ライバー間の呼び方
    コラボ名
    (語録)
"""
#  TODO 現状上三つを登録しているものの、基本的な単語すら反応しないので要改善だ。

NIJISANJI_WIKI = "https://wikiwiki.jp/nijisanji/"
NIJISANJI_COLAB = "https://wikiwiki.jp/nijisanji/%E3%82%B3%E3%83%A9%E3%83%9C%E4%B8%80%E8%A6%A7%E8%A1%A8"
# NIJISANJI_WORDS = "https://wikiwiki.jp/nijisanji/" \
#                   "%E3%81%AB%E3%81%98%E3%81%95%E3%82%93%E3%81%98%E8%AA%9E%E9%8C%B2%E9%9B%86"
NIJISANJI_HOWTOCALL = "https://wikiwiki.jp/nijisanji/" \
                      "%E3%83%A1%E3%83%B3%E3%83%90%E3%83%BC%E9%96%93%E3%81%AE%E5%91%BC%E3%8" \
                      "1%B3%E6%96%B9%E4%B8%80%E8%A6%A7"


def create_user_dic(words, dic_name):
    """
      TASK: 指定された単語群からJanome指定のユーザー辞書.csvファイルを作成する
      words: []string -> 辞書に登録したい単語群
      dic_name: string -> __.csvに該当するファイル名
      return void
    """
    df = words_to_df(words)
    df = to_janome_csv_style(df)
    save_df_to_csv(df, dic_name)


def words_to_df(words):
    """
      TASK: 単語リストをpandas.DataFrame形式に変換する
      wrods: []string -> 対象の単語群
      return pandas.DataFrame
    """
    to_df_list = [[w] for w in words]
    return pd.DataFrame(words, columns=["単語"])


def to_janome_csv_style(df):
    """
      TASK: 読み込まれたdfをjanomeが指定するユーザー辞書.csv形式に変換する
      df: pandas.DataFrame -> 単語リストから生成されたdf
      return pandas.DataFrame
    """
    return df.assign(
        a=df.pipe(lambda df: -1),
        b=df.pipe(lambda df: -1),
        c=df.pipe(lambda df: 1000),
        d=df.pipe(lambda df: "名詞"),
        e=df.pipe(lambda df: "一般"),
        f=df.pipe(lambda df: "*"),
        g=df.pipe(lambda df: "*"),
        h=df.pipe(lambda df: "*"),
        i=df.pipe(lambda df: "*"),
        j=df.pipe(lambda df: df["単語"]),
        k=df.pipe(lambda df: "*"),
        l=df.pipe(lambda df: "*"),
    )


def save_df_to_csv(df, file_name):
    """
      TASK: dfを.csv形式で保存する
      df: pandas.DataFrame -> to_janome_csv_style()の戻り値のdf
      file_name: ファイルの保存名(拡張子は含まない)
      return void
    """
    df.to_csv(f"{file_name}.csv", header=False, index=False, encoding="cp932")


def getLiverName(driver):
    words = []
    driver.get(NIJISANJI_WIKI)
    time.sleep(5)

    th = driver.find_element_by_xpath(
        "//div[@class='column-left']/div[@id='menubar']/"
        "hr[@class='full_hr']/following-sibling::div[@class='fold-container  clearfix']"
    )

    button = th.find_element_by_xpath("button")
    button.click()
    time.sleep(1)

    th = th.find_elements_by_xpath("div[@class='fold-content visible-on-open']/div")

    for tag in th:
        time.sleep(1)
        li_tags = tag.find_elements_by_xpath(
            "div[@class='fold-content visible-on-open']/ul/li"
        )
        for li in li_tags:
            print(li.text)
            if len(li.find_elements_by_xpath("span")) > 0:
                words.append(li.find_element_by_xpath("span/a").get_attribute("title"))
            else:
                words.append(li.find_element_by_xpath("a").get_attribute("title"))
    print(words)

    return words


def getUnitName(driver):
    words = []
    driver.get(NIJISANJI_COLAB)
    time.sleep(5)

    rows = driver.find_elements_by_xpath(
        "//table[@role='grid']/tbody/tr[@role='row']"
    )

    for row in rows:
        time.sleep(1)
        th = row.find_element_by_xpath("th")
        text = th.text

        if len(th.find_elements_by_xpath("ruby")) > 0 and "*" in text:
            print(text[0:text.find("\n")])
            words.append(text[0:text.find("\n")])
        elif len(th.find_elements_by_xpath("ruby")) > 0:
            print(text[0:text.find("\n")])
            words.append(text[0:text.find("\n")])
        elif "*" in text:
            print(text[0:text.find("*")])
            words.append(text[0:text.find("*")])
        else:
            print(text)
            words.append(text)
        time.sleep(1)

    print(words)
    return words


def getHowToCall(driver):
    words = []
    driver.get(NIJISANJI_HOWTOCALL)
    time.sleep(5)

    rows = driver.find_elements_by_xpath(
        "//div[@class='column-center clearfix']/div[@id='body']/"
        "div[@id='content']/div[@class='fold-container  clearfix']"
    )

    for row in rows:
        print("--------")
        time.sleep(1)
        row.find_element_by_xpath("button[@class='fold-toggle-button hidden-on-open']").click()
        time.sleep(1)
        trs = row.find_elements_by_xpath("div[@class='fold-content visible-on-open']/div/table/tbody/tr")
        del trs[0]

        for i, tr in enumerate(trs):
            container = tr.find_element_by_xpath("td")
            container = container.text

            if container.find("→") and container.find("、"):
                containers = re.split("[→、]", container)
                for data in containers:
                    if "*" in data:
                        print(data[0:data.find("*")])
                        words.append(data[0:data.find("*")])
                    else:
                        print(data)
                        words.append(data)
            elif container.find("、"):
                containers = container.split("、")
                for data in containers:
                    if "*" in data:
                        print(data[0:data.find("*")])
                        words.append(data[0:data.find("*")])
                    else:
                        print(data)
                        words.append(data)
            elif container.find("→"):
                containers = container.split("→")
                for data in containers:
                    if "*" in data:
                        print(data[0:data.find("*")])
                        words.append(data[0:data.find("*")])
                    else:
                        print(data)
                        words.append(data)
            else:
                if "*" in container:
                    print(container[0:container.find("*")])
                    words.append(container[0:container.find("*")])
                else:
                    print(container)
                    words.append(container)
    print(words)
    return words


def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path="chromedriver.exe", options=chrome_options)
    words = getHowToCall(driver)

    try:
        cp932_words = []
        for word in words:
            cp932_words.append(word.encode("cp932", "ignore").decode("cp932", "ignore"))
        create_user_dic(cp932_words, "Nijisanji_dic")
    except Exception as e:
        print(e)


# def debug():
    # with open("datas/Nijisanji_dic.csv", "rt") as f:
        # datas = f.readlines()

    # datas = list(set(datas))

    # with open("datas/Nijisanji_dic.csv", "wt") as f:
    #     for data in datas:
    #         if data.count(",") == 12:
    #             f.write(data)


if __name__ == '__main__':
    pass
