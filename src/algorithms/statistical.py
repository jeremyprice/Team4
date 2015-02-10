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


def get_keyword(s, n=5):
    tok_sent = get_tokenized_sentences(s)
    terms, mat = get_coocurrence_matrix(tok_sent)
    clusters = cluster_terms(terms, mat)
    rated_terms = get_chi_squared(terms, clusters, mat)
    sorted_terms = sorted(rated_terms.items(), key=operator.itemgetter(1))
    sorted_terms.reverse()
    keywords = sorted_terms[:n]
    return [i[0] for i in keywords]


def get_chi_squared(terms, clusters, matrix):
    words = {}
    for term in terms:
        words[term] = get_chi_squared_for_term(term, terms, clusters, matrix)

    print("Chi values generated at " + str(time.clock()))
    return words


def cluster_terms(terms, matrix):
    time.clock()
    print("Len terms: " + str(len(terms)))
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
                # div = js_divergence(arr, arr2)
                div = 1 - dit.divergences.jensen_shannon_divergence_pmf([arr, arr2])
                div_time += time.clock() - pre_div

                if div > threshold:
                    cluster.add(term2)

        add_cluster(clusters, cluster)

    print("Time spent diverging: " + str(div_time))
    print("Terms clustered at " + str(time.clock()))
    return clusters


def add_cluster(current_clusters, new_cluster):
    for clust in current_clusters:
        for term in new_cluster:
            if term in clust:
                clust.union(new_cluster)
                return
    current_clusters.append(new_cluster)


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


def get_expected_probability(term, terms, clusters, matrix):
    for cluster in clusters:
        if term in cluster:
            cluster_cooccurence = get_cluster_cooccurence(terms, cluster, matrix)
            return (cluster_cooccurence.getnnz() - 1) / len(clusters)

    raise ValueError('Term "' + term + '" was not found to be in any cluster.')


def get_cluster_cooccurence(terms, cluster, matrix):
    rows = []
    for term in cluster:
        rows.append(matrix.getrow(terms[term]))

    total = rows[0]
    for i in range(1, len(rows)):
        total = total + rows[i]

    return total


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
    print(get_keyword(
        """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras leo tortor, varius quis erat id, gravida
        egestas sem. Suspendisse potenti. Ut erat ligula, gravida ut leo ut, mollis tincidunt urna. Maecenas vel purus
        eu erat pharetra suscipit. Etiam scelerisque pharetra diam at porta. Sed pellentesque lorem vitae laoreet
        porttitor. Suspendisse consequat, nulla eget eleifend vestibulum, ex arcu bibendum ipsum, in hendrerit turpis
        mauris sed nisl."""))

    #     Suspendisse lobortis erat libero, in tincidunt magna luctus vel. Praesent posuere leo nunc, lobortis consectetur
    #     urna ornare ut. Donec iaculis, augue nec congue laoreet, dolor nisi convallis nulla, ac ultrices erat neque
    #     maximus lacus. Vivamus porta dictum lorem, ac interdum metus sagittis id. Nulla egestas quam nibh. Pellentesque
    #     auctor ex in mollis pulvinar. Nullam venenatis lacus efficitur ullamcorper malesuada. Nullam ac dolor a ligula
    #     bibendum scelerisque. Quisque in consectetur ex. Phasellus mattis tellus sapien, sed venenatis nibh convallis
    #     semper. Vivamus maximus condimentum cursus. Maecenas eu leo in massa condimentum congue. Vivamus tempor
    #     malesuada ligula, a hendrerit sapien pharetra vitae. Nullam ornare, mi consectetur scelerisque auctor, odio nisi
    #     feugiat eros, nec viverra magna massa ut augue.
    #
    #     Cras non est et felis scelerisque convallis. Sed rutrum ac orci sed efficitur. Curabitur felis leo, gravida at
    #     pulvinar sit amet, tempus ut arcu. Vivamus tempor quam convallis magna feugiat lacinia. Nam sit amet eros eget
    #     diam molestie iaculis. Fusce pulvinar, erat ut bibendum sagittis, purus lacus aliquet elit, eu porttitor tellus
    #     tortor sed arcu. Nulla vitae malesuada magna. Nulla facilisi. Aenean tincidunt erat quis ultricies commodo.
    #     Curabitur posuere luctus tortor, vel efficitur metus ullamcorper sed. Mauris tempus condimentum nibh, vel
    #     laoreet purus sollicitudin sit amet. Fusce vitae rhoncus sapien, et finibus turpis.
    #
    #     Cras placerat ligula vel est tincidunt vehicula non sit amet metus. Etiam consectetur maximus auctor.
    #     Suspendisse in libero condimentum, lacinia urna ac, tempus nibh. Donec consectetur lectus non mattis vestibulum.
    #     Vivamus sed purus at enim convallis ornare a a nunc. Nunc non rhoncus arcu. Pellentesque congue arcu nunc, ut
    #     gravida erat congue id.
    #
    #     Sed posuere lorem eget mi feugiat, feugiat commodo eros egestas. Nam placerat quam ac ullamcorper consequat.
    #     Praesent ex elit, auctor id velit non, fermentum sollicitudin lectus. Quisque ullamcorper metus libero, vel
    #     pretium tortor consectetur sed. Praesent semper mollis molestie. Integer aliquet pretium mi, in cursus sem
    #     bibendum ut. Quisque at consequat eros. Morbi imperdiet erat eu consequat tempor. Etiam interdum porttitor est,
    #     ac mollis dui tincidunt eu. Vestibulum urna mauris, dignissim aliquam scelerisque in, eleifend sed dolor. Nam
    #     non eros ac elit luctus tristique. Sed pharetra risus id nisi egestas tincidunt. Nulla eget feugiat lectus.
    #
    #     Nulla efficitur sapien in mi dictum, vel varius erat feugiat. Integer egestas sit amet nibh quis euismod.
    #     Vestibulum lacinia tempor ipsum, volutpat feugiat dolor. Morbi posuere risus quis lacinia posuere. Sed id
    #     tellus augue. Aliquam massa odio, viverra ut nunc eu, tincidunt tincidunt magna. Nam in tellus nibh. Nullam
    #     efficitur et urna vitae semper. Nunc eu est id ligula elementum ultricies. Vestibulum justo orci, aliquam in
    #     rutrum eu, consectetur et felis. Nullam pharetra nulla felis, in scelerisque felis feugiat."""
    # ))