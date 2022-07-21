from Bio import pairwise2


class Alignment:
    def __init__(
        self,
        seq_a: str,
        seq_b: str,
        score: float,
        start: int,
        end: int
    ):
        self.__seq_a = seq_a
        self.__seq_b = seq_b
        self.__score = score
        self.__start = start
        self.__end = end

    @property
    def seqA(self) -> str:
        return self.__seq_a

    @property
    def seqB(self) -> str:
        return self.__seq_b

    @property
    def score(self) -> float:
        return self.__score

    @property
    def start(self) -> int:
        return self.__start

    @property
    def end(self) -> int:
        return self.__end


def create_alignment(
    sequence_1: str,
    sequence_2: str
) -> Alignment:
    alignments: list[Alignment] = pairwise2.align.globalxx(
        sequence_1, sequence_2
    )
    return max(alignments, key=lambda x: x.score)


def contains_targets(
    alignment: Alignment,
    targets: list[int]
) -> bool:
    counter = 0
    for a, b in zip(alignment.seqA, alignment.seqB):
        if a != '-':
            counter += 1
        if counter in targets and a != b:
            print(counter, a, b)
            return False
    return True


def scan_database(
    database: int,
    model: int,
    filtered: bool
) -> None:
    pass


def main():
    with open('../HMM/results/sequences/7nei_ref.txt', 'r') as file:
        sequence_1 = file.read()
    with open('../HMM/results/sequences/OceanDNA-b41030_1870.txt', 'r') as file:
        sequence_2 = file.read()
    alignment = create_alignment(sequence_1, sequence_2)
    print(alignment.seqA)
    print(alignment.seqB)
    result = contains_targets(alignment, [130, 176, 208])
    print(result)


if __name__ == "__main__":
    main()
