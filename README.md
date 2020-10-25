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
* python 3.7

It is known to work on Mac and Linux, but has not yet been tested on Windows.

## Running the workflow

The [scripts](scripts) directory has a set of bash scripts numbered in the order they should executed.

You can run the full workflow from end to end using the [run.sh](run.sh) file in the root directory.

### database configuration

There are several database configuration files under the project root. Not all of them are needed for all datasets. See README inside each dataset folder for database configuration requirment. 

Before running scripts, database server address, user name and password need to be configured in those files. 

- db-config.sh

  This file configures the enviroenment variables for PostgreSQL coomand line tool `psql`. 
  
  See db-config.example.json for an example. 
  
- db_config.json

  This file configures database connections parameters for python scripts. 
  
  See db_config.example.json for example. 
  
- mysql.cnf

  Because the latest version of MySQL and MariaDB strongly discourage using environment variables to configure connection, some version even dropped support for environemnt password vairable, we have to use an configuration file to store password. 
  The format of mysql.cnf is basically similar to ~/.my.cnf, the full documentation is here: https://dev.mysql.com/doc/refman/8.0/en/option-files.html
  
  There is an example file mysql.example.cnf. Don't change the section name, just fill in password. 
