# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 11:05:32 2019

@author: Sikander
"""

import os
import pickle
import pandas as pd

TERM_FREQ = 1
USE_DISTR = 0

def tally(dct, key, num=1):
    if key in dct:
        dct[key] += num
    else:
        dct[key] = num

#BASIC: Total number of matched posts, distributions of matches per post, tokens, parents, types
if TERM_FREQ == 1:
    #Forum posts
    # print 'FORUMS'
    # matchesperpost_p = {0: 0}
    # matchesperuser_p = dict()
    # matchpostsperuser_p = dict()
    # tokens_p = dict()
    # parents_p = dict()
    # types_p = dict()
    # count = 0
    # for root, dirs, files in os.walk('tagging_results_users', topdown=True):
    #     for f in files:
    #         count += 1
    #         print str(count) + ' out of ' + str(len(files))
    #         if f[:7] == 'matches':
    #             ulst = pickle.load(open('tagging_results_users/{0}'.format(f), 'rb'))
    #             nummatch = 0
    #             for pdct in ulst: #Going through list of post dicts in user list
    #                 nummatch += len(pdct['matches'])
    #                 tally(matchesperpost_p, len(pdct['matches']))
    #                 for m in pdct['matches']: #Going through matches in each post dict
    #                     tally(tokens_p, m['token'])
    #                     tally(parents_p, m['parent'])
    #                     tally(types_p, m['type'])
    #             tally(matchesperuser_p, nummatch)
    #         else:
    #             ustat = pickle.load(open('tagging_results_users/{0}'.format(f), 'rb'))
    #             npost_zeromatch = int(ustat['posts']) - int(ustat['matched_posts'])
    #             matchesperpost_p[0] += npost_zeromatch
    #             tally(matchpostsperuser_p, ustat['matched_posts'])
    # pickle.dump(matchesperpost_p, open("tag_analysis/matchesperpost_p.pkl", 'wb'))
    # pickle.dump(matchesperuser_p, open("tag_analysis/matchesperuser_p.pkl", 'wb'))
    # pickle.dump(matchpostsperuser_p, open("tag_analysis/matchpostsperuser_p.pkl", 'wb'))
    # pickle.dump(tokens_p, open("tag_analysis/tokens_p.pkl", 'wb'))
    # pickle.dump(parents_p, open("tag_analysis/parents_p.pkl", 'wb'))
    # pickle.dump(types_p, open("tag_analysis/types_p.pkl", 'wb'))
    #Chats
    print 'CHATS'
    matchesperpost_c = {0: 0}
    matchesperuser_c = dict()
    matchpostsperuser_c = dict()
    tokens_c = dict()
    parents_c = dict()
    types_c = dict()
    count = 0
    for root, dirs, files in os.walk('tagging_results_chats', topdown=True):
        for f in files:
            count += 1
            print str(count) + ' out of ' + str(len(files))
            if f[:7] == 'matches':
                ulst = pickle.load(open('tagging_results_chats/{0}'.format(f), 'rb'))
                for pdct in ulst: #Going through list of post dicts in user list
                    nummatch += len(pdct['matches'])
                    tally(matchesperpost_c, len(pdct['matches']))
                    for m in pdct['matches']: #Going through matches in each post dict
                        tally(tokens_c, m['token'])
                        tally(parents_c, m['parent'])
                        tally(types_c, m['type'])
                tally(matchesperuser_c, nummatch)
            else:
                if f == 'matched_chats_list.pkl':
                    continue
                ustat = pickle.load(open('tagging_results_chats/{0}'.format(f), 'rb'))
                npost_zeromatch = int(ustat['posts']) - int(ustat['matched_posts'])
                matchesperpost_c[0] += npost_zeromatch
                tally(matchpostsperuser_c, ustat['matched_posts'])
    pickle.dump(matchesperpost_c, open("tag_analysis/matchesperpost_c.pkl", 'wb'))
    pickle.dump(matchesperuser_c, open("tag_analysis/matchesperuser_c.pkl", 'wb'))
    pickle.dump(matchpostsperuser_c, open("tag_analysis/matchpostsperuser_c.pkl", 'wb'))
    pickle.dump(tokens_c, open("tag_analysis/tokens_c.pkl", 'wb'))
    pickle.dump(parents_c, open("tag_analysis/parents_c.pkl", 'wb'))
    pickle.dump(types_c, open("tag_analysis/types_c.pkl", 'wb'))



#Next level: time evolution of specific term usage, distro of term within parent
