#!/bin/bash
set -ev

prep_network() {
  OUT=~/workspaces/tripods/map4sci/datasets/myaura/$1
  time python3 ./map4sci/src/json2dot.py $OUT/network.json $OUT/network.dot > $OUT/log.txt
}

prep_network net_clinical_trials_20180706
prep_network net_clinical_trials_20210321

prep_network net_efwebsite_forums_20180706
prep_network net_efwebsite_forums_20210321

prep_network net_instagram_20180706
prep_network net_instagram_20210321

prep_network net_pubmed_epilepsy_20180706
prep_network net_pubmed_epilepsy_20210321

prep_network net_twitter_20180706
