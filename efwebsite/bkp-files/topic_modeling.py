# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 13:12:09 2020

@author: Sikander
"""

import sys
sys.path.insert(0, '../ddi_project/include')
sys.path.insert(0, '../ddi_project/social/include')

import db_init as db
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation

TF_IDF = 1
# LDA = 1
# N_M_F = 1

def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        message = "Topic #%d: " % topic_idx
        message += " ".join([feature_names[i]
                             for i in topic.argsort()[:-n_top_words - 1:-1]])
        print(message)
    print()

if TF_IDF == 1:
    engineE = db.connectToMySQL(server='mysql_epilepsy')

    print '--- Loading MySQL table dw_forums ---'
    forums = """SELECT f.pid, SUBSTRING_INDEX(f.pid, "|", 1) AS onlypid,
				f.parentid, f.uid, f.type, f.topicid, f.topic, f.created, f.text_original
	            FROM dw_forums f;"""
    dfF = pd.read_sql(forums, engineE)

    gbF = dfF.groupby('onlypid')
    threadlist = [gbF.get_group(grp) for grp in gbF.groups]
    # gbC = dfC.groupby('uid')
    # grouplistC = [gbC.get_group(grp) for grp in gbC.groups]
    n_threads = len(threadlist)
    current = 1
    all_docs = []
    thread_names = []
    for thread in threadlist:
        thread = thread.set_index(pd.to_datetime(thread['created'], unit='s'), drop=False)
        thread = thread.sort_index(ascending=True)
        thread_name = thread.iloc[0]['onlypid']
        thread_names.append(thread_name)
        print '> Parsing thread {0} ({1} of {2})'.format(thread_name,  current, n_threads)
        current += 1
        # topic = topic.set_index(pd.to_datetime(topic['created'], unit='s'), drop=False) #Do we need parameter drop=False?
        # topic = topic.sort_index(ascending=True)
        # n_posts = topic.shape[0]
        text_list = []
        for creat_time, post in thread.iterrows():
            #date = created_time.strftime('%Y-%m-%d')
            # post_id = post['onlypid']
            text = post['text_original']
            text_list.append(text)
        thread_doc = " ".join(txt for txt in text_list) #joins all posts in a topic
        all_docs.append(thread_doc)

    n_top_words = 20
    n_comps = 10
    n_features = 1000
    n_top_words = 20

    print '> Begin TF-IDF'

    tfidf_vectorizer = TfidfVectorizer(max_df=0.65, min_df=10, stop_words='english', decode_error='ignore', strip_accents='unicode')
    tfidf = tfidf_vectorizer.fit_transform(all_docs)
    print '> Saving TF-IDF'
    print type(tfidf)
    pickle.dump(tfidf, open("nlp/tfidf.pkl", 'wb'))
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()
    # transformed_documents_as_array = tfidf.toarray()
    # print '> End TF-IDF'
    # # topic_dct = {}
    # for counter, doc in enumerate(transformed_documents_as_array):
    #     # construct a dataframe
    #     tf_idf_tuples = list(zip(tfidf_vectorizer.get_feature_names(), doc))
    #     one_doc_as_df = pd.DataFrame.from_records(tf_idf_tuples, columns=['term', 'score']).sort_values(by='score', ascending=False).reset_index(drop=True)
    #     # output to a csv using the enumerated value for the filename
    #     # tpc_nm = topic_names[counter].encode("ascii", "ignore").decode('ascii') #''.join(filter(str.isalnum, str(topic_names[counter])))
    #     # print tpc_nm
    #     one_doc_as_df.to_csv("nlp/tfidf_thread{0}.csv".format(thread_names[counter]), encoding='utf-8')
    #     # topic_dct[counter] = topic_names[counter]
    #     # pickle.dump(one_doc_as_df, open("{0}.pkl".format(counter), 'wb'))
    # # pickle.dump(topic_dct, open("topic_number_dct.pkl", 'wb'))
    print '> Begin TF'

    tf_vectorizer = CountVectorizer(max_df=0.65, min_df=10, max_features=n_features,stop_words='english', decode_error='ignore', strip_accents='unicode')
    tf = tf_vectorizer.fit_transform(all_docs)
    tf_feature_names = tf_vectorizer.get_feature_names()

    print '> End TF'
    print '> Calculating NMF (Frobenius)...'

    nmf_f = NMF(n_components=n_comps, random_state=1,alpha=.1, l1_ratio=.5).fit(tfidf)
    print '> Calculating NMF (Kullback-Leibler)...'
    nmf_kl = NMF(n_components=n_comps, random_state=1,
          beta_loss='kullback-leibler', solver='mu', max_iter=1000, alpha=.1,
          l1_ratio=.5).fit(tfidf)
    print '> Calculating LDA...'
    lda = LatentDirichletAllocation(n_components=n_comps, max_iter=5,
                                learning_method='online',
                                learning_offset=50.,
                                random_state=0)
    lda.fit(tf)
    print "Topics in NMF model (Frobenius norm) fitted with tf-idf features"
    print_top_words(nmf_f, tfidf_feature_names, n_top_words)
    print "Topics in NMF model (generalized Kullback-Leibler divergence) fitted with tf-idf features"
    print_top_words(nmf_kl, tfidf_feature_names, n_top_words)


    print "Topics in LDA model fitted with tf features"
    print_top_words(lda, tf_feature_names, n_top_words)
