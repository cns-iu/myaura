import os, sys, json
import concurrent.futures
include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'instagram', 'alt_dict'))
sys.path.insert(0, include_path)

from count_comentions_samepost_alt import compute_instagram_comentions_samepost
from build_network_samepost_alt import build_instagram_network_samepost

NUM_WORKERS = 10

with open('thR_8_1000_id.json', 'r') as f:
# with open('thF_12_100_id.json', 'r') as f:
# with open('known_ids.json', 'r') as f:
    known_ids = json.load(f)

# for name in known_ids:
#     print(name)
#     save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'network', name))
#     os.makedirs(save_dir, exist_ok=True)
#     compute_instagram_comentions_samepost(known_ids[name], save_dir)
#     build_instagram_network_samepost(save_dir)

def worker(name, id_value):
    print(name)
    save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'network', name))
    os.makedirs(save_dir, exist_ok=True)
    compute_instagram_comentions_samepost(id_value, save_dir)
    build_instagram_network_samepost(save_dir, False)

def parallel_execution(known_ids):
    with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
        # using executor.map for parallel execution
        list(executor.map(worker, known_ids.keys(), known_ids.values()))

parallel_execution(known_ids)