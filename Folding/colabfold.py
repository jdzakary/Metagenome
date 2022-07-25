import os
import pandas as pd


def create_fold_command(input_file: str) -> None:
    data = [
        '#!/bin/bash',
        'CONTAINER=/home/iwe22/zakaryjd/Metagenome/ColabFold/colabfold_1.2.0_multimer.sif',
        f'SCRIPT="colabfold_batch --num-recycle 3 ./fold_files/{input_file}.csv ./out_folder"',
        'singularity exec --nv $CONTAINER $SCRIPT'
    ]
    with open('submit_job.sh', 'w') as file:
        file.write('\n'.join(data))


def clean_output(input_file: str) -> None:
    files = os.listdir('out_folder')
    structures = pd.read_csv(f'fold_files/{input_file}.csv')['id'].tolist()
    for i in structures:
        try:
            os.mkdir(f'results/{i}')
        except FileExistsError:
            pass
    for name in files:
        for query in structures:
            if query in name:
                os.rename(f'out_folder/{name}', f'results/{query}/{name}')


def main():
    clean_output('a1_d2_m4_f')


if __name__ == '__main__':
    main()
