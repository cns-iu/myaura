import random, pickle, sys, os, json
import pandas as pd
import random
include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'include'))
sys.path.insert(0, include_path)
from load_dictionary import load_dictionary
from math import factorial
from itertools import combinations

sample_with_token_removed = False
name_root = 'thR_8'

n_sample = 1000
# removed_id = [8433, 202468, 211750, 201798, 201791, 35150, 174899, 240710, 8619, 199415, 170326, 190790]
# removed_id = [8433, 202468, 211750, 201798, 201791, 35150, 174899, 240710, 8619]
removed_id = [202468, 211750, 201791, 35150, 174899, 240710, 8619, 8433]
removed_id_set = set(removed_id)

with open('mention.pkl', 'rb') as rfp:
    token_count = pickle.load(rfp)

sorted_count = sorted(token_count.items(), key=lambda x: x[1], reverse=True)
# old code, used to select tokens with similar ranking
dict_id_rank = {duo[0]: i for i, duo in enumerate(sorted_count)}


#%%

# find the minimum count of ids in removed_id
min_count = min([token_count[tid] for tid in removed_id])
# slice the sorted_count to get the ids with the same or greater count as min_count
for i, duo in enumerate(sorted_count):
    if duo[1] < min_count:
        break
top_sorted_count = sorted_count[:i]
print(len(top_sorted_count))

if sample_with_token_removed:
    top_ids_purged = [duo[0] for duo in top_sorted_count]
else:
    top_ids_purged = []
    for duo in top_sorted_count:
        if duo[0] not in removed_id_set:
            top_ids_purged.append(duo[0])

#%%
sample_list = []
n_ids = len(removed_id)
n_pool = len(top_ids_purged)
# calculate the combination of n_pool choose n_ids
max_sample = factorial(n_pool) / (factorial(n_ids) * factorial(n_pool - n_ids))
if max_sample < 100000:
    print('sample space is small, use all possible combinations')
    if n_sample > max_sample:
        print('sample size is greater than the possible combination, use all possible combinations, ignore n_sample')
    else:
        print('shuffle the possible combinations and select n_sample')
    all_sample = list(combinations(top_ids_purged, n_ids))
    random.shuffle(all_sample)
    sample_list = all_sample[:n_sample]
else:
    for _ in range(n_sample):
        sampled_id_counts = random.sample(top_ids_purged, n_ids)
        sample_list.append(sampled_id_counts)

#%%
# save the sample_list into a json file like known_ids.json
id_dict = {}
count_dict = {}
for i, sample in enumerate(sample_list):
    id_dict['{}_{}'.format(name_root, i)] = sample
    count_dict['{}_{}'.format(name_root, i)] = [token_count[tid] for tid in sample]
with open('{}_{}_id.json'.format(name_root, n_sample), 'w') as fp:
    json.dump(id_dict, fp)
with open('{}_{}_count.json'.format(name_root, n_sample), 'w') as fp:
    json.dump(count_dict, fp)