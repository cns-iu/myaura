import json
from sys import argv

IN_JSON=argv[1]

def fix_name(dataset):
    name = dataset['name']
    name = name.replace('net_', '').replace('-is_', ' (').replace('_', ' ') + ')'
    dataset['name'] = name.title()
    return dataset

data = json.load(open(IN_JSON))
data = list(map(lambda ds: fix_name(ds), data))

json.dump(data, open(IN_JSON, 'w'), indent=2)
