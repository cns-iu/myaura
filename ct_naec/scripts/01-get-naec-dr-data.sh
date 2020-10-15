#!/bin/bash
source constants.sh
set -ev

URL=https://www.naec-epilepsy.org/wp-admin/admin-ajax.php?action=get_results_ajax
wget "$URL" -O $OUT/doctor-data.raw.json
