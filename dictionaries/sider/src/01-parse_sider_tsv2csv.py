# coding=utf-8
# Author: Rion B Correia
# Date: April 19, 2021
#
# Description:
# Parses the SIDER data to be inserted into the PostgreSQL.
#
import os
import sys
#
include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'include'))
sys.path.insert(0, include_path)
#
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
from collections import Counter
#
import utils


def map_stitch_id_to_drugbank_id(row):
    stitch_id_flat = row['stitch_id_flat']
    stitch_id_stereo = row['stitch_id_stereo']
    """ Map the STICH cid to a Drugbank id"""

    # CID in SIDER 'flat_chemical'
    if stitch_id_flat in dict_sider_flat_chemical_2_drugbank:
        return dict_sider_flat_chemical_2_drugbank[stitch_id_flat]

    if stitch_id_stereo in dict_sider_stereo_chemical_2_drugbank:
        return dict_sider_stereo_chemical_2_drugbank[stitch_id_stereo]

    # Translate CID to name and search in DrugBank
    name = df_s_names.loc[stitch_id_flat, 'name']
    if name in dict_db_name_2_id:
        return dict_db_name_2_id[name]

    # ID in DrugBank
    #if stitch_id_stereo in dict_db_


    # Additional manually curated mappings
    #if stitch_id_stereo in dict_add_stereo_chemical_2_drugbank:
    #    return dict_add_stereo_chemical_2_drugbank[stitch_id_stereo]

    return np.nan


if __name__ == '__main__':

    # DrugBank from tmp-data
    df_db_atc = pd.read_csv('../../drugbank/tmp-data/drugbank_515_atc.csv.gz')

    # SIDER
    df_s_atc = pd.read_table('../data/sider-v4.1/drug_atc.tsv', index_col=0, names=['stitch_id_flat', 'atc'])

    # Load Meddra Mapping file
    df_s_m = pd.read_csv('../data/sider-v4.1/meddra.tsv', sep='\t', names=['umls_cid_from_meddra', 'meddra_type', 'meddra_id', 'side_effect_name'])
    # Only PreferedTerms (PT)
    df_s_m = df_s_m.loc[df_s_m['meddra_type'] == 'PT', :]
    df_s_m.set_index('umls_cid_from_meddra', inplace=True)
    df_s_m = df_s_m.loc[~df_s_m.index.duplicated()]


    # Merge on ATC codes
    a = df_db_atc.set_index('id_atc')
    b = df_s_atc.reset_index().set_index('atc')
    df_atc_map = pd.merge(left=a, right=b, how='inner', left_index=True, right_index=True)


    # Drug & Side Effects
    # (node that meddra_id_label == meddra_id)
    columns = ['stitch_id_flat', 'stitch_id_stereo', 'meddra_id_label', 'placebo', 'frequency', 'lower', 'upper', 'meddra_type', 'meddra_id', 'meddra_name']
    df_s_freq = pd.read_table('../data/sider-v4.1/meddra_freq.tsv.gz', names=columns)

    # Only PreferedTerm (PT)
    df_s_freq = df_s_freq.loc[df_s_freq['meddra_type'] == 'PT', :].copy()

    # Fix Frequency 'postmarketing' => 'PM'
    df_s_freq['frequency'] = df_s_freq['frequency'].str.replace('postmarketing', 'PM')
    # Transform placebo column into Boolean
    df_s_freq['placebo'] = df_s_freq['placebo'].apply(lambda x: True if (x == 'placebo') else False)

    # Map DrugBank ids
    d = df_atc_map.set_index('stitch_id_flat')['id_drugbank']
    d = d.loc[~d.index.duplicated()]
    df_s_freq['id_drugbank'] = df_s_freq['stitch_id_flat'].map(d)

    # Map MedDRA ids
    df_s_freq['meddra_id'] = df_s_freq['meddra_id'].map(df_s_m['meddra_id'])

    # Group by
    df_s_freq = df_s_freq.\
        groupby(['id_drugbank', 'meddra_id']).\
        agg({'placebo': list, 'frequency': list, 'meddra_type':'first', 'meddra_name': 'first'}).reset_index()

    # Counter
    df_s_freq['placebo'] = df_s_freq['placebo'].apply(Counter)
    df_s_freq['frequency'] = df_s_freq['frequency'].apply(Counter)


    #
    # Drug Indication
    # (node that meddra_id_label == meddra_id)
    columns = ['stitch_id_flat', 'meddra_id_label', 'method', 'concept_name', 'meddra_type', 'meddra_id', 'meddra_name']
    df_s_ind = pd.read_table('../data/sider-v4.1/meddra_all_indications.tsv.gz', names=columns)

    # Only PreferedTerm (LLT)
    df_s_ind = df_s_ind.loc[df_s_ind['meddra_type'] == 'PT', :].copy()

    # Map DrugBank ids
    df_s_ind['id_drugbank'] = df_s_ind['stitch_id_flat'].map(d)

    # Map MedDRA ids
    df_s_ind['meddra_id'] = df_s_ind['meddra_id'].map(df_s_m['meddra_id'])

    df_s_ind = df_s_ind.\
        groupby(['id_drugbank', 'meddra_id']).\
        agg({'meddra_type': 'first', 'meddra_name': 'first'}).reset_index()


    #
    # Export CSV
    #
    df_s_freq.to_csv('../tmp-data/sider-drug-sideeffect.csv.gz')
    df_s_ind.to_csv('../tmp-data/sider-drug-indication.csv.gz')