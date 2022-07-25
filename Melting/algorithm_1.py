import pandas as pd
from HMM.hmm import find_sequence


def fetch_matrix() -> pd.DataFrame:
    """
    Fetch the weight matrix from file
    :return:
    """
    return pd.read_csv('matrix.csv', index_col=0)


def show_matrix() -> None:
    """
    For visual inspection of the matrix
    :return:
    """
    pd.set_option('display.width', None)
    pd.set_option('display.max_columns', None)
    matrix = fetch_matrix()
    print(matrix.info())
    print(matrix)


def score_sequence(sequence: str) -> float:
    """
    Score a protein sequence using the algorithm
    :param sequence:
        The protein sequence as a string
    :return:
        The score value
    """
    matrix = fetch_matrix()
    length = len(sequence)
    summation = 0
    for i in range(length - 1):
        x = sequence[i]
        y = sequence[i+1]
        summation += matrix.at[x, y]
    return ((100 / length) * summation - 9372) / 398


def scan_database(
    database: int,
    model: int,
    filtered: bool
) -> dict[str, float]:
    """
    Scan the summary file (csv) of the HMM Search Results and apply the
    algorithm to estimate their melting temperatures
    :param database:
        The database id
    :param model:
        The model id
    :param filtered:
        Use the filtered csv file?
    :return:
    """
    data = pd.read_csv(
        f'../HMM/results/summary/database_{database}_model_{model}'
        f'{"_filtered" if filtered else ""}.csv'
    )
    scores = {}
    for idx, values in data.iterrows():
        sequence = find_sequence(
            f'/home/iwe22/zakaryjd/Metagenome/GenomeFiles/database_{database}',
            row=values
        )
        scores[
            f'{values["File"]}_{values["SubFile"]}'
        ] = score_sequence(sequence)
    scores = {
        x: y for x, y in sorted(
            scores.items(), key=lambda j: j[1], reverse=True
        )
    }
    return scores


def create_fold_file(
    database: int,
    model: int,
    filtered: bool,
    threshold: float = 1.0
) -> None:
    """
    Create the CSV File with desired sequences for AlphaFold2 Script
    :param database:
        The database id
    :param model:
        The model id
    :param filtered:
        Use filtered sequence matches
    :param threshold:
        Do not include any sequences with an algorithm_1 index lower than
        this threshold
    :return:
    """
    data = pd.read_csv(
        f'../HMM/results/summary/database_{database}_model_{model}'
        f'{"_filtered" if filtered else ""}.csv'
    )
    scores = scan_database(database, model, filtered)
    results = []
    data_folder = f'/home/iwe22/zakaryjd/Metagenome' \
                  f'/GenomeFiles/database_{database}'
    save_path = f'../Folding/fold_files' \
                f'/a1_d{database}_m{model}{"_f" if filtered else ""}.csv'
    for key, value in scores.items():
        if value >= threshold:
            file, sub_file = key.split('_')
            index = data[
                (data['File'] == file) & (data['SubFile'] == int(sub_file))
            ].index[0]
            results.append([key, find_sequence(data_folder, data.loc[index])])
    results = pd.DataFrame(results)
    results.columns = ['id', 'sequence']
    results.to_csv(save_path, index=False)


def main():
    create_fold_file(2, 4, True)


if __name__ == '__main__':
    main()
