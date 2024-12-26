from functools import reduce
from pathlib import Path
import sys

EXAMPLE_INPUT = """
kh-tc
qp-kh
de-cg
ka-co
yn-aq
qp-ub
cg-tb
vc-aq
tb-ka
wh-tc
yn-cg
kh-ub
ta-co
de-co
tc-td
tb-wq
wh-td
ta-ka
td-qp
aq-cg
wq-ub
ub-vc
de-ta
wq-aq
wq-vc
wh-yn
ka-de
kh-ta
co-tc
wh-qp
tb-vc
td-yn
"""


type Hostname = str
type Network = dict[Hostname, set[Hostname]]


def parse_input(input: str) -> Network:
    lines = input.strip().split("\n")
    network: Network = {}
    for line in lines:
        host1, host2 = line.split("-")
        if host1 not in network:
            network[host1] = set()
        if host2 not in network:
            network[host2] = set()
        network[host1].add(host2)
        network[host2].add(host1)
    return network


def triplet_to_str(triplet: tuple[Hostname, Hostname, Hostname]) -> str:
    hash = "".join(sorted(triplet))
    return hash


def find_all_cliques(network: Network) -> list[set[Hostname]]:
    cliques: list[set[Hostname]] = []
    unlinked_nodes = set(network.keys())
    while len(unlinked_nodes) != 0:
        clique: set[Hostname] = set()
        node = unlinked_nodes.pop()
        clique.add(node)
        while True:
            # Get the list of nodes not already explored, and linked to all nodes
            # of the clique currently being built
            potential_clique_members = (
                reduce(
                    lambda reduced, other: reduced & other,
                    [network[host] for host in clique],
                )
                & unlinked_nodes
            )
            if len(potential_clique_members) == 0:
                # We have a fully formed clique
                break
            new_clique_member = potential_clique_members.pop()
            unlinked_nodes.remove(new_clique_member)
            clique.add(new_clique_member)
        cliques.append(clique)

    return cliques


def part1(input: str) -> int:
    network = parse_input(input)
    # Each triplet is represented as a concatenation of the hostnames, after
    # sorting them alphabetically
    triplets: set[str] = set()

    for host, connected_hosts in network.items():
        # Let's not care about computers that do not start with the letter t
        if host[0] != "t":
            continue

        for second_host in connected_hosts:
            triplet_members = connected_hosts.intersection(network[second_host])
            for triplet_member in triplet_members:
                triplet_id = triplet_to_str((host, second_host, triplet_member))
                triplets.add(triplet_id)

    count = len(triplets)
    return count


def part2(input: str) -> str:
    network = parse_input(input)
    cliques = find_all_cliques(network)
    max_clique = max(cliques, key=lambda clique: len(clique))
    password = ",".join(sorted(max_clique))
    return password


"""
Benchmark 1: ./venv/bin/python src/day23.py /var/folders/fm/891_8yt158b05hy09ypkjyt40000gn/T/.sops1188168711/tmp-file1330927531
    Time (mean ± σ):      55.8 ms ±   2.9 ms    [User: 43.2 ms, System: 9.3 ms]
    Range (min … max):    48.5 ms …  62.5 ms    48 runs
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (
            Path(__file__).parent.parent / "inputs" / "2024" / "day23.txt"
        ).read_text()

    assert part1(EXAMPLE_INPUT) == 7
    result1 = part1(input_text)
    print(result1)

    assert part2(EXAMPLE_INPUT) == "co,de,ka,ta"
    result2 = part2(input_text)
    print(result2)
