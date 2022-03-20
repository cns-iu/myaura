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

    mention_table = 'mention_clinical_trials_%s.mention' % (dicttimestamp)
    comention_table = 'mention_clinical_trials_%s.comention' % (dicttimestamp)
    mention_count_table = 'mention_clinical_trials_%s.mention_count' % (dicttimestamp)
    psql_mention = db.connectToPostgreSQL('cns-postgres-myaura')

    inserts = {}

    mention_count = Counter()

    for i in range(10000):
        offset = i * 100
        print('> Parsing PubMedID: %d - %d' % (i * 100, (i + 1) * 100))
        i += 1

        # SQL Query
        sql = """SELECT nct_id, start_date, match FROM %s offset %d limit 100""" % (mention_table, offset)
        q = psql_mention.execute(sql)

        # No pmid found
        if q.rowcount < 1:
            break
        else:
            for row in q.fetchall():
                unique_id = row[0]
                match = row[2] if (row[2] is not None) else ''
                index_date = row[1].strftime('%Y-%m-%d') if (row[1] is not None) else -10000

                matches = match['matches']


                # We want unique matches of id_parent
                # Here we also removed id and token, since they have no use in the following part and can cause confusion
                # when only one token is reserved while multiple tokens were matched
                # Two processes are needed, so a for loop. Though one of them can be written in list comprehension
                set_matches_id_parent = set()
                list_unique_mateches = []
                for m in matches:
                    if m['id_parent'] not in set_matches_id_parent:
                        set_matches_id_parent.add(m['id_parent'])
                        m.pop('id')
                        m.pop('token')
                        list_unique_mateches.append(m)
                mention_count.update(set_matches_id_parent)


                # Combination of all matches
                for source, target in combinations(list_unique_mateches, 2):

                    ## Always the smaller number, first
                    # if source['id'] > target['id']:
                    #	source, target = target, source

                    id_parent_source = source['id_parent']

                    id_parent_target = target['id_parent']

                    # Key to only add after all user posts have been processed
                    key = frozenset((id_parent_source, id_parent_target))
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
                        'id': unique_id,
                        'created_time': index_date,
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

    for term_id_parent in mention_count:
        sql = "INSERT INTO %s VALUES (%d, %d);" % \
              (mention_count_table, term_id_parent, mention_count[term_id_parent])
        try:
            q = psql_mention.execute(sql)
        except ValueError as error:
            print("Error! Args: '{:s}'".format(error.args))

    count = 0
    for comention in inserts_list:

        sql = "INSERT INTO %s VALUES (%d, %d, '%s');" % \
              (comention_table, comention['source']['id_parent'], comention['target']['id_parent'], json.dumps(comention).replace("'", "''"))
        try:
            q = psql_mention.execute(sql)
        except ValueError as error:
            print("Error! Args: '{:s}'".format(error.args))
        count += 1
        if count % 100 == 0:
            print('%s/%d entries have been inserted' % (count, inserts_size))
