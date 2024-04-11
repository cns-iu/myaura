#%%
import os,pickle,sys
include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir,'include'))
sys.path.insert(0, include_path)
from load_dictionary import load_dictionary
from tabulate import tabulate
dicttimestamp = '20180706'

#%%

removed_id = [8433, 202468, 211750, 201798, 201791, 35150, 174899, 240710, 8619, 199415, 170326, 190790]
alt_removed_id = [240710, 146507, 25536, 8593, 182630, 8619, 240925, 188818, 16726, 8582, 206783, 8628]

with open('../mention.pkl', 'rb') as rfp:
    token_count = pickle.load(rfp)

#%%

for i in range(12):
    print(removed_id[i], token_count[removed_id[i]], alt_removed_id[i], token_count[alt_removed_id[i]])

#%%
dfD = load_dictionary(dicttimestamp=dicttimestamp, server='cns-postgres-myaura')

#%%
for i in range(12):
    print(dfD.loc[removed_id[i]]['token'], dfD.loc[alt_removed_id[i]]['token'])

#%%
# print the token in removed_id and alt_removed_id, and their count, using tabulate, org-mode format
table = []
for i in range(12):
    table.append([dfD.loc[removed_id[i]]['token'], token_count[removed_id[i]], dfD.loc[alt_removed_id[i]]['token'], token_count[alt_removed_id[i]]])
# sort table by count
table.sort(key=lambda x: x[1], reverse=True)
print(tabulate(table, headers=['removed token', 'count', 'alt token', 'count'], tablefmt='orgtbl'))