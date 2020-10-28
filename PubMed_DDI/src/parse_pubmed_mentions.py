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

py_include_path = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir, os.pardir, 'py_include'))

sys.path.insert(0, py_include_path)
#
import db_init as db

import pandas as pd
import json

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
from termdictparser import Sentences
from load_dictionary import load_dictionary

# import utils


if __name__ == '__main__':

    #
    # Init
    #
    #
    dicttimestamp = '20180706'  # raw_input("dict timestamp [yyyymmdd]:") #'20171221' # datetime.today().strftime('%Y%m%d')

    tdp,dfD = load_dictionary(dicttimestamp)

    dict_token = dfD['token'].to_dict()
    dict_id_parent = dfD['id_parent'].to_dict()
    dict_parent = dfD['parent'].to_dict()
    # dict_dictionary = dfD['dictionary'].to_dict()
    dict_type = dfD['type'].to_dict()
    # dict_source = dfD['source'].to_dict()


    engine_pubmed = db.connectToMySQL(server='mysql_medline17')
    engine_prediction_result = db.connectToPostgreSQL('postgres_cns_test')



    #
    # Get PubMedIDS from database
    #
    # Abstracts Overall Best (Single Best)
    abstracts = [
        ('invivo', 'LSVC', 'ddi.abstract_classification_invivo'),  # In Vivo
        ('invitro', 'LSVC', 'ddi.abstract_classification_invitro'),  # In Vitro
        ('clinical', 'LR', 'ddi.abstract_classification_clinical'),  # Clinical
    ]
    dfs = []
    for type, clf, table in abstracts:
        print("Requesting type: '{:s}'".format(type))

        sql = "SELECT id_pm FROM {table:s} WHERE classifier = '{clf:s}' AND prediction = 1".format(table=table, clf=clf)

        dft = pd.read_sql(sql, engine_prediction_result)
        dft[type] = True
        dft.set_index('id_pm', inplace=True)
        dfs.append(dft)

    dfSB = pd.concat(dfs, axis=1)
    dfSB.fillna(False, inplace=True)

    db_pubmed = 'pubmed_medline17'
    # db_mention = 'ddi_pubmed_mentions'
    mention_col = 'pubmed_abstract_mention_%s' % (dicttimestamp)
    psql_mention = db.connectToPostgreSQL('postgres_cns_test')
    # mongo_mention, _ = db.connectToMongoDB(server='mongo_ddi', db=db_mention)

    n_abstracts = dfSB.shape[0]

    i = 0
    for pmid, r in dfSB.iterrows():
        i += 1
        types = r[r == True].to_dict()

        if i % 100 == 0:
            print('> Parsing PubMedID: %s (%d of %d)' % (pmid, i + 1, n_abstracts))

        # SQL Query
        sql = """SELECT id_pm, id_pmc, title, abstract, date_publication FROM articles WHERE id_pm = %s""" % (pmid)
        q = engine_pubmed.execute(sql)

        # No pmid found
        if q.rowcount < 1:
            print("> PMID '{:d}' not found. Skipping.".format(pmid))
            continue
        else:
            row = q.fetchone()
            row = dict(list(zip(list(q.keys()), row)))

        title = row['title'] if (row['title'] is not None) else ''
        abstract = row['abstract'] if (row['abstract'] is not None) else ''
        date_publication = str(row['date_publication'])
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
            mj.update(types)  # include

            for match in s.get_unique_matches():
                for mid in match.id:
                    mj['matches'].append({
                        'id': mid,
                        'id_parent': dict_id_parent[mid],
                        'token': dict_token[mid],
                        'parent': dict_parent[mid],
                        'type': dict_type[mid]
                    })

            sql = "INSERT INTO ddi.%s VALUES (%s, '%s', '%s');" % (mention_col, pmid, date_publication, json.dumps(mj).replace("'", "''"))
            try:
                q = psql_mention.execute(sql)
            except ValueError as error:
                print("Error! Args: '{:s}'".format(error.args))
        else:
            pass

