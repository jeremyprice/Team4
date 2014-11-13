from flask import Flask
from flask import request
from flask import render_template
from algorithms.statistical import get_keyword
from nltk.tokenize import word_tokenize
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
    
    
@app.route('/keyword_output', methods=['POST'])
def keyword_output():
    if request.method == 'POST':
        text = request.form['text']
        tokenized_text = word_tokenize(text)
        keywords = get_keyword(text)
        return render_template('output.html', hashtags=keywords, text=text, tokenized_text=tokenized_text)
    else:
        return 'Something has gone terribly wrong.'


if __name__ == '__main__':
    app.run(debug=True)
