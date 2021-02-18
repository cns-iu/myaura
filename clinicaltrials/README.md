# How to re-generate all data

1. edit scripts/var.sh to change dictionary version
2. make sure bash is in myaura/clinicaltrials folder, then execute run.sh

# data location

## In PostgraSQL

### materiailzed view

- clinical_trials
  - view_clinical_trials
  - view_clinical_trials_query

### mention, co-mention and proximity network

- mention_clinical_trials_dictdate
  - mention
  - comention
- net_clinical_trials_dictdate
  - nodes
  - edges
  
  
## in local directory

tmp-data