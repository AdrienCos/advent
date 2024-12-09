from pathlib import Path
import sys


EXAMPLE_INPUT = """
190: 10 19
3267: 81 40 27
83: 17 5
156: 15 6
7290: 6 8 6 15
161011: 16 10 13
192: 17 8 14
21037: 9 7 18 13
292: 11 6 16 20
"""

type Equation = tuple[int, list[int]]


def parse_input(input: str) -> list[Equation]:
    lines = input.strip().split("\n")
    equations: list[Equation] = []
    for line in lines:
        (result_raw, operands_raw) = line.split(": ")
        result = int(result_raw)
        operands = [int(op) for op in (operands_raw.split(" "))]
        equations.append((result, operands))
    return equations


def try_solve_recursive(
    target_value: int, current_value: int, remaining_operands: list[int]
) -> bool:
    if current_value == target_value:
        return True
    elif current_value > target_value:
        return False
    elif len(remaining_operands) == 0:
        return False
    else:
        new_operand = remaining_operands[0]
        return try_solve_recursive(
            target_value, current_value + new_operand, remaining_operands[1:]
        ) or try_solve_recursive(
            target_value, current_value * new_operand, remaining_operands[1:]
        )


def is_solvable(equation: Equation) -> bool:
    result = try_solve_recursive(equation[0], equation[1][0], equation[1][1:])
    return result


def part1(input: str) -> int:
    equations = parse_input(input)
    count = 0
    for equation in equations:
        if is_solvable(equation):
            count += equation[0]
    return count


def part2(input: str) -> int:
    return 0


"""
Benchmark 1 (10 runs): ./venv/bin/python src/day09.py /tmp/.sops3896349036/tmp-file421800216
    measurement          mean ± σ            min … max           outliers
    wall_time           520ms ± 14.7ms     506ms …  552ms          0 ( 0%)
    peak_rss           19.6MB ± 65.3KB    19.5MB … 19.7MB          0 ( 0%)
    cpu_cycles         1.88G  ± 19.9M     1.82G  … 1.89G           1 (10%)
    instructions       5.75G  ± 46.8M     5.66G  … 5.79G           1 (10%)
    cache_references   2.86M  ± 98.6K     2.66M  … 2.98M           0 ( 0%)
    cache_misses        588K  ±  150K      347K  …  782K           0 ( 0%)
    branch_misses      1.16M  ± 94.0K      991K  … 1.25M           0 ( 0%)
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (Path(__file__).parent.parent / "inputs" / "day07.txt").read_text()

    assert part1(EXAMPLE_INPUT) == 3749
    result1 = part1(input_text)
    print(result1)

    assert part2(EXAMPLE_INPUT) == 0
    result2 = part2(input_text)
    print(result2)
