# coding=utf-8
# Author: Rion B Correia
# Date: March 26, 2015
# Updated: December 06, 2016
# 
# Description: 
# Database Connection to both Mysql and Mongo
#
#
import os
import warnings
import json
from urllib.parse import quote_plus
# Mysql
import pymysql
import sqlalchemy
# Mongo
import pymongo
from pymongo import MongoClient

# Enable Deprecation Warnings
warnings.simplefilter('always', DeprecationWarning)

#
# Load DB Configuration File
#
with open(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'db_config.json'))) as f:
    CONFIGS = json.load(f)


#
# Connect to MySQL DB
#
def connectToMySQL(server, verbose=False, *args, **kwargs):
    if verbose:
        print('--- Connecting to MySQL DB: %s ---' % (server))

    # Get the correct MySQL Server configuration. Or throws an error.
    if server not in CONFIGS:
        raise ValueError('Database server `%s` not defined in `db_config.json`.' % (server))
    else:
        CONFIG = CONFIGS[server]

    url = 'mysql+pymysql://%(user)s:%(password)s@%(host)s/%(database)s?charset=utf8' % CONFIG
    engine = sqlalchemy.create_engine(url, encoding='utf-8', *args, **kwargs)

    return engine


def connectToPostgreSQL(server, verbose=False, *args, **kwargs):
    if verbose:
        print('--- Connecting to PostgreSQL DB: %s ---' % (server))

    # Get the correct MySQL Server configuration. Or throws an error.
    if server not in CONFIGS:
        raise ValueError('Database server `%s` not defined in `db_config.json`.' % (server))
    else:
        CONFIG = CONFIGS[server]

    url = 'postgresql+psycopg2://%(user)s:%(password)s@%(host)s:%(port)s/%(database)s' % CONFIG
    engine = sqlalchemy.create_engine(url, encoding='utf-8', *args, **kwargs)

    return engine


#
# Connect ot Mongo DB
#
def connectToMongoDB(server, db, verbose=False, *args, **kwargs):
    if verbose:
        print('--- Connecting to MongoDB: %s:%s ---' % (server, db))

    if server not in CONFIGS:
        raise ValueError('Database server `%s` not defined in `db_config.json`.' % (server))
    else:
        CONFIG = CONFIGS[server].copy()

    # Has Authentication
    if 'user' in CONFIG and 'password' in CONFIG:
        CONFIG['user'] = quote_plus(CONFIG['user'])
        CONFIG['password'] = quote_plus(CONFIG['password'])
        url = 'mongodb://%(user)s:%(password)s@%(host)s/?authMechanism=SCRAM-SHA-1&authSource=admin' % CONFIG
    else:
        url = 'mongodb://%(host)s' % CONFIG

    client = MongoClient(url, *args, **kwargs)
    try:
        cnx = client[db]
    except Exception as e:
        raise e
    else:
        return cnx, client


#
# Disconnects from the DBs
#
def disconnectFromMySQLDB(cnx):
    print('--- Disconnecting MySQL DB ---')
    cnx.close()


#
#
#
def disconnectFromMongoDB(cnx):
    print('--- Disconnecting Mongo DB ---')
    cnx.disconnect()
