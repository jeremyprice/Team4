from __future__ import division
import string
import operator
import itertools
from math import log

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.probability import FreqDist
import scipy.sparse
import time

import dit

## Method get_keyword
# Summarizes a given abstract to return the keywords based on each terms chi-squared value
#
# @param s The abstract to be parsed
# @param n The number of keywords to generate
# @return array The keywords of the abstract
def get_keyword(s, n=5):
    tok_sent = get_tokenized_sentences(s)
    terms, mat = get_coocurrence_matrix(tok_sent)
    clusters = cluster_terms(terms, mat)
    rated_terms = get_chi_squared(terms, clusters, mat)
    sorted_terms = sorted(rated_terms.items(), key=operator.itemgetter(1))
    sorted_terms.reverse()
    keywords = sorted_terms[:n]
    return [i[0] for i in keywords]

## Method get_keyword
# Assigns a chi-squared value to all of the given terms based on the clusters and co-occurrence matrix
#
# @param terms The terms being assigned a chi-squared value
# @param clusters The clusters formed from term-clustering
# @param matrix The co-occurrence matrix of the abstract
# @return array The terms with their assigned chi-squared value
def get_chi_squared(terms, clusters, matrix):
    words = {}
    for term in terms:
        words[term] = get_chi_squared_for_term(term, terms, clusters, matrix)
    return words

## Method cluster_terms
# Performs term clustering of the abstract given the abstracts co-occurrence matrix
#
# @param terms The terms within the co-occurrence matrix
# @param matrix The co-occurrence matrix of the abstract
# @return array The term clusters of the abstract
def cluster_terms(terms, matrix):
    time.clock()
    threshold = 0.95 * log(2)
    clusters = []
    div_time = 0.0

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

                pre_div = time.clock()
                div = 1 - dit.divergences.jensen_shannon_divergence_pmf([arr, arr2])
                div_time += time.clock() - pre_div

                if div > threshold:
                    cluster.add(term2)

        add_cluster(clusters, cluster)

    return clusters

## Method add_cluster
# Adds a cluster to the list of clusters, combining it with existing clusters if a term belongs to both.
#
# @param current_clusters The current list of term-clusters
# @param new_cluster The new cluster of terms to be added
def add_cluster(current_clusters, new_cluster):
    for clust in current_clusters:
        for term in new_cluster:
            if term in clust:
                clust.union(new_cluster)
                return
    current_clusters.append(new_cluster)

## Method get_chi_squared_for_term
# Analyzes a term within the abstract to assign it a chi-squared value
#
# @param term The term being assigned a chi-squared value
# @param terms The terms of the abstract
# @param clusters The clusters of terms
# @param matrix The co-occurrence matrix of the abstract
# @return numeric The chi-squared value of the term
def get_chi_squared_for_term(term, terms, clusters, matrix):
    index = terms[term]
    row = matrix.getrow(index)
    arr = row.toarray()[0]
    arr[index] = 0

    nw = row.sum()
    chi = 0
    maximal = 0

    for cluster in clusters:
        if term in cluster:
            continue

        pc = get_expected_probability(term, terms, clusters, matrix)
        cluster_cooccurence = get_cluster_cooccurence(terms, cluster, matrix).toarray()[0]
        freq = cluster_cooccurence[index]
        tmp = nw * pc
        tmp = pow((freq - tmp), 2) / tmp
        chi += tmp

        if tmp > maximal:
            maximal = tmp

    return chi - maximal

## Method get_expected_probability
# Computes the probability of a term occuring in the abstract given the terms cluster and the co-occurrence matrix
#
# @param term The term being assigned a chi-squared value
# @param terms The terms of the abstract
# @param clusters The clusters of terms
# @param matrix The co-occurrence matrix of the abstract
# @return numeric The probability of the term occurring in the abstract
def get_expected_probability(term, terms, clusters, matrix):
    for cluster in clusters:
        if term in cluster:
            cluster_cooccurence = get_cluster_cooccurence(terms, cluster, matrix)
            return (cluster_cooccurence.getnnz() - 1) / len(clusters)

    raise ValueError('Term "' + term + '" was not found to be in any cluster.')

## Method get_cluster_cooccurence
# Computes the sum of the co-occurrence value of all of the terms in a cluster
#
# @param terms The terms of the abstract
# @param clusters The clusters of terms
# @param matrix The co-occurrence matrix of the abstract
# @return numeric The cluster occurrence value
def get_cluster_cooccurence(terms, cluster, matrix):
    rows = []
    for term in cluster:
        rows.append(matrix.getrow(terms[term]))

    total = rows[0]
    for i in range(1, len(rows)):
        total = total + rows[i]

    return total

## Method get_coocurrence_matrix
# Computes the co-occurrence matrix of the abstract terms
#
# @param sentences The terms of the abstract
# @return array The terms of the co-occurrence matrix
# @return array The co-occurrence value for the terms
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

## Method get_tokenized_sentences
# Tokenizes the text of the abstract to evaluate.
#
# @param s The text of the abstract
# @return array The tokenized text of the abstract
def get_tokenized_sentences(s):
    sentences = sent_tokenize(s.lower())
    return filter_sentences(sentences)

## Method filter_sentences
# Stems words of sentences and removes all stop words
#
# @param sentences The sentence to filter
# @param fraction_words_to_use Used in computing which words to keep in analysis
# @return array The words to be kept in the sentence
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
    print(get_keyword(
        """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras leo tortor, varius quis erat id, gravida
        egestas sem. Suspendisse potenti. Ut erat ligula, gravida ut leo ut, mollis tincidunt urna. Maecenas vel purus
        eu erat pharetra suscipit. Etiam scelerisque pharetra diam at porta. Sed pellentesque lorem vitae laoreet
        porttitor. Suspendisse consequat, nulla eget eleifend vestibulum, ex arcu bibendum ipsum, in hendrerit turpis
        mauris sed nisl."""))