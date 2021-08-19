#!/bin/bash

DICTIONARY=$1
EDGES=$2
OUT_JSON=$3

psql -t -A -f map4sci/src/get_json_network.sql -v edges=$2 -v dictionary=$1 -o $OUT_JSON
