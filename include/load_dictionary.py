# coding=utf-8
# Author: Rion B Correia & Xuan Wang
# Date: Jan 06, 2021
#
# Description: Helper function that loads the dictionary from the a database and builds the term parser.
#
import db_init as db
import pandas as pd
from termdictparser import TermDictionaryParser


def load_dictionary_build_term_parser(dicttimestamp, server='postgres-cns-myaura'):
    """ Load dictionary from database and builds termdictparser

    Args:
        dicttimestamp (string): the version of dictionary (ex: 20210131)
        server (string): the server name in db_config.ini

    Returns:
        tuple (termdictparser, pandas.DataFrame): A TermDictParser and a pandas dataframe containing the dictionary.
    """
    #
    # Load Dictionary from MySQL
    #
    print('--- Loading MySQL dictionary (%s)---' % dicttimestamp)
    #
    if server.startswith('postgres'):

        engine = db.connectToPostgreSQL(server=server)
        tablename = 'dictionaries.dict_%s' % (dicttimestamp)
        sql = """
            SELECT
                d.id,
                COALESCE(d.id_parent,d.id) AS id_parent,
                d.dictionary,
                d.token,
                COALESCE(p.token, d.token) as parent,
                d.type,
                d.source,
                d.id_original,
                COALESCE(p.id_original, d.id_original) as id_original_parent
                FROM %s d
                LEFT JOIN %s p ON d.id_parent = p.id
                WHERE d.enabled > 0""" % (tablename, tablename)

    elif server.startswith('mysql'):

        engine = db.connectToMySQL(server=server)
        tablename = 'dict_%s' % (dicttimestamp)
        sql = """
            SELECT
            d.id,
            IFNULL(d.id_parent,d.id) AS id_parent,
            d.dictionary,
            d.token,
            IFNULL(p.token, d.token) as parent,
            d.type,
            d.source,
            d.id_original,
            IFNULL(p.id_original, d.id_original) as id_original_parent
            FROM %s d
            LEFT JOIN %s p ON d.id_parent = p.id
            WHERE d.enabled = True""" % (tablename, tablename)
    else:
        raise TypeError('Invalid server')

    dfD = pd.read_sql(sql, engine, index_col='id')

    # Some tokens have multiple hits (Drug products with multiple compounds)
    dfDg = dfD.reset_index(drop=False).groupby('token').agg({
        'id': lambda x: tuple(x)
    })
    dfDg = dfDg.reset_index().set_index('id')

    # Build Term Parser
    print('--- Building Term Parser ---')
    tdp = TermDictionaryParser()

    # Select columns to pass to parser
    list_tuples = list(dfDg['token'].str.lower().items())

    # Build Parser Vocabulary
    tdp.build_vocabulary(list_tuples)

    return tdp, dfD
