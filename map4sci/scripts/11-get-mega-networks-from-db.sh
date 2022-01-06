#!/bin/bash
source constants.sh
set -ev

get_network() {
  for type in is_original is_metric is_ultrametric
  do
    OUT=${DATASETS_HOME}/${2}-${type}
    mkdir -p $OUT
    cat src/get_mega_network.sql src/get_json_network.sql | \
      psql -f - -v edges=$2 -v dictionary=$1 -v edgetype=$type -v out_json=$OUT/network.json
  done
}

get_network dict_20180706 net_mega_20180706
get_network dict_20210321 net_mega_20210321
