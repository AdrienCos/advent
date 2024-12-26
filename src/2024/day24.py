from pathlib import Path
import re
import sys
from typing import Callable


EXAMPLE_INPUT = """
x00: 1
x01: 0
x02: 1
x03: 1
x04: 0
y00: 1
y01: 1
y02: 1
y03: 1
y04: 1

ntg XOR fgs -> mjb
y02 OR x01 -> tnw
kwq OR kpj -> z05
x00 OR x03 -> fst
tgd XOR rvg -> z01
vdt OR tnw -> bfw
bfw AND frj -> z10
ffh OR nrd -> bqk
y00 AND y03 -> djm
y03 OR y00 -> psh
bqk OR frj -> z08
tnw OR fst -> frj
gnj AND tgd -> z11
bfw XOR mjb -> z00
x03 OR x00 -> vdt
gnj AND wpb -> z02
x04 AND y00 -> kjc
djm OR pbm -> qhw
nrd AND vdt -> hwm
kjc AND fst -> rvg
y04 OR y02 -> fgs
y01 AND x02 -> pbm
ntg OR kjc -> kwq
psh XOR fgs -> tgd
qhw XOR tgd -> z09
pbm OR djm -> kpj
x03 XOR y03 -> ffh
x00 XOR y04 -> ntg
bfw OR bqk -> z06
nrd XOR fgs -> wpb
frj XOR qhw -> z04
bqk OR frj -> z07
y03 OR x01 -> nrd
hwm AND bqk -> z03
tgd XOR rvg -> z12
tnw OR pbm -> gnj
"""

TEST_INPUT_1 = """
x00: 1
x01: 1
x02: 1
y00: 0
y01: 1
y02: 0

x00 AND y00 -> z00
x01 XOR y01 -> z01
x02 OR y02 -> z02
"""

TEST_INPUT_2 = """
x00: 0
x01: 1
x02: 0
x03: 1
x04: 0
x05: 1
y00: 0
y01: 0
y02: 1
y03: 1
y04: 0
y05: 1

x00 AND y00 -> z05
x01 AND y01 -> z02
x02 AND y02 -> z01
x03 AND y03 -> z03
x04 AND y04 -> z04
x05 AND y05 -> z00
"""


class NoOperationFoundError(Exception):
    pass


def AND(a: int, b: int) -> int:
    return a & b


def XOR(a: int, b: int) -> int:
    return a ^ b


def OR(a: int, b: int) -> int:
    return a | b


type Gate = Callable[[int, int], int]
type Register = str

type RegisterBank = dict[Register, int | None]
type GateArray = dict[Register, tuple[Gate, Register, Register]]


def registers_to_int(registers: RegisterBank, register_id: str) -> int:
    relevant_registers = [e for e in registers.keys() if e.startswith(register_id)]
    sum = 0
    for register in sorted(relevant_registers, reverse=True):
        sum = sum << 1
        reg_val = registers[register]
        if reg_val is None:
            raise ValueError
        sum += reg_val
    return sum


def parse_input(input: str) -> tuple[RegisterBank, GateArray]:
    registers_str, gates_str = input.strip().split("\n\n")

    registers: RegisterBank = {}
    gates: GateArray = {}
    for gate_str in gates_str.strip().split("\n"):
        reg_in_1, reg_in_2, reg_out = re.findall(r"[a-z0-9]{3}", gate_str)
        if "AND" in gate_str:
            operation = AND
        elif "XOR" in gate_str:
            operation = XOR
        elif "OR" in gate_str:
            operation = OR
        else:
            raise NoOperationFoundError
        gates[reg_out] = (operation, reg_in_1, reg_in_2)
        registers[reg_out] = None

    for register_str in registers_str.strip().split("\n"):
        id, value_str = register_str.split(": ")
        registers[id] = int(value_str)

    return registers, gates


