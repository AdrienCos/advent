from pathlib import Path
import sys


EXAMPLE_INPUT = """
"""


def parse_input(input: str) -> None:
    return


def part1(input: str) -> int:
    count = 0
    return count


def part2(input: str) -> int:
    count = 0
    return count


"""
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (
            Path(__file__).parent.parent / "inputs" / "YYYY" / "dayXX.txt"
        ).read_text()

    assert part1(EXAMPLE_INPUT) == -1
    result1 = part1(input_text)
    print(result1)

    assert part2(EXAMPLE_INPUT) == -1
    result2 = part2(input_text)
    print(result2)
