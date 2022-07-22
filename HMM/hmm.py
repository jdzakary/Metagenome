import os
import pandas as pd
from functools import partial
from typing import Union, TextIO, Iterable
from Other.utility import JobMachine, simple_run


def hmm_build(
    alignment_file: str,
    save_path: str,
    log_path: str
) -> None:
    """
    Python wrapper to build an HMM Model from a Stockholm Alignment File
    :param alignment_file:
        The path of the alignment file
    :param save_path:
        Where to save the model
    :param log_path:
        Where to save the logs from std::out
    :return:
    """
    log = simple_run(f'hmmbuild {save_path} {alignment_file}')
    with open(log_path, 'w') as file:
        file.write(log)


def create_worker(
    model_file: str,
    data_folder: str,
    save_folder: str,
    name: str
) -> None:
    """
    The worker function for the `parse_database_multi` multiprocessing function
    :param model_file:
        The path of the HMM Model File
    :param data_folder:
        The path of the database folder
    :param save_folder:
        The folder to save results inside
    :param name:
        The name of the fasta file being searched
    :return:
    """
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
    """
    Search a database folder for sequence matches using a HMM Model
    :param model_file:
        The path of the model file to use
    :param data_folder:
        The database folder
    :param save_folder:
        The folder to save results in
    :param processes:
        The number of worker processes to create
    :return:
    """
    assert data_folder[-1] != '/'
    assert save_folder[-1] != '/'
    files = os.listdir(data_folder)
    worker = partial(create_worker, model_file, data_folder, save_folder)
    machine = JobMachine(
        processes=processes,
        worker_func=worker,
        args_list=files
    )
    machine.start()
    for i in files:
        if os.path.getsize(f'{save_folder}/{i}') <= 2000:
            os.remove(f'{save_folder}/{i}')


def is_number(x: str) -> Union[float, None]:
    """
    Attempt to convert a string value to a float
    :param x:
        The string to convert
    :return:
        If valid conversion, return the floating point number, if invalid
        conversion, return None.
    """
    try:
        return float(x)
    except ValueError:
        return None


def extract_results(file_path: str) -> pd.DataFrame:
    """
    Extract the important details from the HMM Search Results File
    :param file_path:
        The HMM search results file
    :return:
        A dataframe containing the matches
    """
    # Fetch and Parse Data
    with open(file_path, 'r') as file:
        data = file.read()
    data = data.split('\n')
    table_idx: dict[str, tuple[int, int]] = {}
    start_idx = 0
    label = ''
    for key, row in enumerate(data):
        if row[0:2] == '>>':
            start_idx = key
            label = row[row.find('_')+1:row[3:].find(' ')+3]
        elif start_idx > 0 and len(row) == 0:
            table_idx[label] = (start_idx, key)
            start_idx = 0

    # Extract columns and rows from text
    frame = []
    for key, (start_idx, end_idx) in table_idx.items():
        for row_idx in range(start_idx+3, end_idx):
            # noinspection PyTypeChecker
            frame.append(
                [
                    y for x in data[row_idx].split(' ')
                    if (y := is_number(x)) is not None
                ] + [key]
            )

    # Setup Dataframe
    frame = pd.DataFrame(frame)
    frame.columns = [
        'Domain', 'Score', 'Bias', 'EValue(C)', 'EValue(I)', 'HMM-From',
        'HMM-To', 'Ali-From', 'Ali-To', 'Env-From', 'Env-To', 'Accuracy',
        'SubFile'
    ]
    frame.drop(columns='Domain', inplace=True)
    file_name = file_path[file_path.rfind('/') + 1:-4]
    frame.insert(0, column='File', value=file_name)
    frame.insert(1, 'SubFile', frame.pop('SubFile'))
    columns_int = [
        'HMM-From', 'HMM-To', 'Ali-From', 'Ali-To', 'Env-From', 'Env-To',
        'SubFile'
    ]
    for column in columns_int:
        frame[column] = frame[column].astype(int)

    # Return Results
    return frame