def get_register_value(
    register: Register, registers: RegisterBank, gates: GateArray
) -> int:
    reg_value = registers.get(register, None)
    if reg_value is not None:
        return reg_value

    operation, reg_1, reg_2 = gates[register]
    reg_1_value = get_register_value(reg_1, registers, gates)
    reg_2_value = get_register_value(reg_2, registers, gates)
    reg_value = operation(reg_1_value, reg_2_value)
    registers[register] = reg_value
    return reg_value


def is_output_register(register: Register) -> bool:
    return register.startswith("z")


def register_bit_number(register: Register) -> int | None:
    try:
        value = int(register[1:])
        return value
    except ValueError:
        return None


# Returns a copy of the gate array with the provided output registers swapped
def swap_gates_outputs(
    output_1: Register,
    output_2: Register,
    gates: GateArray,
) -> GateArray:
    new_gates = gates.copy()

    tmp_gate = new_gates[output_1]
    new_gates[output_1] = new_gates[output_2]
    new_gates[output_2] = tmp_gate
    return new_gates


def find_gate_output(
    gates: GateArray,
    a: Register,
    b: Register,
    op: Gate,
) -> Register | None:
    for output, gate in gates.items():
        if gate[0] != op:
            continue
        if sorted([a, b]) == sorted(gate[1:]):
            return output


def find_gate_second_input(
    gates: GateArray,
    input: Register,
    output: Register,
    op: Gate,
) -> Register | None:
    for out, gate in gates.items():
        if gate[0] != op:
            continue
        if output != out:
            continue
        if input == gate[1]:
            return gate[2]
        if input == gate[2]:
            return gate[1]


def find_potential_gates(
    gates: GateArray,
    input: Register,
    op: Gate,
) -> list[Register]:
    partial_matches: list[Register] = []

    for out, gate in gates.items():
        if gate[0] != op:
            continue
        if input not in gate[1:]:
            continue
        partial_matches.append(out)

    return partial_matches


# Returns a list of suggested swaps that could improve the array, and a set of
# registers not linked to any valid-ish gate during the analysis
def analyze(
    registers: RegisterBank,
    gates: GateArray,
) -> tuple[list[tuple[Register, Register]], set[Register]]:
    nb_bits = len([e for e in registers if e.startswith("x")])
    # List of register pairs that should be swapped. If a single invalid register
    # is found, the second one is set to ''
    potential_swaps: list[tuple[Register, Register]] = []
    # Dict that maps bit number to their corresponding adder output carry register
    carry_registers: dict[int, Register] = {}
    # Set of all registers linked to a valid gate at some point
    seen_registers: set[Register | None] = set(["x00", "y00"])

    # First bit case
    x00_xor_y00 = find_gate_output(gates, "x00", "y00", XOR)
    x00_and_y00 = find_gate_output(gates, "x00", "y00", AND)
    seen_registers.add(x00_and_y00)
    seen_registers.add(x00_xor_y00)
    if x00_and_y00 is not None and not is_output_register(x00_and_y00):
        carry_registers[0] = x00_and_y00

    for i in range(1, nb_bits):
        x_label = f"x{i:02d}"
        y_label = f"y{i:02d}"
        input_carry_register = carry_registers.get(i - 1, None)
        seen_registers.add(x_label)
        seen_registers.add(y_label)

        # Find output of Xi^Yi gate
        x_xor_y = find_gate_output(gates, x_label, y_label, XOR)
        seen_registers.add(x_xor_y)
        if x_xor_y is not None and is_output_register(x_xor_y):
            potential_swaps.append((x_xor_y, ""))

        # Find output of Xi.Yi gate
        x_and_y = find_gate_output(gates, x_label, y_label, AND)
        seen_registers.add(x_and_y)
        if x_and_y is not None and is_output_register(x_and_y):
            potential_swaps.append((x_and_y, ""))

        # Check if the Xi^Yi and Xi.Yi have been swapped
        # One way to check if is Xi^Yi is used in an OR operation
        if (
            x_xor_y is not None
            and x_and_y is not None
            and len(find_potential_gates(gates, x_xor_y, OR)) != 0
        ):
            potential_swaps.append((x_xor_y, x_and_y))

        # Try to reverse-engineer the Cin register from Zi and Xi^Yi
        if input_carry_register is None and x_xor_y is not None:
            potential_input_carry = find_gate_second_input(
                gates, x_xor_y, f"z{i:02d}", XOR
            )
            if potential_input_carry is not None and not is_output_register(
                potential_input_carry
            ):
                input_carry_register = potential_input_carry
                seen_registers.add(input_carry_register)

        # Find X^Y^Cin = Z gate
        if input_carry_register is not None and x_xor_y is not None:
            xy_xor_c = find_gate_output(gates, x_xor_y, input_carry_register, XOR)
            seen_registers.add(xy_xor_c)
            if xy_xor_c is not None and (
                not is_output_register(xy_xor_c) or register_bit_number(xy_xor_c) != i
            ):
                potential_swaps.append((xy_xor_c, f"z{i:02d}"))
        else:
            pass

        # Find Cin.(X^Y)
        if input_carry_register is not None and x_xor_y is not None:
            xy_and_c = find_gate_output(gates, x_xor_y, input_carry_register, AND)
            seen_registers.add(xy_and_c)
            if xy_and_c is not None and not is_output_register(xy_and_c):
                # Find (X.Y) + Cin.(X^Y) = Cout
                if x_and_y is not None:
                    output_carry_register = find_gate_output(
                        gates, x_and_y, xy_and_c, OR
                    )
                    _ = seen_registers.add(output_carry_register)
                    if output_carry_register is None:
                        continue
                    if is_output_register(output_carry_register) and i != 44:
                        potential_swaps.append((output_carry_register, ""))
                    elif not is_output_register(output_carry_register) and i == 44:
                        print(
                            f"Invalid Cout gate output for bit {i:02d}: {output_carry_register}"
                        )
                        potential_swaps.append((output_carry_register, ""))
                    else:
                        carry_registers[i] = output_carry_register

    unseen_registers = set(registers.keys()) - seen_registers
    return potential_swaps, unseen_registers


