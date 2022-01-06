#!/bin/bash
source constants.sh
set -ev

# Make sure this line is at the end of your map4sci env.sh:
# source datasets/${CURRENT_DATASET}/config.sh

pushd ${MAP4SCI_HOME}/data-processor/

DATASETS=${MAP4SCI_HOME}/data-processor/datasets/myaura

for dataset in $(ls $DATASETS)
do
  OUT=${DATASETS}/${dataset}
  echo $dataset
  if [ ! -e $OUT/map4sci-completed ]
  then
    export CURRENT_DATASET=myaura/$dataset
    time ./run.sh &> $OUT/map4sci.log
    touch $OUT/map4sci-completed
  fi
done

time ./scripts/51x-build-all-dataset-maps.sh 
time ./scripts/90-generate-site.sh

popd
