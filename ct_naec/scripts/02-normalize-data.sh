#!/bin/bash
source ../constants.sh
set -ev

node src/convert-ct-locations.js $OUT/ct-locations.raw.csv $OUT/ct-locations.json
node src/convert-naec-data.js $OUT/doctor-data.raw.json $OUT/doctor-data.json

node src/combine-data.js $OUT/ct-locations.json $OUT/doctor-data.json $OUT/locations.json
any-json convert $OUT/locations.json $OUT/locations.csv
