from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Literal


EXAMPLE_INPUT = """
p=0,4 v=3,-3
p=6,3 v=-1,-3
p=10,3 v=-1,2
p=2,0 v=2,-1
p=0,0 v=1,3
p=3,0 v=-2,-2
p=7,6 v=-1,-3
p=3,0 v=-1,-2
p=9,3 v=2,3
p=7,3 v=-1,2
p=2,4 v=2,-3
p=9,5 v=-3,-3
"""


@dataclass
class Robot:
    px: int
    py: int
    vx: int
    vy: int


def parse_input(input: str) -> list[Robot]:
    robots: list[Robot] = []
    lines = input.strip().split("\n")
    for line in lines:
        matches = re.findall(r"-?\d+", line)
        px, py, vx, vy = [int(e) for e in matches]
        robot = Robot(px, py, vx, vy)
        robots.append(robot)
    return robots


def move_and_get_quadrant(
    robot: Robot, nb_steps: int, width: int, height: int
) -> Literal[-1, 0, 1, 2, 3]:
    new_px = (robot.px + robot.vx * nb_steps) % width
    new_py = (robot.py + robot.vy * nb_steps) % height
    if new_px == int(width / 2) or new_py == int(height / 2):
        # Center cross, ignore
        return -1
    elif new_px < width / 2 and new_py < height / 2:
        # Top left
        return 0
    elif new_px > width / 2 and new_py < height / 2:
        # Top right
        return 1
    elif new_px < width / 2 and new_py > height / 2:
        # Bottom left
        return 2
    elif new_px > width / 2 and new_py > height / 2:
        # Bottom right
        return 3
    # Theoritically unreachable case
    return -1


def compute_safety_factor_after_move(
    robots: list[Robot], nb_steps: int, width: int, height: int
) -> int:
    quadrants_count = [0] * 4
    for robot in robots:
        quadrant = move_and_get_quadrant(robot, nb_steps, width, height)
        if quadrant != -1:
            quadrants_count[quadrant] += 1

    safety_factor = (
        quadrants_count[0]
        * quadrants_count[1]
        * quadrants_count[2]
        * quadrants_count[3]
    )
    return safety_factor


def part1(input: str, width: int, height: int) -> int:
    robots = parse_input(input)
    return compute_safety_factor_after_move(robots, 100, width, height)


def part2(input: str) -> int:
    # Full bluff, let's assume that lowest safety = most clumped robots = picture
    # I hate this problem
    robots = parse_input(input)
    # Random assumtion of max iteration possible, because this solution does not
    # seem to be doable as an optimized loop-less algo
    max_iters = 10000
    safest_iter = 0
    min_safety = 1e12
    for i in range(max_iters):
        safety_factor = compute_safety_factor_after_move(robots, i, 101, 103)
        if safety_factor < min_safety:
            safest_iter = i
            min_safety = safety_factor
    return safest_iter


"""
Benchmark 1 (3 runs): ./venv/bin/python src/day14.py /tmp/.sops379695281/tmp-file554841587
    measurement          mean ± σ            min … max           outliers
    wall_time          3.06s  ± 49.2ms    3.03s  … 3.11s           0 ( 0%)
    peak_rss           14.7MB ± 48.9KB    14.6MB … 14.7MB          0 ( 0%)
    cpu_cycles         14.0G  ± 66.2M     14.0G  … 14.1G           0 ( 0%)
    instructions       36.3G  ±  222K     36.3G  … 36.3G           0 ( 0%)
    cache_references   28.2M  ± 4.46M     24.9M  … 33.3M           0 ( 0%)
    cache_misses       4.97M  ± 2.33M     3.54M  … 7.65M           0 ( 0%)
    branch_misses      44.5M  ± 1.27M     43.5M  … 45.9M           0 ( 0%)
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (
            Path(__file__).parent.parent / "inputs" / "2024" / "day14.txt"
        ).read_text()

    assert part1(EXAMPLE_INPUT, 11, 7) == 12
    result1 = part1(input_text, 101, 103)
    print(result1)

    result2 = part2(input_text)
    print(result2)
