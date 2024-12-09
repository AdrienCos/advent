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

type Equation = tuple[int, tuple[int, ...]]


def parse_input(input: str) -> list[Equation]:
    lines = input.strip().split("\n")
    equations: list[Equation] = []
    for line in lines:
        (result_raw, operands_raw) = line.split(": ")
        result = int(result_raw)
        operands = tuple([int(op) for op in (operands_raw.split(" "))])
        equations.append((result, operands))
    return equations


def try_solve_recursive(
    target_value: int, current_value: int, remaining_operands: tuple[int, ...]
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


def try_solve_recursive_advanced_backwards(
    current_value: int,
    remaining_operands: tuple[int, ...],
    # Not computing the length at each iteration saves a tiny amount of time
    nb_remaining_operands: int,
) -> bool:
    if current_value == 0:
        return True
    elif current_value < 0:
        return False
    elif nb_remaining_operands == 0:
        return False
    else:
        new_operand = remaining_operands[-1]
        if current_value == new_operand:
            return True

        # Multiply case
        if current_value % new_operand == 0:
            multiply_result = try_solve_recursive_advanced_backwards(
                int(current_value / new_operand),
                remaining_operands[:-1],
                nb_remaining_operands - 1,
            )
        else:
            multiply_result = False

        # Concat case
        if str(current_value).endswith(str(new_operand)):
            try:
                new_current_value = int(str(current_value)[: -len(str(new_operand))])
            except ValueError:
                new_current_value = 0
            concat_result = try_solve_recursive_advanced_backwards(
                new_current_value,
                remaining_operands[:-1],
                nb_remaining_operands - 1,
            )
        else:
            concat_result = False

        # Add case
        if current_value > new_operand:
            add_result = try_solve_recursive_advanced_backwards(
                current_value - new_operand,
                remaining_operands[:-1],
                nb_remaining_operands - 1,
            )
        else:
            return False

        return multiply_result or concat_result or add_result


def part1(input: str) -> int:
    equations = parse_input(input)
    count = 0
    for equation in equations:
        if try_solve_recursive(equation[0], equation[1][0], equation[1][1:]):
            count += equation[0]
    return count


def part2(input: str) -> int:
    equations = parse_input(input)
    count = 0
    for equation in equations:
        if try_solve_recursive_advanced_backwards(
            equation[0], equation[1], len(equation[1])
        ):
            count += equation[0]
    return count


"""
Benchmark 1 (44 runs): ./venv/bin/python src/day07.py /tmp/.sops2502108391/tmp-file3713580327
    measurement          mean ± σ            min … max           outliers
    wall_time           114ms ± 1.35ms     112ms …  118ms          1 ( 2%)
    peak_rss           12.8MB ± 41.8KB    12.7MB … 12.9MB          5 (11%)
    cpu_cycles          513M  ± 4.81M      508M  …  524M           1 ( 2%)
    instructions       1.23G  ± 1.18M     1.22G  … 1.23G           0 ( 0%)
    cache_references   5.31M  ± 56.0K     5.18M  … 5.52M           3 ( 7%)
    cache_misses        325K  ± 48.8K      277K  …  600K           1 ( 2%)
    branch_misses      2.20M  ±  125K     2.08M  … 2.56M           1 ( 2%)
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (Path(__file__).parent.parent / "inputs" / "day07.txt").read_text()

    assert part1(EXAMPLE_INPUT) == 3749
    result1 = part1(input_text)
    print(result1)

    assert part2(EXAMPLE_INPUT) == 11387
    result2 = part2(input_text)
    print(result2)
