# ExactAbstract

ExactAbstract is a tool designed to analyze text and spit out keywords which are representative of said text. In
particular, its target is the abstracts of various scientific papers. The idea being that you could automatically
tag them, using the tags to sort things out. In general though, it should be able to handle any English language
text.

## Dependencies

This project is written entirely in Python, and currently has the following dependencies:

* Python 3.4, x86
* NLTK 3.0
* Numpy 1.9.0
* Scipy 0.14.0
* Flask
* dit

To install the dependencies run (in a virtualenv or otherwise):

`pip3 install nltk numpy scipy flask git+https://github.com/dit/dit/#egg=dit`

## Usage

To run the project, simply run the `ExactAbstract.py` file, which will start the server. You can either use the text
box on the main page, or otherwise make api requests directly.

## API Docs

To access API docs, go to our [Apiary site](http://docs.exactabstract.apiary.io/).

## MongoDB

The project also requires the use of MongoDB to store abstracts and their related information.

The structure of MongoDB in ExactAbstract is as follows:

Database: ExactAbstract

Collection: abstracts

Document Structure:
'_id' - Abstract id
'text' - Abstract text
'keywords' - Abstract keywords