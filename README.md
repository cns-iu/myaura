# MyAura Data Processing

## Datasets

### Internally Maintained Datasets

A variety of datasets are being used in this project that we maintain.
For the following datasets, aquisition, transformation, parsing, db_schema, and
loading codes are in separate repositories:

* Clinical Trials - [GitHub](https://github.com/cns-iu/clinical_trials) | [Database Documentation](https://demo.cns.iu.edu/dbdocs/clinical-trials/)
* Web of Science - [GitHub](https://github.com/cns-iu/wos_2017) | [Database Documentation](https://demo.cns.iu.edu/dbdocs/wos/)
* USPTO - [GitHub](https://github.com/cns-iu/uspto) | [Database Documentation](http://demo.cns.iu.edu/dbdocs/uspto/)

### Third Party Datasets

* NAEC - <https://www.naec-epilepsy.org/>

## System Requirements

* bash
* NodeJS 10+
* NPM 6+

It is known to work on Mac and Linux, but has not yet been tested on Windows.

## Running the workflow

The [scripts](scripts) directory has a set of bash scripts numbered in the order they should executed.

You can run the full workflow from end to end using the [run.sh](run.sh) file in the root directory.
