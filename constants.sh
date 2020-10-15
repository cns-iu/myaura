shopt -s expand_aliases

ORIG=../raw-data/original
OUT=../raw-data/derived/2019-05-14
mkdir -p $ORIG $OUT

SCHEMA=${SCHEMA-clinical_trials}
s=$SCHEMA # A shortened form sql-scripts

MINYEAR=${MINYEAR-2018}
PATH=../node_modules/.bin:${PATH}
