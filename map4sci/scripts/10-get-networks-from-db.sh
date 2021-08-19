#!/bin/bash
set -ev

get_network() {
  OUT=~/workspaces/tripods/map4sci/datasets/myaura/$2
  mkdir -p $OUT
  ./map4sci/src/get_json_network.sh $1 $2 $OUT/network.json
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
