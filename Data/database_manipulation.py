import gzip
import shutil
import os
from functools import partial
from tqdm import tqdm
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Other.utility import JobMachine
from warnings import simplefilter


def unzip_file(path: str) -> None:
    with gzip.open(path, 'rb') as f_in:
        with open(f'{path[:-6]}.txt', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def unzip_folder(folder: str) -> None:
    assert folder[-1] != '/'
    for file in tqdm([x for x in os.listdir(folder) if x[-3:] == '.gz']):
        unzip_file(f'{folder}/{file}')


def remove_zips(folder: str) -> None:
    assert folder[-1] != '/'
    for file in tqdm([x for x in os.listdir(folder) if x[-3:] == '.gz']):
        os.remove(f'{folder}/{file}')


def translate_file(file_path: str) -> list[SeqRecord]:
    sequences = [x for x in SeqIO.parse(file_path, "fasta")]
    return [i.translate() for i in sequences]


def convert_datafile(
    file_path: str,
    threshold: int
) -> str:
    sequences = translate_file(file_path)
    keep = []
    counter = 0
    for i in sequences:
        for x in i.seq.split('*'):
            if len(x) > threshold:
                counter += 1
                keep.append(f'>Sequence_{counter}')
                keep.append(str(x))
    return '\n'.join(keep)


def worker(
    d_folder: str,
    s_folder: str,
    thresh: int,
    file_name: str,
) -> None:
    with open(f'{s_folder}/{file_name}', 'w') as handle:
        handle.write(
            convert_datafile(f'{d_folder}/{file_name}', thresh)
        )


def convert_database(
    data_folder: str,
    save_folder: str,
    threshold: int,
    cpus: int
) -> None:
    simplefilter('ignore')
    assert data_folder[-1] != '/'
    assert save_folder[-1] != '/'
    new_worker = partial(worker, data_folder, save_folder, threshold)
    job_machine = JobMachine(
        processes=cpus,
        worker_func=new_worker,
        args_list=os.listdir(data_folder)
    )
    job_machine.start()


def main():
    os.chdir('/home/iwe22/zakaryjd/Metagenome/GenomeFiles/')
    file_count = 1
    sequences = 0
    data = []
    with open('master_4.faa', 'r') as file:
        while (line := file.readline()) != '':
            data.append(line)
            if line[0] == '>':
                sequences += 1
            elif sequences >= 2000:
                with open(f'database_4/file_{file_count}.txt', 'w') as sub_file:
                    sub_file.write(''.join(data))
                data = []
                sequences = 0
                file_count += 1


if __name__ == '__main__':
    main()
