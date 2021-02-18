# coding=utf-8
# Author: Rion B Correia
# Date: October 08, 2018
# Edited by Xuan Wang Oct 2020
# 
# Description: 
# Build Mention Tables (for network construction) on PubMed Abstracts
#
# Add package folder location
import os
import sys

py_include_path = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir, os.pardir, 'include'))

sys.path.insert(0, py_include_path)
#
import db_init as db

import pandas as pd
import json
from pandas import to_datetime

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
from termdictparser import Sentences
from load_dictionary import load_dictionary, build_term_parser

# import utils


if __name__ == '__main__':

    #
    # Init
    #
    #
    dicttimestamp = '20180706'  # raw_input("dict timestamp [yyyymmdd]:") #'20171221' # datetime.today().strftime('%Y%m%d')
    src_table = 'clinical_trials.view_clinical_trials'
    engine_src_text = db.connectToPostgreSQL(server='cns-postgres-myaura')

    with open(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'var.sh')) as varfile:
        defline = varfile.readline()
        dicttimestamp = defline.split('=')[1].strip()

    mention_table = 'mention_clinical_trials_%s.mention' % (dicttimestamp)
    psql_mention = db.connectToPostgreSQL('cns-postgres-myaura')

    # Load Dictionary
    dfD = load_dictionary(dicttimestamp=dicttimestamp, server='cns-postgres-myaura')
    # Build Parser Vocabulary
    tdp = build_term_parser(dfD)

    dict_token = dfD['token'].to_dict()
    dict_id_parent = dfD['id_parent'].to_dict()
    dict_parent = dfD['parent'].to_dict()
    # dict_dictionary = dfD['dictionary'].to_dict()
    dict_type = dfD['type'].to_dict()
    # dict_source = dfD['source'].to_dict()


    for i in range(10000):
        offset = i*100
        print('> Parsing clinical trials: %d - %d' % (i*100, (i+1)*100))
        i += 1

        # SQL Query
        sql = """SELECT nct_id, start_date, brief_title, official_title, brief_summary, detailed_description FROM %s offset %d limit 100""" % (
        src_table, offset)
        q = engine_src_text.execute(sql)

        # No pmid found
        if q.rowcount < 1:
            break
        else:
            for row in q.fetchall():
                unique_id = row[0]
                # convert various date format to ISO format
                index_date = to_datetime(row[1]).strftime('%Y-%m-%d') if (row[1] is not None) else '-infinity'
                text = '\n'.join([i if (i is not None) else '' for i in row[2:]])

                #
                # Find Mentions in Title & Abstract
                #
                # Parser
                s = Sentences(text).preprocess(lower=True).tokenize().match_tokens(parser=tdp)
                if s.has_match():
                    mj = {
                        '_id': unique_id,
                        'created_time': index_date,
                        'matches': []
                    }

                    for match in s.get_unique_matches():
                        for mid in match.id:
                            mj['matches'].append({
                                'id': mid,
                                'id_parent': dict_id_parent[mid],
                                'token': dict_token[mid],
                                'parent': dict_parent[mid],
                                'type': dict_type[mid]
                            })

                    sql = "INSERT INTO %s VALUES ('%s', '%s', '%s');" % \
                          (mention_table, unique_id, index_date, json.dumps(mj).replace("'", "''"))
                    try:
                        q = psql_mention.execute(sql)
                    except ValueError as error:
                        print("Error! Args: '{:s}'".format(error.args))