def part1(input: str) -> int:
    registers, gates = parse_input(input)
    # List of output registers
    targets = [e for e in registers.keys() if e.startswith("z")]
    for target in targets:
        target_value = get_register_value(target, registers, gates)
        registers[target] = target_value
    sum = registers_to_int(registers, "z")
    return sum


def part2(input: str) -> str:
    registers, gates = parse_input(input)
    invalid_regs, _ = analyze(registers, gates)

    swaps_done: set[tuple[Register, Register]] = set()
    swaps = [e for e in invalid_regs if e[0] != "" and e[1] != ""]
    while swaps != []:
        pair = swaps.pop()
        if pair[0] == "" or pair[1] == "":
            continue
        if pair in swaps_done:
            continue
        swaps_done.add(pair)
        gates = swap_gates_outputs(pair[0], pair[1], gates)
        new_invalid_regs, _ = analyze(registers, gates)
        new_swaps = [e for e in new_invalid_regs if e[0] != "" and e[1] != ""]
        swaps += new_swaps

    swapped_regs_list = [e for tup in swaps_done for e in tup]
    output = ",".join(sorted(swapped_regs_list))
    return output


"""
Benchmark 1: ./venv/bin/python src/day24.py /var/folders/fm/891_8yt158b05hy09ypkjyt40000gn/T/.sops45296776/tmp-file65667850
    Time (mean ± σ):      87.6 ms ±   6.6 ms    [User: 73.1 ms, System: 10.9 ms]
    Range (min … max):    78.9 ms … 103.3 ms    31 runs
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (
            Path(__file__).parent.parent / "inputs" / "2024" / "day24.txt"
        ).read_text()

    assert part1(TEST_INPUT_1) == 4
    assert part1(EXAMPLE_INPUT) == 2024
    result1 = part1(input_text)
    print(result1)

    result2 = part2(input_text)
    print(result2)
