# -*- coding: utf-8 -*-
"""
Created on Thu May 23 10:00:12 2019

@author: Sikander
"""

import sys
sys.path.insert(0, '../../ddi_project/include')
sys.path.insert(0, '../../ddi_project/social/include')

from db_init_ddi_project import connectToMySQL
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

SAVE_DATA = 0
TIMERANGE = 0
DEMOGRAPHICS = 0
FORUMS_DISTR = 0
CHATS_DISTR = 0
DEMOGRAPHICS_2 = 0
MEMBER_TYPE = 0
FORUM_TOPICS = 0
TOP_USERS = 1

def tally(dct, key):
    if key in dct:
        dct[key] += 1
    else:
        dct[key] = 1

if SAVE_DATA == 1: #Saves datawarehoused tables to csv files for ease of access
    print '--- Loading MySQL table dw_chats ---'
    engine = connectToMySQL(server='mysql_epilepsy')
    chats = """SELECT c.uid, c.cid, c.type, c.chatroom, c.created
            FROM dw_chats c;"""
    df1 = pd.read_sql(chats, engine)
    df1.to_csv("chats.csv", index=False)

    print '--- Loading MySQL table dw_forums ---'
    forums = """SELECT f.uid, f.pid, f.type, f.topic, f.created
                FROM dw_forums f;"""
    df2 = pd.read_sql(forums, engine)
    df2.to_csv("forums.csv", index=False)

    print '--- Loading MySQL table dw_users ---'
    users = """SELECT u.uid, u.created, u.language, u.dob, u.member_type, u.my_epilepsy_control, u.country, u.state
            FROM dw_users u"""
    df3 = pd.read_sql(users, engine)
    df3.to_csv("users.csv", encoding='utf8', index=False)

if TIMERANGE == 1:
    #CHATS timerange
    rint
    '--- Loading MySQL table dw_chats ---'
    engine = connectToMySQL(server='mysql_epilepsy')
    chats = """SELECT c.uid, c.cid, c.type, c.chatroom, c.created
                FROM dw_chats c;"""
    df1 = pd.read_sql(chats, engine)
    df1 = df1.sort_values(by=['created'])
    df1.reset_index(inplace=True)
    #In order to find the first time stamp that isn't 1970-01-01 00:33:36
    num = df1.loc[0]['created']
    df2 = df1.loc[:][(df1['created'] > num)]
    print df2.head()
    #finds the latest timestamp
    num2 = int(df1.loc[len(df1) - 1]['created'])
    end = datetime.utcfromtimestamp(num2).strftime('%Y-%m-%d %H:%M:%S')
    print 'Last timestamp: ' + end
    #FORUMS timerange
    print
    '--- Loading MySQL table dw_forums ---'
    forums = """SELECT f.uid, f.pid, f.type, f.topic, f.created
                    FROM dw_forums f;"""
    df2 = pd.read_sql(forums, engine)
    df2 = df2.sort_values(by=['created'])
    df2.reset_index(inplace=True)
    num1 = int(df2.loc[0]['created'])
    num2 = int(df2.loc[len(df2) - 1]['created'])
    beg = datetime.utcfromtimestamp(num1).strftime('%Y-%m-%d %H:%M:%S')
    end = datetime.utcfromtimestamp(num2).strftime('%Y-%m-%d %H:%M:%S')
    print 'Time range of forums ' + beg + ' to ' + end

if DEMOGRAPHICS == 1:
    print
    '--- Loading MySQL table dw_users ---'
    engine = connectToMySQL(server='mysql_epilepsy')
    users = """SELECT u.uid, u.created, u.language, u.dob, u.member_type, u.my_epilepsy_control, u.country, u.state
                FROM dw_users u"""
    df = pd.read_sql(users, engine)
    df = df.sort_values(by=['created'])

    created = dict()
    dob = dict()
    lang = dict()
    type = dict()
    control = dict()
    country = dict()
    state = dict()

    count = 0
    #Dates of creation
    for ind, row in df.iterrows():
        creat = datetime.utcfromtimestamp(row['created']).strftime('%Y-%m-%d %H:%M:%S')
        creat = datetime.strptime(creat, '%Y-%m-%d %H:%M:%S')
        creat = creat.year
        tally(created, creat)
        #Dates of birth
        if isinstance(row['dob'], (int,float)) and row['dob'] >= 0:
            birth = datetime.utcfromtimestamp(row['dob']).strftime('%Y-%m-%d %H:%M:%S')
            birth = datetime.strptime(birth, '%Y-%m-%d %H:%M:%S')
            birth = birth.year
            tally(dob, birth)
        #Count number of negative timestamps
        if isinstance(row['dob'], (int,float)) and row['dob'] < 0:
            count += 1


        if row['language'] != np.nan:
            tally(lang, row['language'])

        tally(type, row['member_type'])
        tally(control, row['my_epilepsy_control'])
        tally(country, row['country'])
        tally(state, row['state'])

    print "Negative DOB timestamps: " + str(count)

    print created
    print dob
    print lang
    print type
    print control
    print country
    print state

