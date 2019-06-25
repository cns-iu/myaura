# coding=utf-8
# Author: Rion B Correia
# Date: 25 June 2019
#
# Description: Database Connection

import os
import json
import sqlalchemy

#
# Load DB Configuration File
#
with open(os.path.join(os.path.dirname(__file__), 'db_config.json')) as f:
    CONFIGS = json.load(f)


def connectToMySQL(server, verbose=False, *args, **kwargs):
    """
    Connects to a mySQL server.
    Be sure to have a `db_config.json` file with connection details.
    """
    # Get the correct MySQL Server configuration. Or throws an error.
    if server not in CONFIGS:
        raise ValueError('Database server `%s` not defined in `db_config.json`.' % (server))
    else:
        CONFIG = CONFIGS[server]

    url = 'mysql+pymysql://%(user)s:%(password)s@%(host)s/%(database)s?charset=utf8' % CONFIG
    engine = sqlalchemy.create_engine(url, encoding='utf-8', *args, **kwargs)

    return engine
