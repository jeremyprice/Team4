from flask import Flask
from flask import request
from flask import render_template, jsonify
from algorithms.statistical import get_keyword
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from pymongo import MongoClient
from pymongo import DESCENDING
import json

app = Flask(__name__)
client = MongoClient()
db = client.ExactAbstract
abstracts = db.abstracts
ALLOWED_EXTENSIONS = set(['txt'])

# REMOVE BEFORE COMMIT - Clears out collection of abstracts
abstracts.remove({})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/fileUploadWizard')
def file_upload_wizard():
    return render_template('fileUploadWizard.html')


@app.route('/keywords', methods=['POST'])
def get_keywords():
    if request.method == 'POST':
        text = request.form['text']
        return json.dumps(get_keyword(text))
    else:
        return 'Something has gone terribly wrong.'


def get_data(opened_file):
    text = opened_file.read()
    decoded_text = text.decode("ISO-8859-1")
    tokenized_text = word_tokenize(decoded_text)
    keywords = get_keyword(decoded_text)
    highlighted_words = get_highlighted_words(tokenized_text, keywords)
    abstract_id = insert_document(tokenized_text, keywords, abstracts)
    data = {'hashtags': keywords, 'text': decoded_text, 'tokenized_text': tokenized_text,
            'highlighted_text': highlighted_words, 'abstract_id': abstract_id}
    return data


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/uploadajax', methods=['POST'])
def upldfile():

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            data = get_data(file)
            return jsonify(data)


def get_highlighted_words(text, keys):
    words = []
    stemmer = PorterStemmer()
    for word in text:
        if stemmer.stem(word.lower()) in keys:
            words.append(word)
    return words


def insert_document(text, keywords, target_collection):
    while 1:
        cursor = target_collection.find().sort('_id', DESCENDING).limit(1)
        if cursor.count() == 0:
            seq = 1
        else:
            seq = cursor[0]['_id'] + 1
        document = {'_id': seq, 'text': text, 'keywords': keywords, }
        target_collection.insert(document)
        return seq


@app.route('/keyword_output', methods=['POST'])
def keyword_output():
    if request.method == 'POST':
        text = request.form['text']
        tokenized_text = word_tokenize(text)
        keywords = get_keyword(text)
        highlighted = get_highlighted_words(tokenized_text, keywords)
        abstract_id = insert_document(tokenized_text, keywords, abstracts)
        return render_template('output.html', hashtags=keywords, tokenized_text=tokenized_text,
                               highlighted_text=highlighted, abstract_id=abstract_id)
    else:
        return 'Something has gone terribly wrong.'


def parse_id(s_id):
    try:
        return int(s_id)
    except ValueError:
        return -1


@app.route('/abstract_id_search', methods=['POST'])
def abstract_id_search():
    if request.method == 'POST':
        id = request.form['id']
        cursor = abstracts.find({'_id': parse_id(id)})
        if cursor.count() == 0:
            return 'There are no abstracts with that ID!'
        else:
            tokenized_text = cursor[0]['text']
            keywords = cursor[0]['keywords']
            highlighted = get_highlighted_words(tokenized_text, keywords)
            abstract_id = cursor[0]['_id']
            return render_template('output.html', hashtags=keywords, tokenized_text=tokenized_text,
                                   highlighted_text=highlighted, abstract_id=abstract_id)
    else:
        return 'Something has gone terribly wrong.'


if __name__ == '__main__':
    app.run(debug=True)