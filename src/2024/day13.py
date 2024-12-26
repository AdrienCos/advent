from dataclasses import dataclass
from pathlib import Path
import sys


EXAMPLE_INPUT = """
Button A: X+94, Y+34
Button B: X+22, Y+67
Prize: X=8400, Y=5400

Button A: X+26, Y+66
Button B: X+67, Y+21
Prize: X=12748, Y=12176

Button A: X+17, Y+86
Button B: X+84, Y+37
Prize: X=7870, Y=6450

Button A: X+69, Y+23
Button B: X+27, Y+71
Prize: X=18641, Y=10279
"""


@dataclass
class Machine:
    ax: int
    ay: int
    bx: int
    by: int
    px: int
    py: int


def parse_input(input: str) -> list[Machine]:
    machines: list[Machine] = []
    machines_str = input.strip().split("\n\n")
    for machine_str in machines_str:
        a_line, b_line, p_line = machine_str.strip().split("\n")
        _, _, ax_str, ay_str = a_line.split()
        _, _, bx_str, by_str = b_line.split()
        _, px_str, py_str = p_line.split()
        ax = int(ax_str[2:-1])
        ay = int(ay_str[2:])
        bx = int(bx_str[2:-1])
        by = int(by_str[2:])
        px = int(px_str[2:-1])
        py = int(py_str[2:])
        machine = Machine(ax, ay, bx, by, px, py)
        machines.append(machine)
    return machines


def solve_machine(m: Machine, max_presses: int | None = None) -> int:
    det = (m.ax * m.by) - (m.ay * m.bx)
    if det == 0:
        # Matrix is non-inversible
        return 0
    nb_a = ((m.by * m.px) - (m.bx * m.py)) / det
    nb_b = ((m.ax * m.py) - (m.ay * m.px)) / det
    if nb_a < 0 or nb_b < 0:
        return 0
    if max_presses is not None and (nb_a > max_presses or nb_b > max_presses):
        return 0
    if int(nb_a) != nb_a:
        return 0
    if int(nb_b) != nb_b:
        return 0
    return int(nb_a) * 3 + int(nb_b) * 1


def part1(input: str) -> int:
    machines = parse_input(input)
    count = 0
    for machine in machines:
        count += solve_machine(machine, 100)
    return count


def part2(input: str) -> int:
    machines = parse_input(input)
    count = 0
    for machine in machines:
        machine.px += 10000000000000
        machine.py += 10000000000000
        count += solve_machine(
            machine,
        )
    return count


"""
Benchmark 1 (152 runs): ./venv/bin/python src/day13.py /tmp/.sops857850962/tmp-file239295447
    measurement          mean ± σ            min … max           outliers
    wall_time          32.5ms ±  965us    31.3ms … 38.4ms         11 ( 7%)
    peak_rss           14.4MB ± 65.5KB    14.2MB … 14.5MB          0 ( 0%)
    cpu_cycles          144M  ± 3.31M      140M  …  158M          12 ( 8%)
    instructions        191M  ±  137K      191M  …  191M           1 ( 1%)
    cache_references   7.59M  ± 75.4K     7.40M  … 7.87M           5 ( 3%)
    cache_misses        410K  ±  187K      207K  … 1.10M          11 ( 7%)
    branch_misses      1.32M  ± 7.00K     1.30M  … 1.34M           1 ( 1%)
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (
            Path(__file__).parent.parent / "inputs" / "2024" / "day13.txt"
        ).read_text()

    assert part1(EXAMPLE_INPUT) == 480
    result1 = part1(input_text)
    print(result1)

    result2 = part2(input_text)
    print(result2)