if FORUMS_DISTR == 1: #Find distribution of number of posts
    print
    '--- Loading MySQL table dw_forums ---'
    engine = connectToMySQL(server='mysql_epilepsy')
    forums = """SELECT f.uid, f.pid, f.type, f.topic, f.created
                    FROM dw_forums f;"""
    df = pd.read_sql(forums, engine)
    df = df.sort_values(by=['created'])
    df.reset_index(inplace=True)

    #Create a list of dfs with one df per unique user
    gb = df.groupby('uid')
    grouplist = [gb.get_group(grp) for grp in gb.groups] #Each element in list is a df of all of one user's posts
    #Get distribution ofnumber of posts per users:
    postdstr = dict()
    for user in grouplist:
        num = len(user)
        tally(postdstr, num)

    print postdstr

if CHATS_DISTR == 1: #Find distribution of number of chats
    print
    '--- Loading MySQL table dw_chats ---'
    engine = connectToMySQL(server='mysql_epilepsy')
    chats = """SELECT c.uid, c.cid, c.type, c.chatroom, c.created
                FROM dw_chats c;"""
    df1 = pd.read_sql(chats, engine)
    df = df.sort_values(by=['created'])
    df.reset_index(inplace=True)

    #Create a list of dfs with one df per unique user
    gb = df.groupby('uid')
    grouplist = [gb.get_group(grp) for grp in gb.groups] #Each element in list is a df of all of one user's chats

    #Get distribution ofnumber of chats per users:
    chatdstr = dict()
    for user in grouplist:
        num = len(user)
        tally(chatdstr, num)

    print chatdstr

if DEMOGRAPHICS_2 == 1:
    print
    '--- Loading MySQL table dw_users ---'
    engine = connectToMySQL(server='mysql_epilepsy')
    users = """SELECT u.uid, u.created, u.language, u.dob, u.member_type, u.my_epilepsy_control, u.country, u.state
                FROM dw_users u"""
    df = pd.read_sql(users, engine)

    us_states = dict()
    gb_regions = dict()
    ca_provinces = dict()
    in_states = dict()
    au_states = dict()

    for ind, row in df.iterrows():
        #USA
        if row['country'] == 'US':
            tally(us_states, row['state'])
        #GB
        if row['country'] == 'GB':
            tally(gb_regions, row['state'])
        #Canada
        if row['country'] == 'CA':
            tally(ca_provinces, row['state'])
        #India
        if row['country'] == 'IN':
            tally(in_states, row['state'])
        #Australia
        if row['country'] == 'AU':
            tally(au_states, row['state'])

    print "US states: \n" + str(us_states)
    print "GB regions: \n" + str(gb_regions)
    print "Canada provinces: \n" + str(ca_provinces)
    print "India states: \n" + str(in_states)
    print "Australia states: \n" + str(au_states)

