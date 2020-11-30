# coding=utf-8
#
# Util Functions
#
import os
import pandas as pd
import functools, pickle

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
from collections.abc import Mapping

try:
    import re2 as re
except ImportError:
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)

BASE_DICT_DIR = os.path.dirname(os.path.realpath(__file__)) + '/../../dictionaries/'


#
# Load Dictionaries
#
def loadDrugsDict():
    rfile_dictionary = BASE_DICT_DIR + '20150123-drug_name_dictionary.csv'
    rfile_references = BASE_DICT_DIR + '20150123-reference.csv'
    # Load Dictionary into Pandas
    dfD = pd.read_csv(rfile_dictionary, sep=',', encoding='utf-8')
    dfR = pd.read_csv(rfile_references, sep=',', encoding='utf-8')
    # Merge the Dictionary and References based on FOREIGH_KEY
    dfA = pd.merge(dfD, dfR, left_on='Original_ID', right_on='DB_ID')
    # Strip White Space
    dfA['Name'] = dfA['Name'].str.strip()
    return dfA


def loadCannabisDict():
    rfile = BASE_DICT_DIR + 'cannabis.csv'
    dfC = pd.read_csv(rfile, sep=',', encoding='utf-8')
    # Strip White Space
    dfC['token'] = dfC['token'].str.strip()
    dfC.rename(columns={'token': 'Name'}, inplace=True)
    return dfC


def loadHerbsDict():
    rfile = BASE_DICT_DIR + 'tcm_herbs.csv'
    dfH = pd.read_csv(rfile, sep=',', encoding='utf-8')
    # Strip White Space
    dfH['name'] = dfH['name'].str.strip()
    dfH.rename(columns={'name': 'Name'}, inplace=True)
    return dfH


def loadSymptomsDict(dictfile='meddra'):
    if dictfile == 'bicepp':
        rfile = BASE_DICT_DIR + 'bicepp_adverse_effects.csv'
        dfAE = pd.read_csv(rfile, sep=',', encoding='utf-8')
    elif dictfile == 'meddra':
        rfile = BASE_DICT_DIR + 'meddra.csv'
        dfAE = pd.read_csv(rfile, sep=',', index_col=0, encoding='utf-8')
        dfAE.columns = ['llt_code', 'Name', 'pt_code', 'Synonym', 'hlt_code', 'hlt_name']
    return dfAE


def loadEpilepsyDict():
    rfile = BASE_DICT_DIR + 'epilepsy.csv'
    dfEp = pd.read_csv(rfile, sep=',', encoding='utf-8')
    return dfEp


#
# Helper Function for 'constructDictsOfGoodTerms'
#
def update_dict(d, u, depth=-1):
    """
    Recursively merge or update dict-like objects.
    >>> update({'k1': {'k2': 2}}, {'k1': {'k2': {'k3': 3}}, 'k4': 4})
    {'k1': {'k2': {'k3': 3}}, 'k4': 4}
    """
    for k, v in u.items():
        # If u-value contains a dict
        if isinstance(v, Mapping) and not depth == 0:
            r = update_dict(d.get(k, {}), v, depth=max(depth - 1, -1))
            d[k] = r
        elif isinstance(d, Mapping):
            d[k] = u[k]
        else:
            d = {k: u[k]}
    return d


#
# Functions to handle Twitter text
# - remove everything after a retweet is seen
re_all_after_retweet = re.compile(r"rt @[a-zA-Z0-9_]+.+", re.IGNORECASE | re.UNICODE)


def removeAllAfterRetweet(text):
    return re_all_after_retweet.sub(text, '')


#
# Functions to handle Instagram Caption/Hashtag
# - Add spaces between hastags: #i#love#newyork -> #i #love #newyork
#
def addSpacesBetweenHashTags(text):
    if len(text) == 0:
        return ''

    # Add spaces if hashtags are togerther
    new_text = ''
    chars = set('#@')
    for i, c in enumerate(text, start=0):
        if (c in ['#', '@']) and (i > 0):
            if text[i - 1] != ' ':
                new_text += ' '
        new_text += c
    return new_text


# - combine Both Tags and Text Fields.
def combineTagsAndText(text, tags):
    text = addSpacesBetweenHashTags(text)
    tags = [tag for tag in tags if tag not in text]
    if len(tags):
        new_tags = '. '.join(['#' + w for w in tags])
        tagsandtext = text + '. ' + new_tags + '.'
    else:
        tagsandtext = text
    return tagsandtext


# - remove new lines
def removeNewLines(sentence):
    sentence = sentence.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    return sentence


# - remove content that was posted by another person using the @repostapp
re_repostapp = re.compile(r"(#Repost @\w+ with @repostapp)|(#EzRepost @\w+ with @ezrepostapp)|(Regrann from @\w+ -)")


def removeRepostApp(caption):
    m = re_repostapp.search(caption)
    if m:
        start, finish = m.span()
        return caption[:start]
    else:
        return caption


#
# Functions to handle social media text
# - Remove @mentions
re_atmention = re.compile(r"@[a-zA-Z0-9_]+")


def removeAtMention(text):
    return re_atmention.sub('', text)


#
# - remove # symbol
#
re_hashtagsymbol = re.compile(r"#([a-zA-Z0-9_]+)")


def removeHashtagSymbol(text):
    return re_hashtagsymbol.sub(r'\1', text)


# - Remove Links
re_links = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")


def removeLinks(text):
    return re_links.sub('', text)


#
# Ensure Folders Exists
#
def ensurePathExists(path):
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        print('-- Creating Folders: %s --' % (dirname))
        os.makedirs(dirname)


def load_save_return(dbname):
    def LS_decorator(func):
        @functools.wraps(func)
        def LS_wrapper(*args, **kwargs):
            # dbpath = os.path.join(godbpath, dbname)
            dbpath = dbname
            if os.path.isfile(dbpath):
                with open(dbpath, 'rb') as db_fp:
                    return pickle.load(db_fp)
            else:
                result = func(*args, **kwargs)
                with open(dbpath, 'wb') as db_fp:
                    pickle.dump(result, db_fp)
                return result

        return LS_wrapper

    return LS_decorator