def search_results(result_folder: str) -> pd.DataFrame:
    """
    Compile all results from a folder of HMM result files
    :param result_folder:
        The folder with the HMM result files
    :return:
        A dataframe containing all sequence hits.
    """
    assert result_folder[-1] != '/'
    files = os.listdir(result_folder)
    data = extract_results(f'{result_folder}/{files[0]}')
    for i in files[1:]:
        data = pd.concat([data, extract_results(f'{result_folder}/{i}')])
    data.reset_index(inplace=True, drop=True)
    data['HMM-Length'] = data['HMM-To'] - data['HMM-From']
    data['Ali-Length'] = data['Ali-To'] - data['Ali-From']
    data['Env-Length'] = data['Env-To'] - data['Env-From']
    return data


def save_summary(folder_name: str) -> None:
    """
    Save a summary of the search results
    :param folder_name:
        The results folder name

    :return:
    """
    assert folder_name[-1] != '/'
    data = search_results(f'search_output/{folder_name}')
    data.sort_values(by='Accuracy', inplace=True, ascending=False)
    data.to_csv(f'results/summary/{folder_name}.csv', index=False)
    data[
        data['HMM-Length'] >= 200
    ].to_csv(f'results/summary/{folder_name}_filtered.csv', index=False)


def get_lines(
    file: TextIO,
    line_numbers: list[int]
) -> Iterable[str]:
    """
    Get the desired lines of a long file without having to handle the entire
    contents
    :param file:
        The TextIO handle (created by `with open(...) as file:`
    :param line_numbers:
        A list of integers indicating which line numbers should be fetched
    :return:
    """
    return (x for i, x in enumerate(file) if i in line_numbers)


def find_sequence(
    data_folder: str,
    row: pd.Series
) -> str:
    """
    Find the sequence corresponding to the record in the HMM Results
    :param data_folder:
        The database folder
    :param row:
        The pandas dataframe row of the sequence you wish to extract
    :return:
        The sequence as a string
    """
    assert data_folder[-1] != '/'
    file_path = f'{data_folder}/{row["File"]}.txt'
    number = row["SubFile"] * 2 - 1
    with open(file_path, 'r') as file:
        line = get_lines(file, [number])
        data = list(line)[0]
    return data[row["Ali-From"]-1:row["Ali-To"]]


def full_run(
    model_id: int,
    database_id: int,
    cpus: int
) -> None:
    """
    Full run of HMM model creation, searching the database, and parsing results
    :param model_id:
        The model id - should correspond to the alignment file id
        See code for the naming convention `alignment_{model_id}`
    :param database_id:
        The database_id - should correspond to the database folder name
        See code for the naming convention `database_{database_id}`
    :param cpus:
        The number of worker processes to spawn
    :return:
    """
    print('Checking for Alignment File')
    assert os.path.exists(f'../Data/alignments/alignment_{model_id}.txt')
    print('Checking for Database Folder')
    assert os.path.exists(
        f'/home/iwe22/zakaryjd/Metagenome/GenomeFiles/database_{database_id}'

    )
    try:
        os.mkdir(f'search_output/database_{database_id}_model_{model_id}')
    except FileExistsError:
        print('Output Folder Already Exists')
    else:
        print('Created Output Folder')
    print('Building HMM Model')
    hmm_build(
        alignment_file=f'../Data/alignments/alignment_{model_id}.txt',
        save_path=f'models/model_{model_id}.hmm',
        log_path=f'logs/log_{model_id}.txt'
    )
    assert os.path.exists(f'models/model_{model_id}.hmm')
    print('Searching Database Using HMM Model')
    parse_database_multi(
        model_file=f'models/model_{model_id}.hmm',
        data_folder=f'/home/iwe22/zakaryjd/Metagenome'
                    f'/GenomeFiles/database_{database_id}',
        save_folder=f'search_output/database_{database_id}_model_{model_id}',
        processes=cpus
    )


def main():
    pd.set_option('display.width', None)
    pd.set_option('display.max_columns', None)
    data = pd.read_csv('results/summary/database_2_model_4_filtered.csv')
    print(data[0:10])
    print(data[-10:])
    sequence = find_sequence(
        data_folder='/home/iwe22/zakaryjd/Metagenome/GenomeFiles/database_2',
        row=data.loc[73]
    )
    print(sequence)


if __name__ == '__main__':
    main()