if MEMBER_TYPE == 1:
    print
    '--- Loading MySQL table dw_users ---'
    engine = connectToMySQL(server='mysql_epilepsy')
    users = """SELECT u.uid, u.created, u.language, u.dob, u.member_type, u.my_epilepsy_control, u.country, u.state
                    FROM dw_users u"""
    df = pd.read_sql(users, engine)
    df = df.sort_values(by=['created'])

    created_PLE = dict()
    created_PCE = dict()
    created_FMC = dict()
    created_HP = dict()
    dob_PLE = dict()
    dob_PCE = dict()
    dob_FMC = dict()
    dob_HP = dict()

    for ind, row in df.iterrows():
        if row['member_type'] == 'A Person Living with Epilepsy':
            creat = datetime.utcfromtimestamp(row['created']).strftime('%Y-%m-%d %H:%M:%S')
            creat = datetime.strptime(creat, '%Y-%m-%d %H:%M:%S')
            creat = creat.year
            tally(created_PLE, creat)
            if isinstance(row['dob'], (int,float)) and row['dob'] >= 0:
                birth = datetime.utcfromtimestamp(row['dob']).strftime('%Y-%m-%d %H:%M:%S')
                birth = datetime.strptime(birth, '%Y-%m-%d %H:%M:%S')
                birth = birth.year
                tally(dob_PLE, birth)
        elif row['member_type'] == 'A Parent of a Child with Epilepsy':
            creat = datetime.utcfromtimestamp(row['created']).strftime('%Y-%m-%d %H:%M:%S')
            creat = datetime.strptime(creat, '%Y-%m-%d %H:%M:%S')
            creat = creat.year
            tally(created_PCE, creat)
            if isinstance(row['dob'], (int,float)) and row['dob'] >= 0:
                birth = datetime.utcfromtimestamp(row['dob']).strftime('%Y-%m-%d %H:%M:%S')
                birth = datetime.strptime(birth, '%Y-%m-%d %H:%M:%S')
                birth = birth.year
                tally(dob_PCE, birth)
        elif row['member_type'] == 'A Family Member or Caregiver':
            creat = datetime.utcfromtimestamp(row['created']).strftime('%Y-%m-%d %H:%M:%S')
            creat = datetime.strptime(creat, '%Y-%m-%d %H:%M:%S')
            creat = creat.year
            tally(created_FMC, creat)
            if isinstance(row['dob'], (int,float)) and row['dob'] >= 0:
                birth = datetime.utcfromtimestamp(row['dob']).strftime('%Y-%m-%d %H:%M:%S')
                birth = datetime.strptime(birth, '%Y-%m-%d %H:%M:%S')
                birth = birth.year
                tally(dob_FMC, birth)
        elif row['member_type'] == 'Healthcare Professional':
            creat = datetime.utcfromtimestamp(row['created']).strftime('%Y-%m-%d %H:%M:%S')
            creat = datetime.strptime(creat, '%Y-%m-%d %H:%M:%S')
            creat = creat.year
            tally(created_HP, creat)
            if isinstance(row['dob'], (int,float)) and row['dob'] >= 0:
                birth = datetime.utcfromtimestamp(row['dob']).strftime('%Y-%m-%d %H:%M:%S')
                birth = datetime.strptime(birth, '%Y-%m-%d %H:%M:%S')
                birth = birth.year
                tally(dob_HP, birth)

    print "---- CREATED ----"
    print "Person Living with Epilepsy: \n" + str(created_PLE)
    print "A Parent of a Child with Epilepsy: \n" + str(created_PCE)
    print "A Family Member or Caregiver: \n" + str(created_FMC)
    print "Healthcare Professional: \n" + str(created_HP)
    print "---- DOB ----"
    print "Person Living with Epilepsy: \n" + str(dob_PLE)
    print "A Parent of a Child with Epilepsy: \n" + str(dob_PCE)
    print "A Family Member or Caregiver: \n" + str(dob_FMC)
    print "Healthcare Professional: \n" + str(dob_HP)

    #LEVEL OF ENGAGEMENT OF DIFFERENT MEMBER TYPES
    gb = df.groupby('member_type')
    grouplist = [gb.get_group(grp) for grp in gb.groups]

    PLE = []
    PCE = []
    FMC = []
    HP = []
    for type in grouplist:
        if type.loc[0]['member_type'] == 'A Person Living with Epilepsy':
            for ind, row in type.iterrows():
                PLE.append(row['uid'])
        elif type.loc[0]['member_type'] == 'A Parent of a Child with Epilepsy':
            for ind, row in type.iterrows():
                PCE.append(row['uid'])
        elif type.loc[0]['member_type'] == 'A Family Member or Caregiver':
            for ind, row in type.iterrows():
                FMC.append(row['uid'])
        elif type.loc[0]['member_type'] == 'Healthcare Professional':
            for ind, row in type.iterrows():
                HP.append(row['uid'])

    dfF = pd.read_csv("forums.csv")
    dfC = pd.read_csv("chats.csv")

    posts_PLE = dict()
    posts_PCE = dict()
    posts_FMC = dict()
    posts_HP = dict()
    chats_PLE = dict()
    chats_PCE = dict()
    chats_FMC = dict()
    chats_HP = dict()

    gbF = dfF.groupby('uid')
    groupsF = [gbF.get_group(grp) for grp in gbF.groups]
    gbC = dfC.groupby('uid')
    groupsC = [gbC.get_group(grp) for grp in gbC.groups]

    for user in groupsF:
        if user.loc[0]['uid'] in PLE:
            num = len(user)
            tally(posts_PLE, num)
        elif user.loc[0]['uid'] in PCE:
            num = len(user)
            tally(posts_PCE, num)
        elif user.loc[0]['uid'] in FMC:
            num = len(user)
            tally(posts_FMC, num)
        elif user.loc[0]['uid'] in HP:
            num = len(user)
            tally(posts_HP, num)
    for user in groupsC:
        if user.loc[0]['uid'] in PLE:
            num = len(user)
            tally(chats_PLE, num)
        elif user.loc[0]['uid'] in PCE:
            num = len(user)
            tally(chats_PCE, num)
        elif user.loc[0]['uid'] in FMC:
            num = len(user)
            tally(chats_FMC, num)
        elif user.loc[0]['uid'] in HP:
            num = len(user)
            tally(chats_HP, num)

    print posts_PLE
    print posts_PCE
    print posts_FMC
    print posts_HP
    print chats_PLE
    print chats_PCE
    print chats_FMC
    print chats_HP

