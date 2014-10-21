from __future__ import division
import string
import operator

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import scipy.sparse


def main():
    print(get_keyword(
        "This is a sentence. This is another important sentence, but about bagels. "
        "This is a very important sentence. This sentence is not. Never important. "
        "Now here is a phrase that shares no words with the others to make a mess of things."))


def get_keyword(s, n=5):
    tok_sent = get_tokenized_sentences(s)
    terms, mat = get_coocurrence_matrix(tok_sent)
    rated_terms = get_chi_squared(terms, mat)
    sorted_terms = sorted(rated_terms.items(), key=operator.itemgetter(1))
    sorted_terms.reverse()
    keywords = sorted_terms[:n]
    return [i[0] for i in keywords]


def get_chi_squared(terms, matrix):
    words = {}
    for term in terms:
        prob = get_chi_squared_for_term(term, terms, matrix)
        words.setdefault(term, prob)
    return words


def get_chi_squared_for_term(term, terms, matrix):
    index = terms[term]
    row = matrix.getrow(index)
    arr = row.toarray()[0]
    arr[index] = 0

    nw = row.sum()
    chi = 0

    for i, freq in enumerate(arr):
        if i == index:
            continue

        pg = get_expected_probability(i, terms, matrix)
        tmp = nw * pg
        chi += pow((freq - tmp), 2) / tmp

    return chi


def get_expected_probability(index, terms, matrix):
    return (matrix.getrow(index).getnnz() - 1) / len(terms)


def get_expected_probabilities(terms, matrix):
    arr = [None] * len(terms)
    for term in terms:
        nc = matrix.getcol(terms[term]).getnnz()
        pc = nc / len(terms)
        arr[terms[term]] = pc
    return arr


def get_coocurrence_matrix(sentences):
    terms = {}
    data = []
    row = []
    col = []

    for i, sentence in enumerate(sentences):
        for word in sentence:
            j = terms.setdefault(word, len(terms))
            data.append(1)
            row.append(i)
            col.append(j)

    mat = scipy.sparse.coo_matrix((data, (row, col)))
    coocurence_mat = mat.T * mat
    return terms, coocurence_mat


def get_tokenized_sentences(s):
    sentences = sent_tokenize(s.lower())
    for i in range(len(sentences)):
        sentences[i] = filter_words(sentences[i])
    return sentences


def filter_words(sentence):
    words = word_tokenize(sentence)
    stops = set(stopwords.words('english')).union(string.punctuation)
    return [word for word in words if word not in stops]


if __name__ == '__main__':
    main()