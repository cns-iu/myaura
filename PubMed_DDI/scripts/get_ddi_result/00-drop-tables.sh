#!/bin/bash
set -ev

source ../db-config.sh

psql << EOF

DROP TABLE IF EXISTS pubmed_ddi_classification.abstract_classification_clinical;
DROP TABLE IF EXISTS pubmed_ddi_classification.abstract_classification_invitro;
DROP TABLE IF EXISTS pubmed_ddi_classification.abstract_classification_invivo;

EOF
