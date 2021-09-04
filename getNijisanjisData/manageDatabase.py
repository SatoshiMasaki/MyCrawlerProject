import sqlite3
from contextlib import closing
from janome.tokenizer import Tokenizer
from janome.analyzer import Analyzer
from janome.tokenfilter import CompoundNounFilter

from ja_stopword_remover.remover import StopwordRemover
from ja_stopword_remover import stop_words

""" 
nijisanji.db
    table video_comment(
        video_id string, video_title string, channel_id string, channel_name string, comment string, 
        upload_date string, indexed integer
    )
    table live_chat(
        video_id string, video_title string, channel_id string,
        channel_name string, chat string, upload_date string, indexed integer
    )
    upload_date: 20xx-x-x の書式
    indexed : 1なら逆インデックス化済み
    
    table word_dict(word string, sentence string, place string, video_id string)
    place : 詳細が保存されているテーブル
    
    table video_information(video_id string, )
    
    
    関連度計算
    fd,t	文書dの中に出現するタームtの頻度（数）
    fq,t	クエリqの中に出現するタームtの頻度（数）
    ft	タームtを1つでも含む文書の数
    Ft	文書の中のtの出現回数
    N	文書数
    n	文書の中でインデックスされるターム数
    
    コサイン類似度は，文書とクエリをタームを次元としたベクトル空間にマップし，文書ベクトルとクエリベクトルの成す角度により，
    文書とクエリの関連度（類似度）を求めます（成す角度が小さければ関連度が高い⁠）⁠。
    またOkapi BM25は，文書がクエリに対して適合かどうかは確率的に決定されるという統計的な原理に基づき，文書とクエリの関連度を求めます。

    検索時にこれらを計算するには，索引の構築時に上記の統計値を計算し保持しておく必要があります。
    実装にはさまざまな方法が考えられますが，たとえばfd,tはポスティングリストの中に埋め込んでおき（※4⁠）⁠，
    ftやFtは辞書と一緒に保存しておくといった方法が考えられます（fq,tは検索時に検索でき，その他の値は構築時にカウントし，
    別の領域に保存しておきます⁠）⁠。
"""

NIJISANJI_DATA = "datas/nijisanji.db"
USER_DIC_PATH = "datas/Nijisanji_dic.csv"


def searchDatabase():
    dbname = NIJISANJI_DATA
    with closing(sqlite3.connect(dbname)) as conn:
        c = conn.cursor()
        query = "select count(*) from word_dict"
        for row in c.execute(query):
            print(row)


def checkSearchedID(video_id):
    """

    :param video_id: YouTubeの動画ID
    :return: 既にデータベースに登録されている場合はTrue。そうでないならFalseを返す
    """
    dbname = NIJISANJI_DATA
    with closing(sqlite3.connect(dbname)) as conn:
        c = conn.cursor()
        query = "select exists(select * from video_comment where video_id = '{}' limit 1)".format(video_id)
        response = c.execute(query)

        for flag in response:
            if flag != (0, ):
                return True
            else:
                return False


def controllDatabase():
    dbname = NIJISANJI_DATA
    with closing(sqlite3.connect(dbname)) as conn:
        c = conn.cursor()
        # query = "create table word_dict(word string, sentence string, place string, video_id string)"
        # query = "delete from word_dict"
        table_name = "video_comment"
        index_query = "update {} set indexed = 0 where indexed = 1".format(table_name)
        c.execute(index_query)
        # c.execute(query)
        conn.commit()


def getVideoComments(insert_data):
    """

    :param insert_data: (video_id, video_title, channel_id, channel_name, comment, upload_date, indexed) 。もしくはこれらのリスト
    :return:
    """
    dbname = NIJISANJI_DATA
    with closing(sqlite3.connect(dbname)) as conn:
        if type(insert_data) is tuple:
            c = conn.cursor()
            query = "insert into video_comment" \
                    "(video_id, video_title, channel_id, channel_name, comment, upload_date, indexed)" \
                    " values (?, ?, ?, ?, ?, ?, ?)"
            c.execute(query, insert_data)
            conn.commit()
        elif type(insert_data) is list:
            c = conn.cursor()
            query = "insert into video_comment" \
                    "(video_id, video_title, channel_id, channel_name, comment, upload_date, indexed)" \
                    " values (?, ?, ?, ?, ?, ?, ?)"
            c.executemany(query, insert_data)
            conn.commit()


