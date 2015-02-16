from flask import Flask
from flask import request
from flask import render_template, jsonify, make_response
from flask.helpers import url_for
from algorithms.statistical import get_keyword
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from pymongo import MongoClient
from pymongo import DESCENDING
import json
import os
import os.path

app = Flask(__name__)
client = MongoClient()
db = client.ExactAbstract
abstracts = db.abstracts
ALLOWED_EXTENSIONS = set(['txt'])

# REMOVE BEFORE COMMIT - Clears out collection of abstracts
# abstracts.remove({})
def parse_id(s_id):
    try:
        return int(s_id or 0)
    except ValueError:
        return -1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<abstract_id>')
def jump_to_index(abstract_id):
    cursor = abstracts.find({'_id': parse_id(abstract_id)})
    if cursor.count() == 0:
        return 'There are no abstracts with that ID!'
    else:
        tokenized_text = cursor[0]['text']
        keywords = cursor[0]['keywords']
        highlighted = get_highlighted_words(tokenized_text, keywords)
        abstract_id = cursor[0]['_id']
        related_abstracts = get_related_abstracts(abstract_id, keywords)
        return render_template('output.html', hashtags=keywords, tokenized_text=tokenized_text,
                               highlighted_text=highlighted, abstract_id=abstract_id,
                               related_abstracts=related_abstracts)

@app.route('/abstract_keyword_search', methods=['POST'])
def abstract_keyword_search():
    if request.method == 'POST':
        keyword = request.form['keyword']
        cursor = abstracts.find({})
        output = []
        stemmer = PorterStemmer()
        if cursor.count() == 0:
            return 'There are no abstracts!'
        else:
            for x in range(0, cursor.count()):
                keywords = cursor[x]['keywords']
                if any(stemmer.stem(keyword.lower()) in s for s in keywords):
                    output.append([str(cursor[x]['_id']), cursor[x]['keywords']])
        return render_template('keywordSearchOutput.html', output=output)
    else:
        return 'Something has gone terribly wrong.'

@app.route('/single_keyword_search/<keyword>')
def single_keyword_search(keyword):
    cursor = abstracts.find({})
    output = []
    stemmer = PorterStemmer()
    if cursor.count() == 0:
        return 'There are no abstracts!'
    else:
        for x in range(0, cursor.count()):
            keywords = cursor[x]['keywords']
            if any(stemmer.stem(keyword.lower()) in s for s in keywords):
                output.append([str(cursor[x]['_id']), cursor[x]['keywords']])
    return render_template('keywordSearchOutput.html', output=output)

@app.route('/delete_abstract/', methods=['GET', 'POST'])
def delete_abstract():
    if request.method == 'POST':
        post_id = request.form.get('abstract_id')
        cursor = abstracts.find({'_id': parse_id(post_id)})
        if cursor.count() == 0:
            return 'There was an error deleting the abstract'
        else:
            abstracts.remove({"_id": parse_id(post_id)})
            return render_template('deleteConfirmation.html')
    else:
        return 'Something has gone terribly wrong.'


@app.route('/fileUploadWizard', methods=['GET', 'POST'])
def file_upload_wizard():
    return render_template('fileUploadWizard.html')


@app.route('/downloads/<run>')
def downloadResults(run):
    # Check for valid file and assign it to `inbound_file`
    # data = upldfile()
    fname = "results-" + run + ".txt"
    f = open(os.path.dirname(__file__) + "/../" + fname)
    # file = open("../results-" + run + ".txt", "r")
    response = make_response(f.read())
    response.headers["Content-Disposition"] = "attachment; filename=" + fname
    return response

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
    # data that will be stored in output file
    filedata = {'abstract_id': abstract_id, 'filename': opened_file.filename, 'hashtags': keywords,
                'original_abstract': decoded_text, }
    # create a new file for each file uploaded with the data from the results
    resultsfile = open('results' + '-' + str(abstract_id) + '.txt', 'w+')
    jsonifieddata = json.dumps(filedata)
    resultsfile.write(jsonifieddata)
    resultsfile.close()
    # data needed for webpage items to be populated
    data = {'filename': opened_file.filename, 'hashtags': keywords, 'text': decoded_text,
            'tokenized_text': tokenized_text,
            'highlighted_text': highlighted_words, 'abstract_id': abstract_id}
    return data


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/uploadajax', methods=['POST'])
def upldfile():
    allData = {'fileInfo': []}
    if request.method == 'POST':
        files = request.files.getlist('file[]')
        for file in files:
            if file and allowed_file(file.filename):
                data = get_data(file)
                allData['fileInfo'].append(data)
        return jsonify(allData)


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

