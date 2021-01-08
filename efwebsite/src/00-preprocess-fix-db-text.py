# coding: utf-8
# Author: Rion B Correia
# Date: 07 Jan 2021
#
# Description:
# Preprocess, cleans, the text on the DB.
#
import os
import sys
#
#include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'include'))
include_path = '/nfs/nfs7/home/rionbr/myaura/include'
sys.path.insert(0, include_path)
#
import pandas as pd
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
import re
import string
import nltk
# from nltk.corpus import wordnet
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
#
import multiprocessing
from multiprocessing import Pool
#
import db_init as db

#
# Regular Expression Definitions
#
re_tags = re.compile(r'<.*?>')
re_punctuation = re.compile(r'[%s]' % re.escape(string.punctuation))  # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
re_url = re.compile(r'((http|https)(\:\/\/))?[a-zA-Z0-9\-\.]+\.(com|org|net|gov|int|edu|mil|arpa)(.[a-z]{2})?(\/\S*)?\b')
# re_age = re.compile(r'\b(\d+)\b( and \b\d+\b)? (years|year|yr|y) (old|o)\b')
re_drugnumber = re.compile(r'(\d+) ?(mg/ml|mg|kg|mcg/kg/hour|mcg/kg/minute|mcg/kg)')
re_number = re.compile(r'\b\d+\b')


def preprocess_text(s):
    # all lowercase
    s = s.lower()
    # remove tags
    s = re_tags.sub(' ', s)
    # remove &nbsp;
    s = s.replace(u'&nbsp;', ' ')
    # transform url into tags
    s = re_url.sub('<url>', s)
    # remove new lines
    s = s.replace('\n', '').replace('\r', '')
    # remove double spaces
    s = ' '.join(s.split())
    #  transforming age
    # s = re_age.sub('<age>', s)
    # transforming numbers used in drug quantity
    s = re_drugnumber.sub('<unit>', s)
    # transforming numbers
    s = re_number.sub('<number>', s)
    # remove punctuation
    # s = re_punctuation.sub(' ', s)
    return s


re_MS_xmltag = re.compile(r'<xml>((.|\n)*)<\/xml>')
re_MS_iftag = re.compile(r'<!--\[if((.|\n)*)<!\[endif\]-->')
re_MS_metatag = re.compile(r'<meta .*\/>')
re_MS_linktag = re.compile(r'<link .*\/>')


def preprocess_removeMSWord(s):
    # Remove <xml>content</xml>
    s = re_MS_xmltag.sub('', s)
    # Remove <!--[if content [endif]--!> tag
    s = re_MS_iftag.sub('', s)
    # Remove <meta /> tag
    s = re_MS_metatag.sub('', s)
    # Remove <link /> tag
    s = re_MS_linktag.sub('', s)

    return s


# User Specific RE
re_USER_53211 = re.compile(r'(^Baruch Hashem)((.|\n)*)')


def get_wordnet_pos(treebank_tag):
    """ Return the correct object dependin on the pos_tag"""
    # ADJ, ADJ_SAT, ADV, NOUN, VERB = 'a', 's', 'r', 'n', 'v'
    # POS_LIST = [NOUN, VERB, ADJ, ADV]
    if treebank_tag.startswith('J'):
        return 'a'
    elif treebank_tag.startswith('V'):
        return 'v'
    elif treebank_tag.startswith('N'):
        return 'n'
    elif treebank_tag.startswith('R'):
        return 'r'
    else:
        return False


def _worker_clean(text_original, uid):
    text_clean = preprocess_removeMSWord(text_original)
    # User Manual Fix
    # if uid == '53211':
    #   s = re_USER_53211.sub('', text_clean)
    text_clean = preprocess_text(text_clean)

    return text_clean


def _worker_token(text_clean):
    text_tokens = tokenizer.tokenize(text_clean)
    return text_tokens


def _worker_tag(text_tokens):
    text_tagged = nltk.pos_tag(text_tokens)
    return text_tagged


def _worker_lem(text_tagged):
    text_lemmed = list()
    for w, t in text_tagged:
        wordnet_pos = get_wordnet_pos(t)
        if wordnet_pos:
            w = lemmatizer.lemmatize(w, pos=wordnet_pos)
        else:
            w = lemmatizer.lemmatize(w)
        text_lemmed.append(w)
    text_lemmed = u' '.join(text_lemmed)
    return text_lemmed


def _worker_stem(text_tagged):
    text_stemmed = [stemmer.stem(w) for w in text_tagged]
    text_stemmed = ' '.join(text_stemmed)
    return text_stemmed


