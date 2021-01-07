# coding=utf-8
# Author: Rion B Correia & Xuan Wang
# Date: Jan 06, 2021
#
# Description: Database connection to Postgress, Mysql and Mongo
#
import os
import configparser
from urllib.parse import quote_plus
import sqlalchemy
from pymongo import MongoClient


# Load DB Configuration File
f = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'db_config.ini'))
configs = configparser.ConfigParser()
configs.read(f)


def connectToMySQL(server, verbose=False, *args, **kwargs):
    """ Connects to MySQL."""
    if verbose:
        print('--- Connecting to MySQL DB: %s ---' % (server))

    # Get the correct MySQL Server configuration. Or throws an error.
    if server not in configs:
        raise ValueError('Database server `%s` not defined in `db_config.ini`.' % (server))
    else:
        config = configs[server]

    url = 'mysql+pymysql://%(user)s:%(password)s@%(host)s/%(database)s?charset=utf8' % config
    engine = sqlalchemy.create_engine(url, encoding='utf-8', *args, **kwargs)

    return engine


def connectToPostgreSQL(server, verbose=False, *args, **kwargs):
    """ Connects to Postgres."""
    if verbose:
        print('--- Connecting to PostgreSQL DB: %s ---' % (server))

    # Get the correct MySQL Server configuration. Or throws an error.
    if server not in configs:
        raise ValueError('Database server `%s` not defined in `db_config.ini`.' % (server))
    else:
        config = configs[server]

    url = 'postgresql+psycopg2://%(user)s:%(password)s@%(host)s:%(port)s/%(database)s' % config
    engine = sqlalchemy.create_engine(url, encoding='utf-8', *args, **kwargs)

    return engine


def connectToMongoDB(server, db, verbose=False, *args, **kwargs):
    """ Connects ot Mongo."""
    if verbose:
        print('--- Connecting to MongoDB: %s:%s ---' % (server, db))

    if server not in configs:
        raise ValueError('Database server `%s` not defined in `db_config.ini`.' % (server))
    else:
        config = dict(configs[server])

    # Has Authentication
    if 'user' in config and 'password' in config:
        config['user'] = quote_plus(config['user'])
        config['password'] = quote_plus(config['password'])
        url = 'mongodb://%(user)s:%(password)s@%(host)s/?authMechanism=SCRAM-SHA-1&authSource=admin' % config
    else:
        url = 'mongodb://%(host)s' % config

    client = MongoClient(url, *args, **kwargs)
    try:
        cnx = client[db]
    except Exception as e:
        raise e
    else:
        return cnx, client
