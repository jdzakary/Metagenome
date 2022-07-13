import os
import pandas as pd
from functools import partial
from typing import Union, TextIO

from Other.utility import JobMachine, simple_run


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
        worker_func=worker,
        args_list=files
    )
    machine.start()
    for i in files:
        if os.path.getsize(f'{save_folder}/{i}') <= 2000:
            os.remove(f'{save_folder}/{i}')


def is_number(x: str) -> Union[float, None]:
    try:
        return float(x)
    except ValueError:
        return None


def extract_results(file_path: str) -> pd.DataFrame:
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


def get_lines(
    file: TextIO,
    line_numbers: list[int]
):
    return (x for i, x in enumerate(file) if i in line_numbers)


def find_sequence(
    data_folder: str,
    row: pd.Series
) -> str:
    assert data_folder[-1] != '/'
    file_path = f'{data_folder}/{row["File"]}.txt'
    number = row["SubFile"] * 2 - 1
    with open(file_path, 'r') as file:
        line = get_lines(file, [number])
        data: str = list(line)[0]
    return data[row["Ali-From"]-1:row["Ali-To"]]


def main():
    parse_database_multi(
        model_file='models/model_3.hmm',
        data_folder='/home/iwe22/zakaryjd/Metagenome/GenomeFiles/database_2',
        save_folder='/home/iwe22/zakaryjd/Python_Projects/Metagenome/HMM'
                    '/search_output/database_2_model_3',
        processes=10
    )


if __name__ == '__main__':
    main()