def getLiveChat(insert_data):
    """

    :param insert_data: (video_id, video_title, channel_id, channel_name, comment) 。もしくはこれらのリスト
    :return:
    """
    dbname = NIJISANJI_DATA
    with closing(sqlite3.connect(dbname)) as conn:
        if type(insert_data) is tuple:
            c = conn.cursor()
            query = "insert into live_chat" \
                    "(video_id, video_title, channel_id, channel_name, comment, upload_date, indexed)" \
                    " values (?, ?, ?, ?, ?, ?, ?)"
            c.execute(query, insert_data)
            conn.commit()
        elif type(insert_data) is list:
            c = conn.cursor()
            query = "insert into live_chat" \
                    "(video_id, video_title, channel_id, channel_name, comment, upload_date, indexed)" \
                    " values (?, ?, ?, ?, ?, ?, ?)"
            c.executemany(query, insert_data)
            conn.commit()


def getImportantNoun(sentence):
    """

    :param sentence: 形態素解析を行った単語のリスト
    :return: ストップワード(重要でない単語)を除いたリスト
    """
    remover = StopwordRemover()

    text_list_result = remover.remove(sentence)
    print(text_list_result)

    return text_list_result


def getReverseIndex():
    """
    各種データベースから文章を転置インデックスに変換する。
    :return:
    """
    tokenizer = Tokenizer(USER_DIC_PATH, udic_enc="cp932")
    analyzer = Analyzer(token_filters=[CompoundNounFilter()])
    stop_word = stop_words.Stopword()
    demonstrative = stop_word.demonstrative
    pronoun = stop_word.pronoun
    dbname = NIJISANJI_DATA

    with closing(sqlite3.connect(dbname)) as conn:
        c = conn.cursor()
        table_name = "video_comment"
        query = "select video_id, comment from {} where indexed = 0".format(table_name)
        response = c.execute(query)
        insert_word = []

        for data in response:
            video_id = data[0]
            comment = data[1]

            token_set = set()

            for token in tokenizer.tokenize(comment):
                part_of_speech = token.part_of_speech.split(",")
                asterisk = []
                for i, noun in enumerate(part_of_speech):
                    if noun == "*":
                        asterisk.append(i)
                for i in reversed(asterisk):
                    del part_of_speech[i]

                if "固有名詞" in part_of_speech or ("名詞" in part_of_speech and "一般" in part_of_speech):
                    if (token.surface not in demonstrative) and (token.surface not in pronoun):
                        insert_word.append((token.surface, comment, table_name, video_id))
                        token_set.add(token.surface)

            for token in analyzer.analyze(comment):
                """
                    set()を使い重複をなくす
                """
                if token in token_set:
                    continue

                part_of_speech = token.part_of_speech.split(",")
                asterisk = []
                for i, noun in enumerate(part_of_speech):
                    if noun == "*":
                        asterisk.append(i)
                for i in reversed(asterisk):
                    del part_of_speech[i]

                if "固有名詞" in part_of_speech or ("名詞" in part_of_speech and "一般" in part_of_speech):
                    insert_word.append((token.surface, comment, table_name, video_id))

        insert_query = "insert into word_dict (word, sentence, place, video_id) values (?, ?, ?, ?)"
        c.executemany(insert_query, insert_word)

        index_query = "update {} set indexed = 1 where indexed = 0".format(table_name)
        c.execute(index_query)

        conn.commit()


if __name__ == '__main__':
    # getReverseIndex()
    searchDatabase()
