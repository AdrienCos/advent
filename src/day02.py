from pathlib import Path
import sys


EXAMPLE_INPUT = """
7 6 4 2 1
1 2 7 8 9
9 7 6 2 1
1 3 2 4 5
8 6 4 4 1
1 3 6 7 9
"""


def parse_input(input: str) -> list[list[int]]:
    lines = input.strip().split("\n")
    reports: list[list[int]] = []
    for line in lines:
        report = [int(x) for x in line.split()]
        reports.append(report)
    return reports


def is_safe(report: list[int]) -> bool:
    # Check if report is monotonic
    if sorted(report) != report and sorted(report, reverse=True) != report:
        return False
    # Check if rate of change is between 1 and 3
    diffs = [abs(report[i] - report[i - 1]) for i in range(1, len(report))]
    if all(diff >= 1 and diff <= 3 for diff in diffs):
        return True
    return False


def part1(input: str) -> int:
    reports = parse_input(input)
    safe_count = [is_safe(report) for report in reports].count(True)
    return safe_count


def part2(input: str) -> int:
    reports = parse_input(input)
    safe_count = 0
    for report in reports:
        sub_reports = [report[0:i] + report[i + 1 :] for i in range(len(report))] + [
            report
        ]
        safe_count += any([is_safe(sub_report) for sub_report in sub_reports])
    return safe_count


"""
Benchmark 1 (132 runs): python day02.py
    measurement          mean ± σ            min … max           outliers
    wall_time          38.0ms ± 4.08ms    33.9ms … 49.6ms          2 ( 2%)
    peak_rss           12.6MB ±  113KB    12.3MB … 12.8MB          0 ( 0%)
    cpu_cycles          110M  ± 9.79M     64.2M  …  132M           5 ( 4%)
    instructions        252M  ± 15.7M      179M  …  264M           2 ( 2%)
    cache_references    951K  ±  110K      431K  … 1.22M           5 ( 4%)
    cache_misses       77.4K  ± 51.7K     15.3K  …  319K          12 ( 9%)
    branch_misses       709K  ±  106K      184K  …  810K           6 ( 5%
"""
if __name__ == "__main__":
    INPUT_TEXT = Path(sys.argv[1]).read_text()

    assert part1(EXAMPLE_INPUT) == 2
    result1 = part1(INPUT_TEXT)
    print(result1)

    assert part2(EXAMPLE_INPUT) == 4
    result2 = part2(INPUT_TEXT)
    print(result2)
