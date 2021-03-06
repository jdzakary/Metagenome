import time
from tqdm import tqdm
from typing import Callable, Iterable
from Bio import Entrez, SeqIO
from Bio.SeqRecord import SeqRecord


def read_entrez(func: Callable) -> Callable:
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        return Entrez.read(result)
    return inner


@read_entrez
def list_ncbi_databases() -> dict[str: list[str]]:
    return Entrez.einfo()


def fetch_sequence(
    code: str,
    db: str = 'protein'
) -> SeqRecord:
    """
    Fetch sequence data from a variety of NCBI Databases
    :param code:
        The identifier to be fetched
    :param db:
        The NCBI database to search
    :return:
        A BioPython sequence record object that contains the queried sequence
    """
    handle = Entrez.efetch(db=db, rettype='fasta', id=code)
    sequence: SeqRecord = SeqIO.read(handle, format='fasta')
    return sequence


def save_fasta(
    sequences: list[SeqRecord],
    save_path: str
) -> None:
    """
    Save a list of SeqRecord objects to a single fasta file on disk
    :param sequences:
        A list of the sequence objects to be saved
    :param save_path:
        The path of the fasta file
    :return:
    """
    with open(save_path, 'w') as file:
        SeqIO.write(sequences, file, 'fasta')


def mega_fasta(
    codes: Iterable[str],
    save_path: str,
    db: str = 'protein',
    pbar: bool = False
) -> None:
    """
    Query a group of sequences from NCBI databases and save them to a single
    fasta file
    :param codes:
        A list of the codes to query NCBI for
    :param save_path:
        The path of the output file
    :param db:
        Which NCBI database you would like to query
    :param pbar:
        If you would like to have a progress bar displayed in the terminal
    :return:
    """
    sequences = []
    for i in (tqdm(codes) if pbar else codes):
        sequences.append(fetch_sequence(i, db))
        time.sleep(0.25)
    save_fasta(sequences, save_path)


def main():
    Entrez.email = 'jonathan.d.zakary@vanderbilt.edu'
    # Protein ID, Then Nucleotide ID
    codes = {
        'ADV92526.1': 'HQ147785.1',
        'ADV92528.1': 'HQ147787.1',
        'AFA45122.1': 'JQ339742.1',
        'CAH17554.1': 'AJ810119.1',
        'BAO42835.1': 'AB728484.1',
        'BAK48590.1': 'AB445476.2',
        'CBY05529.1': 'FR727680.1',
        'CBY05530.1': 'FR727681.1',
        'AEV21261.1': 'HQ704839.1'
    }
    mega_fasta(
        codes=codes.keys(),
        save_path='targets/targets_3.txt',
        db='protein',
        pbar=True
    )


if __name__ == '__main__':

    main()
