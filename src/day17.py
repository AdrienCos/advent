import enum
from pathlib import Path
import re
import sys


EXAMPLE_INPUT = """
Register A: 729
Register B: 0
Register C: 0

Program: 0,1,5,4,3,0
"""

# Example of quine
EXAMPLE_INPUT_2 = """
Register A: 117440
Register B: 0
Register C: 0

Program: 0,3,5,4,3,0
"""


class ReservedError(Exception):
    pass


class InvalidOpCode(Exception):
    pass


class OpCode(enum.Enum):
    ADV = 0
    BXL = 1
    BST = 2
    JNZ = 3
    BXC = 4
    OUT = 5
    BDV = 6
    CDV = 7


OPCODES = [
    OpCode.ADV,
    OpCode.BXL,
    OpCode.BST,
    OpCode.JNZ,
    OpCode.BXC,
    OpCode.OUT,
    OpCode.BDV,
    OpCode.CDV,
]


class CPU:
    a: int
    b: int
    c: int
    pc: int
    instr_size: int
    instr: list[int]
    out: list[int]

    def __init__(self, A: int, B: int, C: int, instructions: list[int]) -> None:
        self.a = A
        self.b = B
        self.c = C
        self.pc = 0
        self.instr = instructions
        self.instr_size = len(instructions)
        self.out = []

    def run(self) -> list[int]:
        while self.pc < self.instr_size:
            self.cycle()
        return self.out

    def cycle(self) -> None:
        instr, operand = self.fetch()
        opcode = self.decode_opcode(instr)
        operand_value = self.decode_operand(opcode, operand)
        self.execute(opcode, operand_value)

    def fetch(self) -> tuple[int, int]:
        instr, operand = self.instr[self.pc : self.pc + 2]
        self.pc += 2
        return (instr, operand)

    @staticmethod
    def decode_opcode(instr: int) -> OpCode:
        return OPCODES[instr]

    def decode_operand(self, opcode: OpCode, operand: int) -> int:
        if opcode not in [OpCode.ADV, OpCode.BST, OpCode.OUT, OpCode.CDV, OpCode.BDV]:
            return operand

        if operand <= 3:
            return operand
        elif operand == 4:
            return self.a
        elif operand == 5:
            return self.b
        elif operand == 6:
            return self.c
        else:
            raise ReservedError("Combo operand 7 is reserved")

    def execute(self, opcode: OpCode, operand: int) -> None:
        if opcode == OpCode.ADV:
            numerator = self.a
            denominator = 2**operand
            result = int(numerator / denominator)
            self.a = result
        elif opcode == OpCode.BDV:
            numerator = self.a
            denominator = 2**operand
            result = int(numerator / denominator)
            self.b = result
        elif opcode == OpCode.CDV:
            numerator = self.a
            denominator = 2**operand
            result = int(numerator / denominator)
            self.c = result
        elif opcode == OpCode.BXL:
            result = self.b ^ operand
            self.b = result
        elif opcode == OpCode.BXC:
            # Operand is ignored
            result = self.b ^ self.c
            self.b = result
        elif opcode == OpCode.BST:
            # FIXME: maybe using a bitwise AND with 0b111 would be faster?
            result = operand % 8
            self.b = result
        elif opcode == OpCode.JNZ:
            if self.a != 0:
                self.pc = operand
        elif opcode == OpCode.OUT:
            # FIXME: maybe using a bitwise AND with 0b111 would be faster?
            result = operand % 8
            self.out.append(result)
        else:
            raise InvalidOpCode(f"Invalid opcode {opcode}")


def parse_input(input: str) -> CPU:
    lines = input.strip().split("\n")
    a = int(re.findall(r"\d+", lines[0])[0])
    b = int(re.findall(r"\d+", lines[1])[0])
    c = int(re.findall(r"\d+", lines[2])[0])
    instructions = [int(e) for e in re.findall(r"\d+", lines[4])]
    cpu = CPU(a, b, c, instructions)
    return cpu


def part1(input: str) -> str:
    cpu = parse_input(input)
    result = cpu.run()
    return ",".join([str(e) for e in result])


def part2(input: str) -> int:
    cpu = parse_input(input)
    count = 0
    return count


"""
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (Path(__file__).parent.parent / "inputs" / "day17.txt").read_text()

    assert part1(EXAMPLE_INPUT) == "4,6,3,5,6,3,5,2,1,0"
    assert part1(EXAMPLE_INPUT_2) == "0,3,5,4,3,0"
    result1 = part1(input_text)
    print(result1)

    assert part2(EXAMPLE_INPUT) == -1
    result2 = part2(input_text)
    print(result2)
