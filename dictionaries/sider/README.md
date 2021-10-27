SIDER (drug side effect) dataset
======================

This dataset links drugs (DrugBank) to known side effects and drug indication (MedDRA).

Previously, the drugbank ids were converted using Stitch.
This caused lots of problems and required mannual annotation of exceptions.
We have now changed this pipeline and drugbank ids are now matched using ATC codes directly.
This has greatly simplified the process.

Also note that SIDER has side-effect ids that match to multiple MedDRA ids. Sometimes there are multiple MedDRA ids to the SIDER side-effect id. An assumption is made to select only the first record.

In addition, only MedDRA Prefered Terms (PT) are used.

Tables being populated:

- `sider_41_drug_has_sideeffect`
- `sider_41_drug_has_indication`

Note: the SIDER datafiles should be downloaded and placed inside the `data/sider-v4.1` folder.

MySQL Schema
==============

This is the current DB Schema inside the database `epilepsy`.
All tables have the prefix `sider_`.

```sql
DROP TABLE IF EXISTS sider_41_drug_has_sideeffect;
CREATE TABLE sider_41_drug_has_sideeffect
(
    id_drugbank VARCHAR(7) NULL, # from drugbank
    id_meddra_pt_code INT NOT NULL, # from meddra
    placebo JSON,
    frequency JSON,
    meddra_type VARCHAR(3), # only PreferedTerms (PT) codes are used
    meddra_pt_name TEXT  # this is denormalized here for simplicity
);
```

```sql
DROP TABLE IF EXISTS sider_41_drug_has_indication;
CREATE TABLE sider_41_drug_has_indication
(
    id_drugbank VARCHAR(7) NULL, # from drugbank
    id_meddra_pt_code VARCHAR(8) NOT NULL, # from meddra
    meddra_type VARCHAR(3),
    meddra_pt_name TEXT # this is denormalized here for simplicity
) ENGINE=InnoDB;
```

Add Indexes

```sql
CREATE INDEX idx_id_drugbank ON sider41_drug_has_sideeffect (id_drugbank);
CREATE INDEX idx_pt_code ON sider41_drug_has_sideeffect (pt_code);
CREATE INDEX idx_id_drugbank ON sider41_drug_has_indication (id_drugbank);
CREATE INDEX idx_pt_code ON sider41_drug_has_indication (pt_code);
```

Truncate all tables
---------------------
```sql
-- TRUNCATE TABLE sider_sideeffect;
TRUNCATE TABLE sider_41_drug_has_sideeffect;
TRUNCATE TABLE sider_41_drug_has_indication;
```

