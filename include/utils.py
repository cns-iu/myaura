# coding=utf-8
# Author: Rion B Correia & Xuan Wang
# Date: Jan 06, 2021
#
# Description: Utility functions
#
import os
import re
import functools
import pickle
import numpy as np

#
# Functions to handle Twitter text
#
re_all_after_retweet = re.compile(r"rt @[a-zA-Z0-9_]+.+", re.IGNORECASE | re.UNICODE)


def removeAllAfterRetweet(text):
    """ Remove everything after a retweet is seen."""
    return re_all_after_retweet.sub(text, '')


#
# Functions to handle Instagram Caption/Hashtag
#
re_repostapp = re.compile(r"(#Repost @\w+ with @repostapp)|(#EzRepost @\w+ with @ezrepostapp)|(Regrann from @\w+ -)")


def addSpacesBetweenHashTags(text):
    """ Add spaces between hastags: #i#love#newyork -> #i #love #newyork """
    if len(text) == 0:
        return ''

    # Add spaces if hashtags are togerther
    new_text = ''
    for i, c in enumerate(text, start=0):
        if (c in ['#', '@']) and (i > 0):
            if text[i - 1] != ' ':
                new_text += ' '
        new_text += c
    return new_text


def combineTagsAndText(text, tags):
    """ Combine Both Tags and Text Fields."""
    text = addSpacesBetweenHashTags(text)
    tags = [tag for tag in tags if tag not in text]
    if len(tags):
        new_tags = '. '.join(['#' + w for w in tags])
        tagsandtext = text + '. ' + new_tags + '.'
    else:
        tagsandtext = text
    return tagsandtext


def removeNewLines(sentence):
    """ Remove new lines """
    sentence = sentence.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    return sentence


def removeRepostApp(caption):
    """ Remove content that was posted by another person using the @repostapp """
    m = re_repostapp.search(caption)
    if m:
        start, finish = m.span()
        return caption[:start]
    else:
        return caption


#
# Functions to handle general social media text
#
re_atmention = re.compile(r"@[a-zA-Z0-9_]+")
re_hashtagsymbol = re.compile(r"#([a-zA-Z0-9_]+)")
re_links = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")


def removeAtMention(text):
    """ Remove @mentions"""
    return re_atmention.sub('', text)


def removeHashtagSymbol(text):
    """ # - remove # symbol """
    return re_hashtagsymbol.sub(r'\1', text)


def removeLinks(text):
    """ remove links from text """
    return re_links.sub('', text)


#
# File handling functions
#
def ensurePathExists(path):
    """ Ensure path exists."""
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        print('-- Creating Folders: %s --' % (dirname))
        os.makedirs(dirname)


def load_save_return(dbname):
    """ What does this do? """
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


#
# Network functions
#
def prox2dist(p):
    """Transforms a non-negative ``[0,1]`` proximity to distance in the ``[0,inf]`` interval:

    Args:
        p (float): proximity value

    Returns:
        d (float): distance value
    """
    if (p == 0):
        return np.inf
    else:
        return (1 / float(p)) - 1
