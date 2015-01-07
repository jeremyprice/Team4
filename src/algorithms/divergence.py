__author__ = 'Jordon'

from numpy import zeros, array
from math import sqrt, log


def kl_divergence(p, q):
    return sum(_p * log(_p / _q) for _p, _q in zip(p, q) if _p != 0 and _q != 0)


def js_divergence(p, q):
    jsd = 0.0
    weight = 0.5
    average = zeros(len(p))
    for x in range(len(p)):
        average[x] = weight * p[x] + (1 - weight) * q[x]
        jsd = (weight * kl_divergence(array(p), average)) + ((1 - weight) * kl_divergence(array(q), average))
    return 1 - (jsd / sqrt(2 * log(2)))

if __name__ == '__main__':
    p = [5, 0.5]
    q = [5, 0.4]
    print(js_divergence(p, q))