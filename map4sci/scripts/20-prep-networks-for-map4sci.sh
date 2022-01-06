#!/bin/bash
source constants.sh
set -ev

DATASETS=${DATASETS_HOME}
for dataset in $(ls $DATASETS)
do
  OUT=${DATASETS}/${dataset}
  echo $dataset
  time python3 src/json2dot.py $OUT/network.json $OUT/network.dot > $OUT/log.csv
done

for dataset in $(ls $DATASETS)
do
  OUT=${DATASETS}/${dataset}
  echo $dataset
  if [ ! -e $OUT/config.sh ]
  then
    cat src/config-template.sh | perl -pe "s/--DATASET--/${dataset}/g" > $OUT/config.sh
  fi
done
