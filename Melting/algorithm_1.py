import pandas as pd
import os


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
        summation += float(matrix.at[x, y])
    return ((100 / length) * summation - 9372) / 398


def main():
    for i in os.listdir('../HMM/results/sequences'):
        with open(f'../HMM/results/sequences/{i}', 'r') as file:
            fasta = file.read()
        print(f'{i[:-4]:<25} {score_sequence(fasta):.4f}')


if __name__ == '__main__':
    main()
