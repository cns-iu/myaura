import random, pickle, sys, os
import pandas as pd
include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'include'))
sys.path.insert(0, include_path)
from load_dictionary import load_dictionary

pool_size = 5

with open('mention.pkl', 'rb') as rfp:
    token_count = pickle.load(rfp)

sorted_count = sorted(token_count.items(), key=lambda x: x[1], reverse=True)
location_dict = {duo[0]: i for i, duo in enumerate(sorted_count)}

# removed_id = [8433, 202468, 211750, 201798, 201791, 35150, 174899, 240710, 8619, 199415, 170326, 190790]
removed_id = [202468, 211750, 201791, 35150, 174899, 240710, 8619, 8433]
alt_ids = []
for tid in removed_id:
    loc = location_dict[tid]
    half_pool = int(pool_size/2)
    start = loc - half_pool if loc - half_pool >= 0 else 0
    end = start + pool_size
    while True:
        alt_id = random.choice(sorted_count[start:end])[0]
        if alt_id != tid and not (alt_id in alt_ids):
            break
    print(tid, token_count[tid], alt_id, token_count[alt_id])
    alt_ids.append(alt_id)
print(alt_ids)

dicttimestamp = '20180706'

# Load Dictionary
dfD = load_dictionary(dicttimestamp=dicttimestamp, server='cns-postgres-myaura')

dfD.drop(alt_ids)

# with open('new_dict.pkl', 'wb') as wfp:
#     pickle.dump(dfD, wfp)