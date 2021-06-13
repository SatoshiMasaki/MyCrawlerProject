from flask import Flask, render_template
from util import search_twitter_trend, search_wiki, token_analytics


app = Flask(__name__)


@app.route("/")
def test():
    datas = search_twitter_trend()
    container = {}
    counter = 0
    for data in datas:
        if counter == 10:
            break
        container[data] = token_analytics([data])
        counter += 1
    return render_template("index.html", datas=container)


if __name__ == '__main__':
    app.run()
