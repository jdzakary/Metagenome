#!/bin/bash
CONTAINER=/home/iwe22/zakaryjd/Metagenome/ColabFold/colabfold_1.2.0_multimer.sif
SCRIPT="colabfold_batch --num-recycle 3 ./fold_files/a1_d2_m4_f.csv ./out_folder"
singularity exec --nv $CONTAINER $SCRIPT