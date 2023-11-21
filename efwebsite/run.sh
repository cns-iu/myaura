#!/bin/bash
set -ev

source ../db-config.sh
source scripts/var.sh

OLD_DICT_VERSION=20180706

sed -i "s/$OLD_DICT_VERSION/$DICT_VERSION/" src/01-parse_efwebsite_forum_mentions.py
sed -i "s/$OLD_DICT_VERSION/$DICT_VERSION/" src/02-count_comentions_samepost.py
sed -i "s/$OLD_DICT_VERSION/$DICT_VERSION/" src/04-build_network_samepost.py
sed -i "s/$OLD_DICT_VERSION/$DICT_VERSION/" scripts/04-upload_network.sh

pushd src
python 01-parse_efwebsite_forum_mentions.py
python 02-count_comentions_samepost.py
python 04-build_network_samepost.py
popd

chmod +x scripts/04-upload_network.sh
./scripts/04-upload_network.sh

# restore every file back
sed -i "s/$DICT_VERSION/$OLD_DICT_VERSION/" src/01-parse_efwebsite_forum_mentions.py
sed -i "s/$DICT_VERSION/$OLD_DICT_VERSION/" src/02-count_comentions_samepost.py
sed -i "s/$DICT_VERSION/$OLD_DICT_VERSION/" src/04-build_network_samepost.py
sed -i "s/$DICT_VERSION/$OLD_DICT_VERSION/" scripts/04-upload_network.sh
