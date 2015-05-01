## @package ExactAbstract
# All non-algorithm related work for ExactAbstract
#
# The main package for the app

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

## Method index
# Simple integer parsing method.
#
# @param s_id The string of what should be an abstract id
# @return int The integer value of the string, or -1 if not an integer
def parse_id(s_id):
    try:
        return int(s_id or 0)
    except ValueError:
        return -1

## Method index
# Displays the main page to the user
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def welcome():
    return render_template('about.html')

## Method jump_to_index
# Displays the abstract with keywords highlighted, as well as all related information to the user
#
# @param abstract_id The id of the abstract to display
@app.route('/<abstract_id>')
def jump_to_index(abstract_id):
    cursor = abstracts.find({'_id': parse_id(abstract_id)})
    if cursor.count() == 0:
        return render_template('noAbstractFoundError.html')
    else:
        tokenized_text = cursor[0]['text']
        keywords = cursor[0]['keywords']
        highlighted = get_highlighted_words(tokenized_text, keywords)
        abstract_id = cursor[0]['_id']
        related_abstracts = get_related_abstracts(abstract_id, keywords)
        return render_template('output.html', hashtags=keywords, tokenized_text=tokenized_text,
                               highlighted_text=highlighted, abstract_id=abstract_id,
                               related_abstracts=related_abstracts)

## Method abstract_keyword_search
# Stems the manually entered keyword from the main page and displays every abstract containing the keyword to the user
@app.route('/abstract_keyword_search', methods=['POST'])
def abstract_keyword_search():
    if request.method == 'POST':
        keyword = request.form['keyword']
        cursor = abstracts.find({})
        output = []
        stemmer = PorterStemmer()
        if len(keyword) == 0:
            return render_template('noAbstractFoundError.html')
        else:
            for x in range(0, cursor.count()):
                keywords = cursor[x]['keywords']
                if any(stemmer.stem(keyword.lower()) in s for s in keywords):
                    output.append([str(cursor[x]['_id']), cursor[x]['keywords']])
        return render_template('keywordSearchOutput.html', output=output)
    else:
        return 'Something has gone terribly wrong.'

## Method single_keyword_search
# Called when a keyword from an abstract output is clicked on.
# Displays every abstract containing the keyword to the user
#
# @param keyword The keyword being searched for
@app.route('/single_keyword_search/<keyword>')
def single_keyword_search(keyword):
    cursor = abstracts.find({})
    output = []
    stemmer = PorterStemmer()
    print(cursor.count())
    if cursor.count() == 0:
        return render_template('noAbstractFoundError.html')
    else:
        for x in range(0, cursor.count()):
            keywords = cursor[x]['keywords']
            if any(stemmer.stem(keyword.lower()) in s for s in keywords):
                output.append([str(cursor[x]['_id']), cursor[x]['keywords']])
    return render_template('keywordSearchOutput.html', output=output)

## Method delete_abstract
# Deletes the current abstract from the MongoDB collection
# Displays a deletion confirmation page to the user
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

## Method file_upload_wizard
# Displays the file upload wizard to the user
@app.route('/fileUploadWizard', methods=['GET', 'POST'])
def file_upload_wizard():
    return render_template('fileUploadWizard.html')

## Method downloadResults
# Provides the user a file of the abstract and its summarized information
#
# @param run The filename to be downloaded
@app.route('/downloads/<run>')
def downloadResults(run):
    # Check for valid file and assign it to `inbound_file`
    # data = upldfile()
    fname = "/results-" + run + ".txt"
    f = open(os.path.dirname(__file__) + fname)
    # file = open("../results-" + run + ".txt", "r")
    response = make_response(f.read())
    response.headers["Content-Disposition"] = "attachment; filename=" + fname
    return response

## Method get_keywords
# Reads in abstract text and displays the keywords
# Used in early development to easily see keywords of an abstract
#
# @return json The json dump of the keywords of the abstract
@app.route('/keywords', methods=['POST'])
def get_keywords():
    if request.method == 'POST':
        text = request.form['text']
        return json.dumps(get_keyword(text))
    else:
        return 'Something has gone terribly wrong.'

## Method get_data
# Retrieves the abstract contained in the given file, summarizes the abstract, and stores the related information.
#
# @param opened_file The uploaded file containing the abstract text
# @return object The data object of the abstract and related information.
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

## Method allowed_file
# Checks to see if a uploaded file type is currently supported by the system. Note currently only txt files are allowed.
#
# @param filename The name of the file being checked
# @return boolean Whether or not the file name is in the list of allowed extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

## Method upldfile
# Parses a list of uploaded files to analyze all of the abstracts
#
# @return json The jsonified data of all of the summarized abstracts from the uploaded files.
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

## Method get_highlighted_words
# Traverses the abstract and returns a list of all the words whose stem matches a keyword
#
# @param text The text of the abstract
# @param keys The keywords of the summarized abstract
# @return array The array of words contributing to the keywords
def get_highlighted_words(text, keys):
    words = []
    stemmer = PorterStemmer()
    for word in text:
        if stemmer.stem(word.lower()) in keys:
            words.append(word)
    return words

## Method insert_document
# Creates a MongoDB document for the given summarized abstract and stores it in the given collection.
#
# @param text The text of the abstract
# @param keywords The keywords of the summarized abstract
# @param target_collection The MongoDB collection storing the abstract documents
# @return int The id of the summarized abstract (created with the document creation)
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

## Method get_related_abstracts
# Searches the MongoDB collection of abstract documents for all abstracts with the same keywords
#
# @param abstract_id The id of the current abstract
# @param abstract_keywords The keywords of the current abstract
# @return array The array of ids of abstracts with the same keywords
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

## Method keyword_output
# Called when manually entering abstract text into the main page.
# Parses the text, finds keywords, and inserts the abstract into the MongoDB collection.
# The user is displayed the original text with highlighted keywords, along with the keywords and related abstract ids
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

## Method abstract_id_search
# Called when manually entering abstract id into the main page.
# The user is displayed the original text with highlighted keywords, along with the keywords and related abstract ids
@app.route('/abstract_id_search', methods=['POST'])
def abstract_id_search():
    if request.method == 'POST':
        id = request.form['id']
        cursor = abstracts.find({'_id': parse_id(id)})
        if cursor.count() == 0:
            return render_template('noAbstractFoundError.html')
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

## Method api_jump_to_index
# Gives the users API output of a specific abstract given its id
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

## Method api_upload
# Allows the user to analyze abstracts through the API
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

## Constructor
# Runs the application
if __name__ == '__main__':
    app.run(debug=True)
