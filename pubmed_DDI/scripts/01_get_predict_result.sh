mysql --defaults-file=../../mysql.cnf --defaults-group-suffix=pubmed_ddi <../sql/invivo180717_all.sql >invivo_tmp.txt
mysql --defaults-file=../../mysql.cnf --defaults-group-suffix=pubmed_ddi <../sql/invitro180612_all.sql >invitro_tmp.txt
mysql --defaults-file=../../mysql.cnf --defaults-group-suffix=pubmed_ddi <../sql/clinical180717_all.sql >clinical_tmp.txt
awk '{print $1}' invivo_tmp.txt | sed 1d > invivo_LSVC_180717_allid.txt
awk '{print $1}' invitro_tmp.txt | sed 1d > invitro_LSVC_180612_allid.txt
awk '{print $1}' clinical_tmp.txt | sed 1d > clinical_LR_180717_allid.txt
mv invivo_tmp.txt invivo_all_conf.txt
mv invitro_tmp.txt invitro_all_conf.txt
mv clinical_tmp.txt clinical_all_conf.txt
