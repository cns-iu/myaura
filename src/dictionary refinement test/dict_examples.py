# this script is to examine the dictionary and provides some examples needed for the paper
import sys
sys.path.append('../include')
from load_dictionary import load_dictionary
import db_init as db
import pandas as pd

# load the dictionary

dfD = load_dictionary(dicttimestamp='20231116', server='cns-postgres-myaura')

# %%

# print out all fields in dfD
print(dfD.columns)

# %%

# get duplicates in the dictionary, using the token field
# keep all the duplicates, sort by token
duplicates = dfD[dfD.duplicated(subset='token', keep=False)].sort_values('token')

# %%

# since the df duplicated is already sorted by token, we can use a for loop
# to find those token with different type

current_token = None
current_type = None
for i in range(1, len(duplicates)):
    if duplicates.iloc[i]['token'] == current_token:
        if duplicates.iloc[i]['type'] != current_type:
            print(current_token, '|', current_type)
            print(duplicates.iloc[i]['token'], '|' ,duplicates.iloc[i]['type'])
            current_type = duplicates.iloc[i]['type']

    else:
        current_token = duplicates.iloc[i]['token']
        current_type = duplicates.iloc[i]['type']

# %%
# print out rows with token = Relaxan
print(dfD[dfD['token'] == 'Relaxan'])

# print rows id = 8731, 10807, 11006's token
print(dfD.loc[[8731, 10807, 11006]]['token'])