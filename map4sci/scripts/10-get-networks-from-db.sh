#!/bin/bash
source constants.sh
set -ev

get_network() {
  for type in is_original is_metric is_ultrametric
  do
    OUT=${DATASETS_HOME}/${2}-${type}
    mkdir -p $OUT
    cat src/get_json_network.sql | \
      psql -t -A -f - -v edges=${2}.edges -v dictionary=$1 -v edgetype=$type -o $OUT/network.json
  done
}

get_network dict_20180706 net_clinical_trials_20180706
get_network dict_20210321 net_clinical_trials_20210321

get_network dict_20180706 net_efwebsite_forums_20180706
get_network dict_20210321 net_efwebsite_forums_20210321

get_network dict_20180706 net_instagram_20180706
get_network dict_20210321 net_instagram_20210321

get_network dict_20180706 net_pubmed_epilepsy_20180706
get_network dict_20210321 net_pubmed_epilepsy_20210321

get_network dict_20180706 net_twitter_20180706
