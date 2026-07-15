#!/bin/bash
set -e

source ../db-config.sh

echo Run started on $(date)...
echo
for f in scripts/get_ddi_result/??-*.sh
do
  echo Running $f...
  time bash $f
  echo
done
