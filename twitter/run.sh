#!/bin/bash
set -ev

source ../db-config.sh
source scripts/var.sh

OLD_DICT_VERSION=20180706

sed -i "s/$OLD_DICT_VERSION/$DICT_VERSION/" src/01-parse_twitter_mentions.py
sed -i "s/$OLD_DICT_VERSION/$DICT_VERSION/" src/02-count_comentions_samepost.py
sed -i "s/$OLD_DICT_VERSION/$DICT_VERSION/" src/04-build_network_samepost.py
sed -i "s/$OLD_DICT_VERSION/$DICT_VERSION/" scripts/04-upload_network.sh

python src/01-parse_twitter_mentions.py
python src/02-count_comentions_samepost.py
python src/04-build_network_samepost.py

chmod +x scripts/04-upload_network.sh
./scripts/04-upload_network.sh

# restore every file back
sed -i "s/$DICT_VERSION/$OLD_DICT_VERSION/" src/01-parse_twitter_mentions.py
sed -i "s/$DICT_VERSION/$OLD_DICT_VERSION/" src/02-count_comentions_samepost.py
sed -i "s/$DICT_VERSION/$OLD_DICT_VERSION/" src/04-build_network_samepost.py
sed -i "s/$DICT_VERSION/$OLD_DICT_VERSION/" scripts/04-upload_network.sh
