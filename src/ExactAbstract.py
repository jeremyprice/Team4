from flask import Flask
from flask import request
from flask import render_template
from algorithms.Statistical import get_keyword

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/get_user_input', methods=['POST'])
def my_form_post():
    if request.method == 'POST':
        text = request.form['userText']
        return ', '.join(get_keyword(text))
    else:
        return 'Something has gone terribly wrong.'


if __name__ == '__main__':
    app.run(debug=True)
