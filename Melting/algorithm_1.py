import pandas as pd
from HMM.hmm import find_sequence


def fetch_matrix() -> pd.DataFrame:
    return pd.read_csv('matrix.csv', index_col=0)


def show_matrix() -> None:
    pd.set_option('display.width', None)
    pd.set_option('display.max_columns', None)
    matrix = fetch_matrix()
    print(matrix.info())
    print(matrix)


def score_sequence(sequence: str) -> float:
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
) -> None:
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
    for file, score in scores.items():
        print(f'{file:<25} {score:.4f}')


def main():
    scan_database(2, 4, True)


if __name__ == '__main__':
    main()
