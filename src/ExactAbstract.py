from flask import Flask
from flask import request
from flask import render_template
from algorithms.statistical import get_keyword
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
import json

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/keywords', methods=['POST'])
def get_keywords():
    if request.method == 'POST':
        text = request.form['text']
        return json.dumps(get_keyword(text))
    else:
        return 'Something has gone terribly wrong.'

def get_highlighted_words(text, keys):
    words = []
    stemmer = PorterStemmer()
    for word in text:
        if stemmer.stem(word.lower()) in keys:
            words.append(word)
    return words

@app.route('/keyword_output', methods=['POST'])
def keyword_output():
    if request.method == 'POST':
        text = request.form['text']
        tokenized_text = word_tokenize(text)
        keywords = get_keyword(text)
        highlighted = get_highlighted_words(tokenized_text, keywords)
        return render_template('output.html', hashtags=keywords, text=text, tokenized_text=tokenized_text, highlighted_text=highlighted)
    else:
        return 'Something has gone terribly wrong.'


if __name__ == '__main__':
    app.run()
