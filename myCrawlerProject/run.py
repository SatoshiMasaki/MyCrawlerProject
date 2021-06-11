from flask import Flask, render_template
from util import search_twitter_trend, search_wiki


app = Flask(__name__)


@app.route("/")
def test():
    datas = search_twitter_trend()
    return render_template("index.html", datas=datas)


if __name__ == '__main__':
    app.run()
