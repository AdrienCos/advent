import itertools
from pathlib import Path
import sys


EXAMPLE_INPUT = """
............
........0...
.....0......
.......0....
....0.......
......A.....
............
............
........A...
.........A..
............
............
"""

type Coords = tuple[int, int]
type Frequency = str


def add_coords(coord_1: Coords, coord_2: Coords) -> Coords:
    return (coord_1[0] + coord_2[0], coord_1[1] + coord_2[1])


def sub_coords(coord_1: Coords, coord_2: Coords) -> Coords:
    return (coord_1[0] - coord_2[0], coord_1[1] - coord_2[1])


class Map:
    width: int
    height: int
    frequencies: set[Frequency]
    antennas: dict[Frequency, set[Coords]]

    def __init__(self, input_str: str) -> None:
        lines = input_str.strip().split("\n")
        self.frequencies = set()
        self.antennas = {}
        for i, line in enumerate(lines):
            for j, cell in enumerate(line):
                if cell != ".":
                    self.frequencies.add(cell)
                    if self.antennas.get(cell, None) is None:
                        self.antennas[cell] = set()
                    self.antennas[cell].add((i, j))
        self.height = len(lines)
        self.width = len(lines[0])

    def inbounds(self, coords: Coords) -> bool:
        if (
            coords[0] < 0
            or coords[0] >= self.height
            or coords[1] < 0
            or coords[1] >= self.width
        ):
            return False
        return True

    def antinodes(self, ant_1: Coords, ant_2: Coords) -> list[Coords]:
        antinodes: list[Coords] = []
        delta = sub_coords(ant_1, ant_2)
        ant_1_minus = sub_coords(ant_1, delta)
        if self.inbounds(ant_1_minus) and ant_1_minus != ant_2:
            antinodes.append(ant_1_minus)
        ant_1_plus = add_coords(ant_1, delta)
        if self.inbounds(ant_1_plus) and ant_1_plus != ant_2:
            antinodes.append(ant_1_plus)
        ant_2_minus = sub_coords(ant_2, delta)
        if self.inbounds(ant_2_minus) and ant_2_minus != ant_1:
            antinodes.append(ant_2_minus)
        ant_2_plus = add_coords(ant_2, delta)
        if self.inbounds(ant_2_plus) and ant_2_plus != ant_1:
            antinodes.append(ant_2_plus)
        return antinodes

    def antinodes_with_resonance(self, ant_1: Coords, ant_2: Coords) -> list[Coords]:
        antinodes: list[Coords] = [ant_1, ant_2]
        delta = sub_coords(ant_1, ant_2)
        # Start from ant_1, add delta until OOB
        node = ant_1
        while True:
            node = add_coords(node, delta)
            if not self.inbounds(node):
                break
            antinodes.append(node)
        node = ant_1
        while True:
            node = sub_coords(node, delta)
            if not self.inbounds(node):
                break
            antinodes.append(node)
        # Start from ant_1, subtract delta until OOB
        return antinodes


def parse_input(input: str) -> Map:
    map = Map(input)
    return map


def part1(input: str) -> int:
    map = parse_input(input)
    antinodes: set[Coords] = set()
    for frequency in map.frequencies:
        for ant_pairs in itertools.combinations(map.antennas[frequency], 2):
            pair_antinodes = map.antinodes(*ant_pairs)
            antinodes |= set(pair_antinodes)
    return len(antinodes)


def part2(input: str) -> int:
    map = parse_input(input)
    antinodes: set[Coords] = set()
    for frequency in map.frequencies:
        for ant_pairs in itertools.combinations(map.antennas[frequency], 2):
            pass
            pair_antinodes = map.antinodes_with_resonance(*ant_pairs)
            antinodes |= set(pair_antinodes)
    return len(antinodes)


"""
Benchmark 1 (213 runs): ./venv/bin/python src/day08.py /tmp/.sops3766800262/tmp-file512908338
    measurement          mean ± σ            min … max           outliers
    wall_time          23.3ms ± 1.09ms    22.3ms … 32.8ms         12 ( 6%)
    peak_rss           12.7MB ± 81.8KB    12.6MB … 12.9MB          0 ( 0%)
    cpu_cycles         95.6M  ± 2.03M     92.6M  …  106M           7 ( 3%)
    instructions        124M  ± 76.5K      124M  …  124M           0 ( 0%)
    cache_references   5.17M  ± 85.9K     5.03M  … 5.84M           8 ( 4%)
    cache_misses        246K  ± 97.2K      123K  …  601K           6 ( 3%)
    branch_misses       892K  ± 11.5K      876K  …  984K           6 ( 3%)
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (Path(__file__).parent.parent / "inputs" / "day08.txt").read_text()
    assert part1(EXAMPLE_INPUT) == 14
    result1 = part1(input_text)
    print(result1)

    assert part2(EXAMPLE_INPUT) == 34
    result2 = part2(input_text)
    print(result2)