if FORUM_TOPICS:
    engineE = connectToMySQL(server='mysql_epilepsy')
    print '----- Loading MySQL table dw_forums -----'
    forums = """SELECT f.pid, f.uid, f.topic
                FROM dw_forums f"""
    dfF = pd.read_sql(forums, engineE)
    gbF = dfF.groupby('topic')
    grplistF = [gbF.get_group(grp) for grp in gbF.groups]
    topic_dct = {}
    for topic in grplistF:
        topic.reset_index(inplace=True)
        name = topic.loc[0]['topic']
        num = len(topic)
        topic_dct[name] = num
    print topic_dct

usrs_chats = {124741: 3159,142931: 3188,206786: 3234, 91813: 3614, 133186: 3632, 102710: 3699,
              74879: 3753, 226796: 3846, 123406: 3906, 103467: 4204, 93147: 4258, 168131: 4631,
              117586: 4719, 153391: 5356, 203441: 5358, 123996: 6112, 87564: 7539, 95416: 7711,
              44294: 10456, 98914: 11613, 188006: 14238, 90109: 17011, 94861: 18854, 23487: 20288,
              214556: 22108, 40886: 45498}
usrs_forums =  {13600: 336,2495: 349,12416: 350,39104: 353, 22834: 360, 15797: 395,
                70585: 399, 16756: 413, 26464: 457, 33641: 568, 3421: 605, 1837: 655,
                42622: 692, 43851: 698, 10112: 713, 27976: 734, 53211: 918, 13993: 1022,
                2731: 1034, 1998: 1091, 40321: 1195, 51501: 1528, 101498: 1609, 0: 4284}

if TOP_USERS == 1:
    clist = []
    flist = []
    engineE = connectToMySQL(server='mysql_epilepsy')
    for u in usrs_chats:
        print '> Loading user {0}'.format(u)
        user = """SELECT u.uid, u.realname, u.username, u.first_name, u.last_name
                FROM dw_users u
                WHERE u.uid = {0};""".format(u)
        dfU = pd.read_sql(user, engineE, index_col='uid')
        dct = dfU.to_dict('index')
        clist.append(dct)
    for u in usrs_forums:
        print '> Loading user {0}'.format(u)
        user = """SELECT u.uid, u.realname, u.username, u.first_name, u.last_name
                FROM dw_users u
                WHERE u.uid = {0};""".format(u)
        dfU = pd.read_sql(user, engineE, index_col='uid')
        dct = dfU.to_dict('index')
        flist.append(dct)
    print 'Top Chat Users: \n' + str(clist)
    print 'Top Forum Users: \n' + str(flist) 
