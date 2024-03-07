#!/bin/bash
cd /vol/bluebird/seurat/pro_serv/scinamic_integration
echo "Today's date is: $(date +'%Y-%m-%d')" | tee -a test.txt
source /vol/bluebird/seurat/pro_serv/scinamic_integration/venv/bin/activate
echo  'source' | tee -a test.txt
python /vol/bluebird/seurat/pro_serv/scinamic_integration/main.py -i