if __name__ == '__main__':

    engine = db.connectToMySQL(server='etrash-mysql-epilepsy')

    #tokenizer = RegexpTokenizer(r'<url>|<number>|<unit>|\w+')
    #lemmatizer = WordNetLemmatizer()
    #stemmer = SnowballStemmer("english")

    # Generally Fix HTML code
    indexes = ['pid', 'cid']
    selects = [
        'SELECT pid, uid, text_original FROM dw_forums',
        'SELECT cid, uid, text_original FROM dw_chats'
    ]
    updates = [
        'UPDATE dw_forums SET text_clean = %s WHERE pid = %s',
        'UPDATE dw_chats SET text_clean = %s WHERE cid = %s'
    ]

    for index, sql_select, sql_update in zip(indexes, selects, updates):

        dfP = pd.read_sql(sql_select, engine, index)
        n_rows = dfP.shape[0]

        print('--- Computing ---')

        #
        # Parallel Processing
        #
        n_cores = int(multiprocessing.cpu_count() / 4)
        # Clean
        print('- Clean')
        pool_clean = Pool(processes=n_cores)
        texts_clean = [pool_clean.apply_async(_worker_clean, args=(text_original, uid)) for text_original, uid in dfP[['text_original', 'uid']].values]
        texts_clean = [p.get() for p in texts_clean]
        dfP['text_clean'] = texts_clean
        # print dfP.head()

        """
        # Tokenize
        print('- Tokenize')
        pool_token = Pool(processes=n_cores)
        texts_token = [pool_token.apply_async(_worker_token, args=(text_clean,)) for text_clean in texts_clean]
        texts_token = [p.get() for p in texts_token]
        dfP['text_token'] = texts_token
        # print dfP.head()

        # POS-Tag
        print('- POS-Tag')
        pool_tag = Pool(processes=n_cores)
        texts_tag = [pool_tag.apply_async(_worker_tag, args=(text_token,)) for text_token in texts_token]
        texts_tag = [p.get() for p in texts_tag]
        dfP['text_tag'] = texts_tag
        # print dfP.head()

        # Lemmatize
        print('- Lemmatize')
        pool_lemma = Pool(processes=n_cores)
        texts_lemmed = [pool_lemma.apply_async(_worker_lem, args=(text_tag,)) for text_tag in texts_tag]
        texts_lemmed = [p.get() for p in texts_lemmed]
        dfP['text_lemmed'] = texts_lemmed
        # print dfP.head()

        # Stemming
        print('- Stemmming')
        pool_stemm = Pool(processes=n_cores)
        texts_stemmed = [pool_stemm.apply_async(_worker_stem, args=(text_token,)) for text_token in texts_token]
        texts_stemmed = [p.get() for p in texts_stemmed]
        dfP['text_stemmed'] = texts_stemmed
        # print dfP.head()
        """
        #
        # Sequential Processing
        #
        """
        for i, (_id, dft) in enumerate(dfP.iterrows(), start=1):
            if (i%100 == 0):
                print 'updating: %d of %d' % (i, n_rows)
            uid = dft['uid']
            text_original = dft['text_original']

            #
            text_clean = preprocess_removeMSWord(text_original)

            # User Manual Fix
            if uid == '53211':
                s = re_USER_53211.sub('', text_clean)

            text_clean = preprocess_text(text_clean)
            text_tokens = tokenizer.tokenize(text_clean)
            text_tagged = nltk.pos_tag(text_tokens)
            text_lemmed = list()
            for w,t in text_tagged:
                wordnet_pos = get_wordnet_pos(t)
                if wordnet_pos:
                    w = lemmatizer.lemmatize(w, pos=wordnet_pos)
                else:
                    w = lemmatizer.lemmatize(w)
                text_lemmed.append(w)
            text_lemmed = u' '.join(text_lemmed)
            text_stemmed = [ stemmer.stem(w) for w in text_tokens]
            text_stemmed = ' '.join(text_stemmed)

            data = (text_clean, text_lemmed, text_stemmed, _id)
            engine.execute(sql_update, data)
        """
        #
        # Update the DB
        #
        print('--- Updating the DB ---')
        for i, (_id, dft) in enumerate(dfP.iterrows(), start=1):

            text_clean = dft['text_clean']
            #text_lemmed = dft['text_lemmed']
            #text_stemmed = dft['text_stemmed']

            data = (text_clean, _id)
            engine.execute(sql_update, data)
