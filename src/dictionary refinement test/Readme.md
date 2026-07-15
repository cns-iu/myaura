Currently we focus on the latest update on Oct 2023. 

# 1. Introduction

# 2. Different data sources

Old scripts: build_network*.py, possibly contains some modification, like random control and make sure they all have the same set of nodes. 

New scripts: inside each data source, the alt_dict folder. So we can have

## 2.1. Instagram

We have both the old and new version. 

The new version can specify the token to be removed. 

## 2.2. Twitter

## 2.3. PubMed

No plan to write the new code for randomized removed token.

# 3. load different list of removed ids

save_old_config.py: save all the named list of removed ids in a json file. 

To generate 100 or more ids based on the list of id, use random_sample_token_threshold.py. 
This file will generate two json file which can be used later. 

There are two versions: thF use all tokens above a threshold and thR do not use removed tokens (that is the same to sample only tokens with FPR less than 0.5). 

Then call gen_comention_net.py to generate all networks using those sampled ids. This script can accept any json of ids and calculate the corresponding networks and save them in a directory. 

## tau and tau's missing penalty

simple_eigen_1vn.py is an old script that read in a list of id and calculate the statistics for tau (mean, std) for top 10 20 50 100 500. 

Originally we thought this is a one pass calculation. Then we need to do more calculation for the contributing factors for tau. A new pipeline is written for this purpose. 

- eigen_nodes_for_networks.py: this file read in a list of network ids then do the eigenvector centrality (or other centrality at your choice) and save the result into a csv, at the side of network files. So we do not need to calculate the centrality every time, just read them in. 
- tau_factor.py: obsolete. After we found out that we cannot justify 0.5 and random permutation/totally different list, we do not want to continue with the missing penalty contribution calculation.