import json

removed_id_dict = {
    # original 12 tokens, the top 10 parent terms
    "original_12": [8433, 202468, 211750, 201798, 201791, 35150, 174899, 240710, 8619, 199415, 170326, 190790],
    # still using parent terms for FPR, but use different threshold to get top 16 and top 6
    # this version is to use the freq threshold 10
    # added token: Turkey (Turkey Food not included) 8644
    # added token: Trance (Oneirism not included) 187288
    # added token: Bite 171768
    # added token: Burn (all other token not included, more than a dozen) 226336
    "original_16": [8433, 202468, 211750, 201798, 201791, 35150, 174899, 240710, 8619, 199415, 170326, 190790, 8644, 187288, 171768, 226336],
    # this version use the freq threshold 20, select only the first group of dots.
    "original_9": [8433, 202468, 211750, 201798, 201791, 35150, 174899, 240710, 8619],
    # the first comparison group, 12 tokens selected randomly with similar frequency to original_12 group
    "random_12": [240710, 146507, 25536, 8593, 182630, 8619, 240925, 188818, 16726, 8582, 206783, 8628],
    # the latest verison, FPR now calculated using children terms. select top 8 tokens.
    "child_8": [202468, 211750, 201791, 35150, 174899, 240710, 8619, 8433]
}

# save the removed_id_dict in to a json file
with open('known_ids.json', 'w') as fp:
    json.dump(removed_id_dict, fp)
