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
from itertools import combinations

py_include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'include'))

sys.path.insert(0, py_include_path)
#
import db_init as db
from collections import Counter
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
    dicttimestamp = '20180706'  # raw_input("dict timestamp [yyyymmdd]:") #'20171221' # datetime.today().strftime('%Y%m%d')
    with open(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'var.sh')) as varfile:
        defline = varfile.readline()
        dicttimestamp = defline.split('=')[1].strip()

    mention_table = 'mention_pubmed_epilepsy_%s.mention' % (dicttimestamp)
    comention_table = 'mention_pubmed_epilepsy_%s.comention' % (dicttimestamp)
    mention_count_table = 'mention_pubmed_epilepsy_%s.mention_count' % (dicttimestamp)
    psql_mention = db.connectToPostgreSQL('cns-postgres-myaura')

    inserts = {}

    mention_count = Counter()

    for i in range(10000):
        offset = i * 100
        print('> Parsing PubMedID: %d - %d' % (i * 100, (i + 1) * 100))
        i += 1

        # SQL Query
        sql = """SELECT pmid, year_publication, match FROM %s offset %d limit 100""" % (mention_table, offset)
        q = psql_mention.execute(sql)

        # No pmid found
        if q.rowcount < 1:
            break
        else:
            for row in q.fetchall():
                pmid = row[0]
                match = row[2] if (row[2] is not None) else ''
                date_publication = row[1] if (row[1] is not None) else -10000

                matches = match['matches']

                for m in matches:
                    mention_count[m['id_parent']] += 1

                # Combination of all matches
                for source, target in combinations(matches, 2):

                    ## Always the smaller number, first
                    # if source['id'] > target['id']:
                    #	source, target = target, source

                    id_source = source['id']
                    id_parent_source = source['id_parent']

                    id_target = target['id']
                    id_parent_target = target['id_parent']

                    # Skip self-loops
                    if id_parent_source == id_parent_target:
                        continue

                    # Key to only add after all user posts have been processed
                    key = frozenset((id_source, id_target))
                    if key not in inserts:
                        comention = {
                            'source': source,
                            'target': target,
                            'count': 0,
                            'evidences': list(),
                        }
                    else:
                        comention = inserts[key]

                    evidence = {
                        'id': pmid,
                        'created_time': date_publication,
                    }
                    comention['evidences'].append(evidence)
                    # Increase Counter
                    comention['count'] += 1

                    inserts[key] = comention

    print('\nDone.\n')
    print('--- Inserting PubMed CoMentions ---')
    print()
    inserts_list = inserts.values()
    inserts_size = len(inserts_list)
    # print( '> inserting {:,d} records'.format(inserts_size))

    for drug_id in mention_count:
        sql = "INSERT INTO %s VALUES (%d, %d);" % \
              (mention_count_table, drug_id, mention_count[drug_id])
        try:
            q = psql_mention.execute(sql)
        except ValueError as error:
            print("Error! Args: '{:s}'".format(error.args))

    count = 0
    for comention in inserts_list:

        sql = "INSERT INTO %s VALUES (%d, %d, '%s');" % \
              (comention_table, comention['source']['id'], comention['target']['id'], json.dumps(comention).replace("'", "''"))
        try:
            q = psql_mention.execute(sql)
        except ValueError as error:
            print("Error! Args: '{:s}'".format(error.args))
        count += 1
        if count % 100 == 0:
            print('%s/%d entries have been inserted' % (count, inserts_size))
