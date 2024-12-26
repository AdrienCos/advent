import bisect
import collections
from pathlib import Path
import sys


EXAMPLE_INPUT = """2333133121414131402"""

type DiskMap = tuple[list[File], list[Hole]]
type File = tuple[int, list[int]]
type Hole = list[int]


def parse_input(input: str) -> DiskMap:
    map = [int(e) for e in input.strip()]
    files: list[File] = []
    holes: list[Hole] = []
    ptr = 0
    id = 0
    current_block_is_file = True
    for size in map:
        if current_block_is_file:
            files.append((id, [i for i in range(ptr, ptr + size)]))
            id += 1
        else:
            if size != 0:
                holes.append([i for i in range(ptr, ptr + size)])
        ptr += size
        current_block_is_file = not current_block_is_file
    return files, holes


def compact_with_fragmentation(map: DiskMap) -> list[File]:
    files, holes = map
    free_spaces = collections.deque([e for hole in holes for e in hole])
    for file in reversed(files):
        while True:
            first_hole = free_spaces.popleft()
            last_block = file[1].pop()
            if first_hole < last_block:
                # The list of holes is initally sorted by construction, we can
                # bisect insort the new hole in its correct location
                bisect.insort(free_spaces, last_block)
                file[1].insert(0, first_hole)
            else:
                # We cannot compress the array more, stop here
                free_spaces.appendleft(first_hole)
                file[1].append(last_block)
                break
    return files


def compact_without_fragmentation(map: DiskMap) -> DiskMap:
    files, holes = map
    for file in reversed(files):
        # Iterate over each hole, starting from the leftmost one
        for i, hole in enumerate(holes):
            # If the hole is to the right the file, stop here for this file
            if hole[0] > file[1][0]:
                break
            # If the hole is large enough to fit the file...
            if (len(hole)) >= len(file[1]):
                # ...create a new hole where the file was
                # But actually no, because we won't be using this space anymore
                # Because we only try to move the files once, and right to left
                # new_hole = file[1]
                # Note: this would be incorrect, because the hole would not be
                # at the correct location
                # holes.append(new_hole)

                # ...move the file
                for j in range(len(file[1])):
                    file[1][j] = hole[j]

                # ...(partially) fill the hole
                if len(hole) == len(file[1]):
                    holes.pop(i)
                else:
                    shrunk_hole = hole[len(file[1]) :]
                    holes[i] = shrunk_hole

                # ...and stop here for this file
                break
            else:
                # Move on to the next hole
                pass

    return files, holes


def hash_files(files: list[File]) -> int:
    hash = 0
    for file in files:
        for block in file[1]:
            hash += block * file[0]
    return hash


def part1(input: str) -> int:
    map = parse_input(input)
    files = compact_with_fragmentation(map)
    hash = hash_files(files)
    return hash


def part2(input: str) -> int:
    map = parse_input(input)
    files, _ = compact_without_fragmentation(map)
    hash = hash_files(files)
    return hash


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
        input_text = (
            Path(__file__).parent.parent / "inputs" / "2024" / "day09.txt"
        ).read_text()

    assert part1(EXAMPLE_INPUT) == 1928
    result1 = part1(input_text)
    print(result1)

    assert part2(EXAMPLE_INPUT) == 2858
    result2 = part2(input_text)
    print(result2)
