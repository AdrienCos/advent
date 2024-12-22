from collections import deque
from pathlib import Path
import sys


EXAMPLE_INPUT = """
1
10
100
2024
"""

TEST_INPUT_1 = """
1
2
3
2024
"""


def parse_input(input: str) -> list[int]:
    secrets = [int(e) for e in input.strip().split()]
    return secrets


def mix(a: int, b: int) -> int:
    return a ^ b


def prune(a: int) -> int:
    return a & (2**24 - 1)


def cycle(val: int) -> int:
    val = mix(val << 6, val)
    val = prune(val)
    val = mix(val >> 5, val)
    val = prune(val)
    val = mix(val << 11, val)
    val = prune(val)
    return val


def part1(input: str) -> int:
    secrets = parse_input(input)
    count = 0
    for secret in secrets:
        for _ in range(2000):
            secret = cycle(secret)
        count += secret
    return count


def part2(input: str) -> int:
    secrets = parse_input(input)
    count = 0
    sequences_prices: dict[tuple[int, ...], int] = {}
    for secret in secrets:
        sequence: deque[int] = deque()
        # Do the first four iterations to be ready to generate the first pattern
        for _ in range(4):
            new_secret = cycle(secret)
            sequence.append(((new_secret % 10) - (secret % 10)))
            secret = new_secret
        # Set of sequences already seen while iterating on this secret
        seen: set[tuple[int, ...]] = set()
        seen.add(tuple(sequence))
        for _ in range(1996):
            new_secret = cycle(secret)
            sequence.popleft()
            sequence.append((new_secret % 10) - (secret % 10))
            secret = new_secret
            sequence_id = tuple(sequence)
            if sequence_id not in seen:
                seen.add(sequence_id)
                if sequence_id not in sequences_prices:
                    sequences_prices[sequence_id] = 0
                sequences_prices[sequence_id] += secret % 10
        count += secret

    most_valuable_sequence_price = max(sequences_prices.values())
    return most_valuable_sequence_price


"""
Benchmark 1: ./venv/bin/python src/day22.py /var/folders/fm/891_8yt158b05hy09ypkjyt40000gn/T/.sops2393224265/tmp-file3319837045
    Time (mean ± σ):      7.071 s ±  0.299 s    [User: 6.947 s, System: 0.041 s]
    Range (min … max):    6.685 s …  7.576 s    10 runs
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (Path(__file__).parent.parent / "inputs" / "day22.txt").read_text()

    assert part1(EXAMPLE_INPUT) == 37327623
    result1 = part1(input_text)
    print(result1)

    assert part2(TEST_INPUT_1) == 23
    result2 = part2(input_text)
    print(result2)
