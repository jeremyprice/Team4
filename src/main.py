from __future__ import division
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import string
import scipy.sparse


def main():
    print(get_keyword("This is an sentence. This is another important sentence, but about bagels. "
                      "This is a very important sentence. This sentence is not. Never important. "
                      "Now here is a phrase that shares no words with the others to make a mess of things."
    ))


def get_keyword(s):
    tok_sent = get_tokenized_sentences(s)
    vocabulary, mat = get_coocurrence_matrix(tok_sent)
    print(vocabulary)
    get_unconditional_probability("sentence", vocabulary, mat)
    return ""


def get_unconditional_probability(term, terms, matrix):
    index = terms[term]
    row = matrix.getrow(index)
    arr = row.toarray()[0]
    arr[index] = 0

    nw = sum(row)
    chi = 0

    for i, freq in enumerate(arr):
        if i == index:
            continue

        pg = get_expected_probability(i, terms, matrix)
        va = pow((freq - nw * pg), 2) / (nw * pg)
        chi += va

    print(chi)
    return chi


def get_expected_probability(index, terms, matrix):
    return (matrix.getrow(index).getnnz() - 1) / len(terms)


def get_probabilities(terms, matrix):
    diag = matrix.diagonal()
    total = float(sum(diag))
    return list(map(lambda x: x / total, diag))


def get_expected_probabilities(terms, matrix):
    arr = [None] * len(terms)
    for term in terms:
        nc = matrix.getcol(terms[term]).getnnz()
        pc = nc / len(terms)
        arr[terms[term]] = pc
    return arr


def get_coocurrence_matrix(sentences):
    vocabulary = {}
    data = []
    row = []
    col = []

    for i, sentence in enumerate(sentences):
        for word in sentence:
            j = vocabulary.setdefault(word, len(vocabulary))
            data.append(1)
            row.append(i)
            col.append(j)

    mat = scipy.sparse.coo_matrix((data, (row, col)))
    coocurence_mat = mat.T * mat
    return vocabulary, coocurence_mat


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