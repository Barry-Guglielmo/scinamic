#!/bin/bash
source ../venv/bin/activate
python ../main.py -d -f
di_main -s /vol/bluebird/seurat/LiveDesign/DataIntegrator/scinamic_di_settings_di_formatted.json
echo $(date) &>>scinamic.log
sleep 1800
