select id_pm, prediction, classifier, prediction_conf from abstract_classification_clinical_selected_LR_180717 where classifier="LR" and prediction <> 0;
