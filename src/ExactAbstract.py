from flask import Flask
from flask import request
from flask import render_template
from algorithms.statistical import get_keyword
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


if __name__ == '__main__':
    app.run(debug=True)
