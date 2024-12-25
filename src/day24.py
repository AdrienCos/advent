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


def int_to_registers(value: int, nb_bits: int, register_id: str) -> dict[Register, int]:
    registers: dict[Register, int] = {}
    for i in range(nb_bits):
        reg_name = f"{register_id}{i:02d}"
        reg_val = value & 1
        registers[reg_name] = reg_val
        value = value >> 1
    return registers


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


def test_gate_array(registers: RegisterBank, gates: GateArray) -> None:
    targets = [e for e in registers.keys() if e.startswith("z")]
    for i in range(45):
        x_val = 2**i
        x_regs = int_to_registers(x_val, 45, "x")
        for j in range(45):
            y_val = 2**j
            y_regs = int_to_registers(y_val, 45, "y")
            temp_regs = registers.copy()
            temp_regs |= x_regs
            temp_regs |= y_regs
            for target in targets:
                target_value = get_register_value(target, temp_regs, gates)
                registers[target] = target_value
            z_val = registers_to_int(temp_regs, "z")
            if z_val == x_val + y_val:
                print(z_val, i, j)


def get_input_bits_of_register(
    register: Register, gates: GateArray
) -> tuple[set[Register], set[Register], set[Register]]:
    x_registers: set[Register] = set()
    y_registers: set[Register] = set()
    all_inputs: set[Register] = set()
    to_explore = [register]
    while len(to_explore) != 0:
        reg = to_explore.pop()
        if reg.startswith("x"):
            x_registers.add(reg)
        elif reg.startswith("y"):
            y_registers.add(reg)
        all_inputs.add(reg)
        if reg in gates:
            _, reg_1, reg_2 = gates[reg]
            to_explore.append(reg_1)
            to_explore.append(reg_2)

    return (x_registers), (y_registers), all_inputs


def part1(input: str) -> int:
    registers, gates = parse_input(input)
    # List of output registers
    targets = [e for e in registers.keys() if e.startswith("z")]
    for target in targets:
        target_value = get_register_value(target, registers, gates)
        registers[target] = target_value
    sum = registers_to_int(registers, "z")
    return sum


def part2(input: str) -> int:
    registers, gates = parse_input(input)
    targets = [e for e in registers.keys() if e.startswith("z")]

    for target in targets:
        # for target in sorted(targets):
        x_input, y_input, all_inputs = get_input_bits_of_register(target, gates)

        print(f"""
For {target}: x={len(x_input)}, y={len(y_input)}
X: {sorted(list(x_input))}
Y: {sorted(list(y_input))}
All: {sorted(list(all_inputs))}
        """)

    count = 0
    return count


"""
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (Path(__file__).parent.parent / "inputs" / "day24.txt").read_text()

    assert part1(TEST_INPUT_1) == 4
    assert part1(EXAMPLE_INPUT) == 2024
    result1 = part1(input_text)
    print(result1)

    result2 = part2(input_text)