def get_related_abstracts(abstract_id, abstract_keywords):
    ids = []
    cursor = abstracts.find({})
    if cursor.count() == 0:
        return ids
    else:
        for x in range(0, cursor.count()):
            keywords = cursor[x]['keywords']
            if all(word in abstract_keywords for word in keywords) and cursor[x]['_id'] != abstract_id:
                ids.append(cursor[x]['_id'])
        return ids

@app.route('/keyword_output', methods=['POST'])
def keyword_output():
    if request.method == 'POST':
        text = request.form['text']
        tokenized_text = word_tokenize(text)
        keywords = get_keyword(text)
        highlighted = get_highlighted_words(tokenized_text, keywords)
        abstract_id = insert_document(tokenized_text, keywords, abstracts)
        related_abstracts = get_related_abstracts(abstract_id, keywords)
        return render_template('output.html', hashtags=keywords, tokenized_text=tokenized_text,
                               highlighted_text=highlighted, abstract_id=abstract_id,
                               related_abstracts=related_abstracts)
    else:
        return 'Something has gone terribly wrong.'

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
            related_abstracts = get_related_abstracts(abstract_id, keywords)
            return render_template('output.html', hashtags=keywords, tokenized_text=tokenized_text,
                                   highlighted_text=highlighted, abstract_id=abstract_id,
                                   related_abstracts=related_abstracts)
    else:
        return 'Something has gone terribly wrong.'

# API example calls
@app.route('/api/abstracts/<abstract_id>')
def api_jump_to_index(abstract_id):
    cursor = abstracts.find({'_id': parse_id(abstract_id)})
    results = {}
    status_code = 200
    headers = {'Content-Type':'application/json'}
    if cursor.count() == 0:
        results['error'] = 'There are no abstracts with that ID!'
        status_code = 404
    else:
        result = {}
        result['tokenized_text'] = cursor[0]['text']
        result['keywords'] = cursor[0]['keywords']
        result['highlighted'] = get_highlighted_words(result['tokenized_text'], result['keywords'])
        result['abstract_id'] = cursor[0]['_id']
        results['results'] = [result]
    return (json.dumps(results), status_code, headers)

@app.route('/api/upload', methods=['POST'])
def api_upload():
    results = {}
    status_code = 200
    headers = {'Content-Type':'application/json'}
    if request.method == 'POST':
        parsed_request = request.get_json()
        if 'files' not in parsed_request:
            status_code = 400
            results['error'] = 'Unrecognized JSON object in request'
            return (json.dumps(results), status_code, headers)
        processed = []
        for file_contents in parsed_request['files']:
            tokenized_text = word_tokenize(file_contents)
            keywords = get_keyword(file_contents)
            highlighted_words = get_highlighted_words(tokenized_text, keywords)
            abstract_id = insert_document(tokenized_text, keywords, abstracts)
            result = {}
            result['tokenized_text'] = tokenized_text
            result['keywords'] = keywords
            result['highlighted'] = highlighted_words
            result['abstract_id'] = abstract_id
            processed.append(result)
        results['results'] = processed
    else: # unknown requests type
        results['error'] = 'Method Not Allowed'
        status_code = 405
    return (json.dumps(results), status_code, headers)

if __name__ == '__main__':
    app.run(debug=True)
