# coding=utf-8
# Author: Rion B Correia
# Edited by Xuan Wang
#

import db_init as db

import pandas as pd
from termdictparser import TermDictionaryParser

def load_dictionary(dicttimestamp, db_setting = 'postgres_cns_myaura', db_type = 'postgresql'):
    """
    load dictionary from database and build termdictparser
    :param dicttimestamp: the version of dictionary
    :type dicttimestamp: str
    :param db_setting: the setting name in db_config.json
    :type db_setting: str
    :param db_type: either 'postgresql' or 'mysql'
    :type db_type: str
    :return: a TermDictParser and a pandas dataframe containing the dictionary.
    """
    #
    # Load Dictionary from MySQL
    #
    print('--- Loading MySQL dictionary (%s)---' % dicttimestamp)
    if db_type == 'postgresql':
        engine_dict = db.connectToPostgreSQL(db_setting)
        tablename = 'dictionaries.dict_%s' % (dicttimestamp)
        sql = """SELECT
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
    elif db_type == 'mysql':
        engine_dict = db.connectToMySQL(server=db_setting)
        tablename = 'dict_%s' % (dicttimestamp)
        sql = """SELECT
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
        print('invalid db_type')
        return None

    dfD = pd.read_sql(sql, engine_dict, index_col='id')

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

    return tdp,dfD
