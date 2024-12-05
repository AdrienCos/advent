from pathlib import Path

EXAMPLE_INPUT = """
47|53
97|13
97|61
97|47
75|29
61|13
75|53
29|13
97|29
53|29
61|53
97|53
61|29
47|13
75|47
97|75
47|61
75|61
47|29
75|13
53|13

75,47,61,53,29
97,61,53,29,13
75,29,13
75,97,47,61,53
61,13,29
97,13,75,29,47
"""

INPUT_PATH = Path(__file__).parent.parent / "inputs" / "day05.txt"

type Rule = tuple[int, int]
type Update = list[int]

def parse_input(input: str) -> tuple[list[Rule], list[Update]]:
    raw_rules, raw_updates = input.strip().split("\n\n")
    rules: list[Rule] = []
    for line in raw_rules.split("\n"):
        split_rules = (line.split("|"))
        before_rule = int(split_rules[0])
        after_rule = int(split_rules[1])
        rule = (before_rule, after_rule)
        rules.append(rule)
    updates: list[Update] = []
    for line in raw_updates.split("\n"):
        updates.append(list(map(int, line.split(","))))
    return (rules,updates)

def recursive_build(values: set[int], rules: list[Rule]) -> tuple[list[int], set[int]]:
    if len(values) == 0:
        return (list(values), values)
    pivot = values.pop()
    before: set[int] = set()
    after: set[int] = set()
    for value in values:
        if (pivot, value) in rules:
            after.add(value)
        else:
            before.add(value)
    values.difference_update(before)
    values.difference_update(after)
    before_order, before_unused = recursive_build(before, rules)
    after_order, after_unused = recursive_build(after, rules)
    return (before_order + [pivot] + after_order, before_unused.union(after_unused))


def build_ruleset(rules: list[Rule]) -> list[int]:
    # Note: the input respects the following constraints:
    # - each rule is unique
    # - every value present in an update is part of at least one rule
    # - every value is present 1/3 of the rules as part of the before value
    # - every value is present 1/3 of the rules as part of the after value
    # The entire ruleset is a cyclical graph that connects each value to the one
    # just after it. This function builds this ruleset as a list, and one must
    # imagine that the last value is connected to the first one, because I am
    # too lazy to implement a circular list.
    values = set([rule[0] for rule in rules] + [rule[1] for rule in rules])
    ruleset, _ = recursive_build(values, rules)
    return ruleset

def build_filtered_ruleset(rules: list[Rule], update: Update) -> list[int]:
    # For Part 2 only, this will build a ruleset using only the rules where both
    # values are present in the given update.
    filtered_rules: list[Rule] = []
    for rule in rules:
        if rule[0] in update and rule[1] in update:
            filtered_rules.append(rule)
    return build_ruleset(filtered_rules)

def get_correct_and_incorrect_updates(ruleset: list[int], updates: list[Update]) -> tuple[list[Update], list[Update]]:
    correct_updates: list[Update] = []
    incorrect_updates: list[Update] = []
    for update in updates:
        head_index = ruleset.index(update[0])
        new_ruleset = ruleset[head_index:] + ruleset[:head_index]
        filtered_ruleset = [value for value in new_ruleset if value in update]
        if filtered_ruleset == update:
            correct_updates.append(update)
        else:
            incorrect_updates.append(update)
    return (correct_updates, incorrect_updates)


def part1(input: str) -> int:
    rules, updates = parse_input(input)
    ruleset = build_ruleset(rules)
    count = 0
    correct_updates, _ = get_correct_and_incorrect_updates(ruleset, updates)
    for update in correct_updates:
        count += update[int(len(update)/2)]
    return count


def part2(input: str) -> int:
    rules, updates = parse_input(input)
    ruleset = build_ruleset(rules)
    count = 0
    _, incorrect_updates = get_correct_and_incorrect_updates(ruleset, updates)
    for update in incorrect_updates:
        filtered_ruleset = build_filtered_ruleset(rules, update)
        corrected_update = [value for value in filtered_ruleset if value in update]
        count += corrected_update[int(len(corrected_update)/2)]
    return count


"""
Benchmark 1 (79 runs): python src/day05.py
    measurement          mean ± σ            min … max           outliers
    wall_time          63.6ms ± 4.56ms    59.1ms … 80.5ms          4 ( 5%)
    peak_rss           13.0MB ±  120KB    12.7MB … 13.2MB          1 ( 1%)
    cpu_cycles          208M  ± 8.44M      173M  …  227M           6 ( 8%)
    instructions        620M  ± 12.2M      561M  …  627M           6 ( 8%)
    cache_references   1.10M  ± 93.3K      709K  … 1.27M           1 ( 1%)
    cache_misses        253K  ± 50.3K      148K  …  396K           0 ( 0%)
    branch_misses       901K  ± 80.0K      491K  …  960K           9 (11%)
"""
if __name__ == "__main__":
    assert part1(EXAMPLE_INPUT) == 143
    result1 = part1(INPUT_PATH.read_text())
    print(result1)

    assert part2(EXAMPLE_INPUT) == 123
    result2 = part2(INPUT_PATH.read_text())
    print(result2)
