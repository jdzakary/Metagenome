import gzip
import shutil
import os
from tqdm import tqdm
from Bio import SeqIO


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


def translate_file(
    input_path: str,
    save_path: str
):
    sequences = [x for x in SeqIO.parse(input_path, "fasta")]
    translated = [i.translate() for i in sequences]
    for i in translated:
        print(i.seq)


def main():
    translate_file(
        '/home/iwe22/zakaryjd/Metagenome/GenomeFiles/'
        'database_1/OceanDNA-b33934.txt',
        'hello'
    )


if __name__ == '__main__':
    main()
