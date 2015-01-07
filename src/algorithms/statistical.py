from __future__ import division
import string
import operator
import itertools

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.probability import FreqDist
import scipy.sparse
from divergence import js_divergence
from math import log


def get_keyword(s, n=5):
    tok_sent = get_tokenized_sentences(s)
    terms, mat = get_coocurrence_matrix(tok_sent)
    clusters = cluster_terms(terms, mat)
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


def cluster_terms(terms, matrix):
    threshold = 0.95 * log(2)
    clusters = []

    for term in terms:
        dict_index = terms[term]
        row = matrix.getrow(dict_index)
        arr = row.toarray()[0]
        arr[dict_index] = 0

        cluster = set()
        cluster.add(term)

        for term2 in terms:
            if term != term2:
                dict_index = terms[term2]
                row = matrix.getrow(dict_index)
                arr2 = row.toarray()[0]
                arr2[dict_index] = 0
                div = js_divergence(arr, arr2)

                if div > threshold:
                    cluster.add(term2)

        add_cluster(clusters, cluster)

    return clusters


def add_cluster(current_clusters, new_cluster):
    for clust in current_clusters:
        for term in new_cluster:
            if term in clust:
                clust.union(new_cluster)
                return
    current_clusters.append(new_cluster)


def get_chi_squared_for_term(term, terms, matrix):
    index = terms[term]
    row = matrix.getrow(index)
    arr = row.toarray()[0]
    arr[index] = 0

    nw = row.sum()
    chi = 0
    maximal = 0

    for i, freq in enumerate(arr):
        if i == index:
            continue

        pg = get_expected_probability(i, terms, matrix)
        tmp = nw * pg
        tmp = pow((freq - tmp), 2) / tmp
        chi += tmp

        if tmp > maximal:
            maximal = tmp

    return chi - maximal


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
    return filter_sentences(sentences)


def filter_sentences(sentences, fraction_words_to_use=1):
    stops = set(stopwords.words('english')).union(string.punctuation)
    stemmer = PorterStemmer()

    for i in range(len(sentences)):
        sentences[i] = word_tokenize(sentences[i])
        sentences[i] = [stemmer.stem(word) for word in sentences[i] if word not in stops]

    words = list(itertools.chain.from_iterable(sentences))
    freq_dist = FreqDist(words)
    target_num = int(freq_dist.B() * fraction_words_to_use)
    targets = freq_dist.most_common(target_num)
    targets = [target[0] for target in targets]

    for i in range(len(sentences)):
        sentences[i] = [word for word in sentences[i] if word in targets]

    return sentences

if __name__ == '__main__':
    print(get_keyword("Puppies are cool. Puppies are awesome."))