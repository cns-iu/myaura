#!/bin/bash
set -ev

source ../db-config.sh

psql << EOF

DROP TABLE IF EXISTS ddi.abstract_classification_clinical;
DROP TABLE IF EXISTS ddi.abstract_classification_invitro;
DROP TABLE IF EXISTS ddi.abstract_classification_invivo;

EOF
