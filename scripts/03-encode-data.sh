#!/bin/bash
source constants.sh
set -ev

for json in ct-locations doctor-data locations
do
  node src/encode-mav-csv.js $OUT/${json}.json $OUT/${json}.csv
done
