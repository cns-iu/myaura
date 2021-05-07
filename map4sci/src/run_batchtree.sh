#!/bin/bash
set -ev

IN_DOT=$1
OUT_DOT=$2
TEMP=${OUT_DOT}__temp
mkdir -p $TEMP


python3 ~/workspaces/myaura/myaura/map4sci/src/dot2mtx.py $IN_DOT $TEMP/network

~/workspaces/tripods/BatchTree/bin/BatchTree -input $TEMP/network.mtx -label $TEMP/network.labels -output $TEMP/ -algo 2

python3 ~/workspaces/myaura/myaura/map4sci/src/add_pos_to_dot.py $IN_DOT $TEMP/network.mtx*.txt $OUT_DOT

rm -r $TEMP
