# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 11:46:52 2019

@author: Sikander
"""

import sys
sys.path.insert(0, '../ddi_project/include')
sys.path.insert(0, '../ddi_project/social/include')

from db_init_ddi_project import connectToMySQL
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil import rrule

##SWITCHES
BUILD_TIMELINES = 0
TIMELINE_ARRAY = 0
ALL_TLS = 0
WEEKLY_TL_ARR = 1

#FUNCTIONS
def tally(dct, key):
    if key in dct:
        dct[key] += 1
    else:
        dct[key] = 1

def convertDateTime(timestamp):
    dt = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    return dt

def monthDiff(beg, end):
    return (end.year - beg.year)*12 + end.month - beg.month

def weeks_between(start_date, end_date):
    weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date)
    return weeks.count()
    # wk_count = (start_date - end_date).days//7
    # return wk_count

def timelineArray(df, name, threshold, weekly=False):
    """Creates an array of user timelines, binned by month or week"""
    df = df.sort_values(by=['created'])
    earliest = convertDateTime(df.loc[0]['created'])
    df.reset_index(inplace=True)
    df.drop(columns=['index'])
    # print "Head and tail before"
    # print df.head()
    # print df.tail()
    #remove chats with timestamp in the year 1970
    if earliest.year > 1970:
        usr_grps = df.groupby('uid')
        rawlist = [usr_grps.get_group(grp) for grp in usr_grps.groups]
    else:
        num = df.loc[0]['created']
        df = df.loc[:][(df['created'] > num)]
        df.reset_index(inplace=True)
        df.drop(columns=['index'])
        earliest = convertDateTime(df.loc[0]['created'])
        usr_grps = df.groupby('uid')
        rawlist = [usr_grps.get_group(grp) for grp in usr_grps.groups]
    # print "Head and tail after"
    # print df.head()
    # print df.tail()
    #Find number of month diffference between first and last post/chat
    latest = convertDateTime(df.loc[len(df) - 1]['created'])
    if weekly:
        t_range = weeks_between(earliest, latest)
        print "Earliest: " + str(earliest)
        print "Latest: " + str(latest)
        print "Timerange of " + str(t_range) + " weeks for " + name
    else:
        t_range = monthDiff(earliest, latest)
        print "Earliest: " + str(earliest)
        print "Latest: " + str(latest)
        print "Timerange of " + str(t_range) + " months for " + name
    #Take out low activity USERS
    userlist = []
    for user in rawlist:
        if len(user) > threshold:
            userlist.append(user)
    #Number of users
    num_usrs = len(userlist)
    print str(num_usrs) + " users for " + name
    #Sort user list by number of posts/chats and print uids
    userlist.sort(key=len)
    uids = dict()
    for user in userlist:
        user.reset_index(inplace=True)
        user.drop(columns=['index'])
    timelines=np.zeros((num_usrs,t_range+1), dtype=int)
    ar_row = 0
    for user in userlist:
        for ind, row in user.iterrows():
            date = convertDateTime(row['created'])
            if weekly:
                col = weeks_between(earliest, date)
            else:
                col = monthDiff(earliest, date)
            if col < 0:
                continue
            timelines[ar_row][col] += 1
        ar_row += 1
    np.save(name, timelines)


if BUILD_TIMELINES == 1:
    engineE = connectToMySQL(server='mysql_epilepsy')
	print '--- Loading MySQL table dw_forums ---'
	forums = """SELECT f.pid, f.parentid, f.uid, f.type, f.topic, f.created, f.text_original
	            FROM dw_forums f;"""
    print '--- Loading MySQL table dw_chats ---'
    chats = """SELECT c.pid, c.parentid, c.uid, c.type, c.topic, c.created, c.text_original
            	            FROM dw_chats c;"""
	dfF = pd.read_sql(forums, engineE)
    dfC = pd.read_sql(chats, engineE)

    gbF = dfF.groupby('uid')
    grouplistF = [gbF.get_group(grp) for grp in gbF.groups]
    gbC = dfC.groupby('uid')
    grouplistC = [gbC.get_group(grp) for grp in gbC.groups]

    for user in grouplistF:
        user = user.sort_values(by=['created'])
        user.reset_index(inplace=True)
        user.drop(columns=['index'])
        # uid = str(user.loc[0]['uid'])
        # user.to_csv("forum_timilines/{0}.csv".format(uid), index=False)

    for user in grouplistC:
        user = user.sort_values(by=['created'])
        user.reset_index(inplace=True)
        user.drop(columns=['index'])
        #uid = str(user.loc[0]['uid'])
        #user.to_csv("forum_timilines/{0}.csv".format(uid), index=False)

if TIMELINE_ARRAY == 1:
    engineE = connectToMySQL(server='mysql_epilepsy')
	print '--- Loading MySQL table dw_forums ---'
	forums = """SELECT f.pid, f.parentid, f.uid, f.type, f.topic, f.created, f.text_original
	            FROM dw_forums f;"""
    print '--- Loading MySQL table dw_chats ---'
    chats = """SELECT c.pid, c.parentid, c.uid, c.type, c.topic, c.created, c.text_original
            	            FROM dw_chats c;"""
	dfF = pd.read_sql(forums, engineE)
    dfC = pd.read_sql(chats, engineE)

    print "----Creating timeline array for forums----"
    timelineArray(dfF, "forums_tl", 37) #Gives top 317 users (1.4% of posters)
    print "----Creating timeline array for chats----"
    timelineArray(dfC, "chats_tl", 76) #gives top 315 users (16% of users)

if ALL_TLS == 1:
    print "---- Loading chats and forums ----"
    engineE = connectToMySQL(server='mysql_epilepsy')
	print '--- Loading MySQL table dw_forums ---'
	forums = """SELECT f.pid, f.parentid, f.uid, f.type, f.topic, f.created, f.text_original
	            FROM dw_forums f;"""
    print '--- Loading MySQL table dw_chats ---'
    chats = """SELECT c.pid, c.parentid, c.uid, c.type, c.topic, c.created, c.text_original
            	            FROM dw_chats c;"""
	dfF = pd.read_sql(forums, engineE)
    dfC = pd.read_sql(chats, engineE)

    print "----Creating timeline array for forums----"
    timelineArray(dfF, "forums_tl_all", 0)
    print "----Creating timeline array for chats----"
    timelineArray(dfC, "chats_tl_all", 0)

if WEEKLY_TL_ARR == 1:
    engineE = connectToMySQL(server='mysql_epilepsy')
	print '--- Loading MySQL table dw_forums ---'
	forums = """SELECT f.pid, f.parentid, f.uid, f.type, f.topic, f.created, f.text_original
	            FROM dw_forums f;"""
    print '--- Loading MySQL table dw_chats ---'
    chats = """SELECT c.pid, c.parentid, c.uid, c.type, c.topic, c.created, c.text_original
            	            FROM dw_chats c;"""
	dfF = pd.read_sql(forums, engineE)
    dfC = pd.read_sql(chats, engineE)

    print "----Creating timeline array for forums----"
    timelineArray(dfF, "forums_tl_wkly", 0, weekly=True)
    print "----Creating timeline array for chats----"
    timelineArray(dfC, "chats_tl_wkly", 0, weekly=True)
