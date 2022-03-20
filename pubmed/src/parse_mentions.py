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
    with open(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'var.sh')) as varfile:
        defline = varfile.readline()
        dicttimestamp = defline.split('=')[1].strip()

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


    engine_pubmed = db.connectToPostgreSQL(server='cns-postgres-myaura')
    # engine_prediction_result = db.connectToPostgreSQL('postgres_cns_test')


    # db_pubmed = 'pubmed_medline17'
    # db_mention = 'ddi_pubmed_mentions'
    mention_table = 'mention_pubmed_epilepsy_%s.mention' % (dicttimestamp)
    psql_mention = db.connectToPostgreSQL('cns-postgres-myaura')
    # mongo_mention, _ = db.connectToMongoDB(server='mongo_ddi', db=db_mention)


    for i in range(10000):
        offset = i*100
        print('> Parsing PubMedID: %d - %d' % (i*100, (i+1)*100))
        i += 1

        # SQL Query
        sql = """SELECT pmid, article_title, abstract_text, pub_year FROM pubmed.view_epilepsy offset %d limit 100""" % (offset)
        q = engine_pubmed.execute(sql)

        # No pmid found
        if q.rowcount < 1:
            break
        else:
            for row in q.fetchall():
                pmid = row[0]
                title = row[1] if (row[1] is not None) else ''
                abstract = row[2] if (row[2] is not None) else ''
                date_publication = row[3] if (row[3] is not None) else -10000
                # date_publication = datetime.combine(row['date_publication'],
                #                                     datetime.min.time())  # convert date to datetime for MongoDB

                #
                # Find Mentions in Title & Abstract
                #
                text = title + "\n" + abstract
                # Parser
                s = Sentences(text).preprocess(lower=True).tokenize().match_tokens(parser=tdp)
                if s.has_match():
                    mj = {
                        '_id': pmid,
                        'created_time': date_publication,
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

                    sql = "INSERT INTO %s VALUES (%s, '%s', '%s');" % \
                          (mention_table, pmid, date_publication, json.dumps(mj).replace("'", "''"))
                    try:
                        q = psql_mention.execute(sql)
                    except ValueError as error:
                        print("Error! Args: '{:s}'".format(error.args))

