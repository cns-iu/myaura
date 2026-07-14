"""Top-k kendall-tau distance.

This module generalise kendall-tau as defined in [1].
It returns a distance: 0 for identical (in the sense of top-k) lists and 1 if completely different.

Example:
    Simply call kendall_top_k with two same-length arrays of ratings (or also rankings), length of the top elements k (default is the maximum length possible), and p (default is 0, see [1]) as parameters:

        import kendall
        a = np.array([1,2,3,4,5])
        b = np.array([5,4,3,2,1])
        kendall.kendall_top_k(a,b,k=4)

Author: Xuan Wang

With reference to Alessandro Checco's code at
    https://github.com/AlessandroChecco/top-k-kendall-tau
Alessandro's code omitted case 3 in Fagin's paper and scipy's kendall's tau is actually tau-b, not tau-a but Fagin uses tau-a.

References
[1] Fagin, Ronald, Ravi Kumar, and D. Sivakumar. "Comparing top k lists." SIAM Journal on Discrete Mathematics 17.1 (2003): 134-160.
"""
import numpy as np
import scipy.stats as stats
import scipy.stats.mstats_basic as mstats_basic
import scipy.special as special
from numpy import ma

def kendall_top_k(a,b,k=None,p=0,reverse=False): #zero is equal 1 is max distance, compare with 1-scipy.stats.kendalltau(a,b)/2+1/2
    """
    kendall_top_k(np.array,np.array,k,p)
    This function generalise kendall-tau as defined in [1] Fagin, Ronald, Ravi Kumar, and D. Sivakumar. "Comparing top k lists." SIAM Journal on Discrete Mathematics 17.1 (2003): 134-160.
    It returns a distance: 0 for identical (in the sense of top-k) lists and 1 if completely different.

    top k are marked as smallest k ranking number

    Example:
        Simply call it with two same-length arrays of ratings (or also rankings), length of the top elements k (default is the maximum length possible), and p (default is 0, see [1]) as parameters:

            $ a = np.array([1,2,3,4,5])
            $ b = np.array([5,4,3,2,1])
            $ kendall_top_k(a,b,k=4)
    """

    if k is None:
        k = a.size
    if a.size != b.size:
        raise NameError('The two arrays need to have same lengths')
    k = min(k, a.size)
    # There is a question, should top k be smallest or largest. In case 2 we will face the problem again!
    # might need a parameter here
    if reverse:
        # largest k
        a_top_k = np.argpartition(a, -k)[-k:]
        b_top_k = np.argpartition(b, -k)[-k:]
    else:
        # smallest k
        a_top_k = np.argpartition(a, k - 1)[:k]
        b_top_k = np.argpartition(b, k - 1)[:k]
    common_items = np.intersect1d(a_top_k,b_top_k)
    only_in_a = np.setdiff1d(a_top_k, common_items)
    only_in_b = np.setdiff1d(b_top_k, common_items)
    z = common_items.size


    # cannot directly use stats.kendalltau, because it is tau-b, not tau-a
    # tau-b will have variable n_0 if there are ties, while tau-a is always normalized with n(n-1)/2
    # kendall = (1 - (stats.kendalltau(a[common_items], b[common_items])[0] / 2 + 0.5)) * (z * (z - 1) / 2)  # case 1

    # this is better, however, when there are ties, C+D will be less than z(z-1)/2 thus the un-normalization could be inaccurate
    # kendall = (1 - (mstats_basic.kendalltau(a[common_items], b[common_items], False)[0] / 2 + 0.5)) * (z * (z - 1) / 2)  # case 1

    # now we crop from scipy directly about the difference part
    rx = ma.masked_equal(mstats_basic.rankdata(a[common_items]), 0)
    ry = ma.masked_equal(mstats_basic.rankdata(b[common_items]), 0)
    idx = rx.argsort()
    (rx, ry) = (rx[idx], ry[idx])
    D = np.sum([((ry[i+1:] < ry[i])*(rx[i+1:] > rx[i])).filled(0).sum()
                for i in range(len(ry)-1)], dtype=float)
    kendall = D
    if np.isnan(kendall): # degenerate case with only one item (not defined by Kendall)
        if z <= 1:
            kendall = 0
        else:
            return np.nan
    if reverse:
        for i in common_items:  # case 2
            for j in only_in_a:
                if a[i] > a[j]:
                    kendall += 1
            for j in only_in_b:
                if b[i] > b[j]:
                    kendall += 1
    else:
        for i in common_items: #case 2
            for j in only_in_a:
                if a[i] < a[j]:
                    kendall += 1
            for j in only_in_b:
                if b[i] < b[j]:
                    kendall += 1
    kendall += (k - z) ** 2  # case 3
    kendall += 2*p * special.binom(k-z,2)     #case 4
    # Lemma 3.1
    # kendall += (k - z) * ((2 + p) * k - p * z + 1 - p)
    # kendall -= np.sum(only_in_a) + k - z # wrong. can be fix later
    # kendall -= np.sum(only_in_b) + k - z

    kendall_norm = kendall / ((2 * k - z) * (2 * k - z - 1) / 2)  # normalization
    # 1. cannot use original k(k-1)/2, because case 3 will add k**2 in extreme condition
    #    then it will be greater than 1
    # 2. cannot be irrelevant to z, because when z=0, must be k(k-1)/2, so it must have a way to change
    # 3. 2k-z is the unique element set cardinality. a little big but usable. compatible to traditional tau
    return kendall, kendall_norm
    
if __name__ == "__main__":
    print("This is only a module")
