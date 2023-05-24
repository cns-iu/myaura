#!/bin/bash

SOURCE=`realpath $1`
TARGET_CSV=`realpath $2`

echo "dataset,id,label,level,weight,x,y" > $TARGET_CSV
for dataset in `ls $SOURCE | grep -v index.json`; do
  datasetName=$(echo $dataset | perl -pe 's/^net\_//g;s/\_20\d\d\d\d\d\d//g;s/_epilepsy//g;s/[\_\-]/\ /g;s/\ is//g;s/\ original//g;')
  jq -r ".features[] | [\"${datasetName}\",(if .properties.src_id then .properties.src_id|tonumber else .id|tonumber end),.properties.label,.properties.level,(.properties.weight|tonumber),.geometry.coordinates[0],.geometry.coordinates[1]] | @csv" \
    $SOURCE/$dataset/nodes.geojson >> $TARGET_CSV
done
