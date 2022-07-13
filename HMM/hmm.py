import os
from functools import partial
from typing import Union
from subprocess import Popen, PIPE
from Other.utility import JobMachine


def simple_run(
    command: Union[list[str], str]
) -> str:
    process = Popen(command, shell=True, stdout=PIPE)
    output = list()
    while True:
        output.append(process.stdout.readline().strip())
        if process.poll() is not None:
            break
    return '\n'.join([x.decode() for x in output])


def hmm_build(
    alignment_file: str,
    save_path: str,
    log_path: str
) -> None:
    log = simple_run(f'hmmbuild {save_path} {alignment_file}')
    with open(log_path, 'w') as file:
        file.write(log)


def create_worker(
    model_file: str,
    data_folder: str,
    save_folder: str,
    name: str
) -> None:
    assert data_folder[-1] != '/'
    assert save_folder[-1] != '/'
    log = simple_run(
        f'hmmsearch {model_file} {data_folder}/{name} > {save_folder}/{name}'
    )


def parse_database_multi(
    model_file: str,
    data_folder: str,
    save_folder: str,
    processes: int
) -> None:
    assert data_folder[-1] != '/'
    assert save_folder[-1] != '/'
    files = os.listdir(data_folder)
    worker = partial(create_worker, model_file, data_folder, save_folder)
    machine = JobMachine(
        processes=processes,
        total_jobs=len(files),
        worker_func=worker,
        args_list=files
    )
    machine.start()
    for i in files:
        if os.path.getsize(f'{save_folder}/{i}') <= 2000:
            os.remove(f'{save_folder}/{i}')


def main():
    parse_database_multi(
        model_file='models/model_2.hmm',
        data_folder='/home/iwe22/zakaryjd/Metagenome/GenomeFiles/database_1',
        save_folder='/home/iwe22/zakaryjd/Python_Projects'
                    '/Metagenome/HMM/search_output/database_1_model_2',
        processes=10
    )


if __name__ == '__main__':
    main()
