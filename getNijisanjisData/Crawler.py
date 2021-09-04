import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from janome.tokenizer import Tokenizer
from janome.analyzer import Analyzer
from janome.tokenfilter import CompoundNounFilter

BASE_URL = "https://comment2434.com/"
GET_COMMENT_URL = "https://comment2434.com/comment/"
USER_DIC_PATH = "datas/Nijisanji_dic.csv"


def searchByKeywords(driver, keyword, *options):
    """
    TODO 引数の最適化
    :param driver: selenium driver
    :param keyword: search query
    :param options: (channel, mode, since_date, until_date, lower_comments)
    :return:
    """
    driver.find_element_by_id("keyword_search")
    form_tag = driver.find_element_by_id("form")

    input_tag = form_tag.find_element_by_xpath("p/input")
    input_tag.send_keys(keyword)

    if options:
        arg_size = len(options)

        if options[0]:
            channel_name = re.compile(".*{}.*".format(options[0]))
            channel_tags = form_tag.find_elements_by_xpath("p[2]/select/option")
            channel_id = None
            for channel in channel_tags:
                if channel_name.match(channel.text):
                    channel_id = channel.get_attribute("value")
                    break
            if channel_id:
                form_tag.find_element_by_xpath("p[2]/select/option[@value='{}']".format(channel_id)).click()
        if arg_size >= 2 and options[1]:
            low_speed = re.compile(".*低速.*")
            mode_select = form_tag.find_elements_by_xpath("ul/li")
            for mode in mode_select:
                element = mode.find_element_by_xpath("label/input")
                if low_speed.match(element.text):
                    element.click()
                    break
        if arg_size >= 3 and options[2]:
            pass
        if arg_size >= 4 and options[3]:
            pass
        if arg_size >= 5 and options[4]:
            least_count = driver.find_element_by_xpath("//input[@name='least_count']")
            least_count.send_keys(str(options[4]))

    time.sleep(2)

    form_tag.find_element_by_id("start_button").click()

    time.sleep(10)

    re_search_flag = False  # TODO コメントの再検索
    re_search_pattern = re.compile(".*さらに過去を検索.*")
    response_data = driver.find_element_by_xpath("//*[@id='loading']").text
    if re_search_pattern.match(response_data):
        re_search_flag = True

    page_switch_button = driver.find_element_by_xpath(
        "//nav[@aria-label='Page navigation example']/ul"
    )

    videos = page_switch_button.find_elements_by_xpath(
        "parent::nav/parent::div/following-sibling::div[@class='row']"
    )

    container = []
    for div in videos:
        archive_data = div.find_elements_by_xpath("div[2]/*")

        video_name = archive_data[0].text
        channel_name = archive_data[1].text
        live_date = archive_data[2].text

        div.find_element_by_xpath("div[2]/p[3]/a").click()
        time.sleep(5)

        url = driver.find_element_by_xpath("/html/body/div/div[2]/div[2]/div[1]/a").get_attribute("href")
        comment_data = driver.find_elements_by_xpath("/html/body/div/div[2]/form/div[position() > 1]")
        comments = []

        for comment in comment_data:
            comments.append(comment.find_element_by_xpath("div[2]").text)

        # TODO データの扱い方を考える
        container.append((video_name, channel_name, live_date, url, comments))

    time.sleep(500)


def tokenAnalytics(sentence):
    """
    :param sentence:
    :return: (surface, base_form, part_of_speech)
    """
    tokenizer = Tokenizer(USER_DIC_PATH, udic_enc="cp932")
    datas = []
    if type(sentence) is str:
        for token in tokenizer.tokenize(sentence):
            surface = token.surface
            base_form = token.base_form
            part_of_speech = token.part_of_speech.split(",")
            asterisk = []
            for i, noun in enumerate(part_of_speech):
                if noun == "*":
                    asterisk.append(i)
            for i in reversed(asterisk):
                del part_of_speech[i]
            print("単語 : ", surface)
            print("基本形 : ", base_form)
            print("品詞 : ", part_of_speech)
            datas.append((surface, base_form, part_of_speech))
    elif type(sentence) is list:
        for data in sentence:
            for token in tokenizer.tokenize(data):
                surface = token.surface
                base_form = token.base_form
                part_of_speech = token.part_of_speech.split(",")
                print("単語 : ", surface)
                print("基本形 : ", base_form)
                print("品詞 : ", part_of_speech)
                datas.append((surface, base_form, part_of_speech))
    return datas


def main():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    search_word = "カールタ"
    # search_word = input("検索ワードを入れて下さい : ")

    driver = webdriver.Chrome(executable_path="chromedriver.exe", options=chrome_options)
    driver.get(GET_COMMENT_URL)
    time.sleep(5)

    searchByKeywords(driver, search_word, "山神", True)


if __name__ == '__main__':
    tokenAnalytics("MTGやってると人の心失うからしゃーない")
    a = Analyzer(token_filters=[CompoundNounFilter()])

    text = "明日の配信告知です！今日じゃないので注意！ホロライブIDからレイネさんが来てくれます！" \
           "インドネシア語教えてくれるかな〜(∩´∀`∩)マシュマロ送ってね！"

    for token in a.analyze(text):
        print(token.surface)
