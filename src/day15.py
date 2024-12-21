from pathlib import Path
import sys


EXAMPLE_INPUT = """
##########
#..O..O.O#
#......O.#
#.OO..O.O#
#..O@..O.#
#O#..O...#
#O..O..O.#
#.OO.O.OO#
#....O...#
##########

<vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
<<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
>^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
<><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
"""

TEST_INPUT_1 = """
########
#..O.O.#
##@.O..#
#...O..#
#.#.O..#
#...O..#
#......#
########

<^^>>>vv<v>>v<<
"""

TEST_INPUT_2 = """
#######
#...#.#
#.....#
#..OO@#
#..O..#
#.....#
#######

<vv<<^^<<^^
"""

type Map = list[list[str]]
type Coords = tuple[int, int]
type Movements = list[Coords]

ROBOT = "@"
BOX = "O"
WALL = "#"
FLOOR = "."
BOX_LEFT_HALF = "["
BOX_RIGHT_HALF = "]"
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)


class InvalidDirectionError(Exception):
    pass


class UnexpectedOOBError(Exception):
    pass


class InvalidCellError(Exception):
    pass


def arrow_to_direction(arrow: str) -> Coords | None:
    if arrow == "^":
        return (-1, 0)
    elif arrow == ">":
        return (0, 1)
    elif arrow == "<":
        return (0, -1)
    elif arrow == "v":
        return (1, 0)
    elif arrow == "\n":
        return None
    else:
        raise InvalidDirectionError(arrow)


def direction_to_arrow(direction: Coords | None) -> str:
    if direction == (0, 1):
        return ">"
    if direction == (0, -1):
        return "<"
    if direction == (1, 0):
        return "v"
    if direction == (-1, 0):
        return "^"
    if direction is None:
        return ""
    raise InvalidDirectionError


def move(pos: Coords, movement: Coords) -> Coords:
    return (pos[0] + movement[0], pos[1] + movement[1])


def gps(pos: Coords) -> int:
    return pos[0] * 100 + pos[1]


class Warehouse:
    _map: Map
    robot: Coords
    movements: Movements
    movement_idx: int
    movement_len: int
    height: int
    width: int
    last_move: Coords | None

    def __init__(self, map: Map, robot: Coords, movements: Movements) -> None:
        self._map = map
        self.height = len(map)
        self.width = len(map[0])
        self.robot = robot
        self.movements = movements
        self.movement_len = len(movements)
        self.movement_idx = 0
        self.last_move = None

    def __str__(self) -> str:
        map = (
            f"{self.movement_idx}: {direction_to_arrow(self.last_move)}\n"
            + "\n".join("".join(line) for line in self._map)
            + "\n"
        )
        return map

    @staticmethod
    def widen(warehouse: "Warehouse") -> "Warehouse":
        new_robot = (warehouse.robot[0], warehouse.robot[1] * 2)
        new_map: Map = []
        for line in warehouse._map:
            new_line: list[str] = []
            for cell in line:
                if cell == BOX:
                    new_line.append(BOX_LEFT_HALF)
                    new_line.append(BOX_RIGHT_HALF)
                elif cell == WALL:
                    new_line.append(WALL)
                    new_line.append(WALL)
                elif cell == ROBOT:
                    new_line.append(ROBOT)
                    new_line.append(FLOOR)
                elif cell == FLOOR:
                    new_line.append(FLOOR)
                    new_line.append(FLOOR)
                else:
                    raise InvalidCellError
            new_map.append(new_line)

        return Warehouse(map=new_map, robot=new_robot, movements=warehouse.movements)

    def map(self, pos: Coords) -> str:
        return self._map[pos[0]][pos[1]]

    def set_map(self, pos: Coords, value: str) -> None:
        self._map[pos[0]][pos[1]] = value

    def is_oob(self, cell: Coords) -> bool:
        if (
            cell[0] < 0
            or cell[0] >= self.height
            or cell[1] < 0
            or cell[1] >= self.width
        ):
            return True
        return False

    def pop_movement(self) -> Coords:
        movement = self.movements[self.movement_idx]
        self.movement_idx += 1
        self.last_move = movement
        return movement

    # Returns False if there were no more movements to perform
    def execute_movement(self) -> bool:
        # Out of moves to do
        if self.movement_idx >= self.movement_len:
            return False

        # Get the current movement direction
        direction = self.pop_movement()

        # Create cursor that will move in this direction from the robot's position
        cursor = self.robot

        # Move the cursor until it hits either a floor tile or a wall
        while True:
            cursor = move(cursor, direction)
            if self.map(cursor) == WALL:
                # Move cannot be done, abort
                break

            if self.map(cursor) == FLOOR:
                # Move is doable, update the map accordingly
                # 1. A box is created in the floor spot
                self.set_map(cursor, BOX)
                # 2. A floor spot is created where the robot was
                self.set_map(self.robot, FLOOR)
                # 3. The robot is moved to its adjacent cell
                new_robot_pos = move(self.robot, direction)
                self.set_map(new_robot_pos, ROBOT)
                # 4. Update the robot's position
                self.robot = new_robot_pos
                # Note: remove this break to keep moving until we hit a wall
                break
        return True

    def _push_horizontal_wide(self, cursor: Coords, direction: Coords) -> None:
        # 1. Rewrite all the spaces between cursor and next robot pos with wide boxes
        while cursor != move(self.robot, direction):
            if direction == LEFT:
                self.set_map(cursor, BOX_LEFT_HALF)
                cursor = move(cursor, RIGHT)
                self.set_map(cursor, BOX_RIGHT_HALF)
                cursor = move(cursor, RIGHT)
            else:
                self.set_map(cursor, BOX_RIGHT_HALF)
                cursor = move(cursor, LEFT)
                self.set_map(cursor, BOX_LEFT_HALF)
                cursor = move(cursor, LEFT)
        # 2. A floor spot is created where the robot was
        self.set_map(self.robot, FLOOR)
        # 3. The robot is moved to its adjacent cell
        new_robot_pos = move(self.robot, direction)
        self.set_map(new_robot_pos, ROBOT)
        # 4. Update the robot's position
        self.robot = new_robot_pos

    def _can_push_vertical_wide(
        self, cursor: Coords, direction: Coords
    ) -> tuple[bool, set[Coords]]:
        """Returns True if the given `cursor` can be pushed in given vertical direction"""

        if self.map(cursor) == FLOOR:
            return (True, set())
        if self.map(cursor) == WALL:
            return (False, set())
        if self.map(cursor) == ROBOT:
            return self._can_push_vertical_wide(move(cursor, direction), direction)
        if self.map(cursor) == BOX_LEFT_HALF:
            next_cursor_1 = move(cursor, direction)
            next_cursor_2 = move(next_cursor_1, RIGHT)
            left_result = self._can_push_vertical_wide(next_cursor_1, direction)
            right_result = self._can_push_vertical_wide(next_cursor_2, direction)
            if not left_result[0] or not right_result[0]:
                return (False, set())
            new_set = left_result[1] | right_result[1] | {cursor}
            return (True, new_set)
        if self.map(cursor) == BOX_RIGHT_HALF:
            next_cursor_1 = move(cursor, direction)
            next_cursor_2 = move(next_cursor_1, LEFT)
            right_result = self._can_push_vertical_wide(next_cursor_1, direction)
            left_result = self._can_push_vertical_wide(next_cursor_2, direction)
            if not left_result[0] or not right_result[0]:
                return (False, set())
            new_set = left_result[1] | right_result[1] | {move(cursor, LEFT)}
            return (True, new_set)

        raise InvalidCellError

    def _push_vertical_wide(
        self, cubes_to_push: set[Coords], direction: Coords
    ) -> None:
        """Writes the given value to the cursor after propagating the change down
        the impacted cells."""
        # 1. Move the cubes, starting with the last ones
        sorted_cubes: list[Coords] = []
        if direction == UP:
            sorted_cubes = sorted(list(cubes_to_push), key=lambda coords: coords[0])
        else:
            sorted_cubes = sorted(list(cubes_to_push), key=lambda coords: -coords[0])

        for cube in sorted_cubes:
            self.set_map(move(cube, direction), BOX_LEFT_HALF)
            self.set_map(move(move(cube, direction), RIGHT), BOX_RIGHT_HALF)
            self.set_map(cube, FLOOR)
            self.set_map(move(cube, RIGHT), FLOOR)

        # 2. Move the robot
        self.set_map(move(self.robot, direction), ROBOT)
        self.set_map(self.robot, FLOOR)
        self.robot = move(self.robot, direction)

    # Returns False if there were no more movements to perform
    def execute_movement_wide(self) -> bool:
        # Out of moves to do
        if self.movement_idx >= self.movement_len:
            return False

        # Get the current movement direction
        direction = self.pop_movement()

        # Create cursor that will move in this direction from the robot's position
        cursor = self.robot

        # Horizontal move, easy case
        if direction[0] == 0:
            # Move the cursor until it hits either a floor tile or a wall
            while True:
                cursor = move(cursor, direction)
                if self.map(cursor) == WALL:
                    # Move cannot be done, abort
                    break

                if self.map(cursor) == FLOOR:
                    # Move is doable, update the map accordingly
                    self._push_horizontal_wide(cursor, direction)
                    # Note: remove this break to keep moving until we hit a wall
                    break
        else:
            # Vertical move, hard case
            can_push, cubes_to_push = self._can_push_vertical_wide(cursor, direction)
            if can_push:
                # Actually perform the push now
                self._push_vertical_wide(cubes_to_push, direction)
        return True

    def score(self) -> int:
        total = 0
        for line_idx in range(self.height):
            for col_idx in range(self.width):
                if self.map((line_idx, col_idx)) == BOX:
                    total += gps((line_idx, col_idx))
                elif self.map((line_idx, col_idx)) == BOX_LEFT_HALF:
                    total += gps((line_idx, col_idx))

        return total


def parse_input(input: str) -> Warehouse:
    map_str, movements_str = input.strip().split("\n\n")
    map: Map = []
    robot_pos: Coords = (-1, -1)
    for line_idx, line in enumerate(map_str.strip().split("\n")):
        cells = [e for e in line]
        if ROBOT in cells:
            robot_pos = (line_idx, cells.index(ROBOT))
        map.append(cells)

    movements: Movements = []
    for arrow in movements_str:
        direction = arrow_to_direction(arrow)
        if direction is None:
            continue
        movements.append(direction)

    warehouse = Warehouse(map=map, robot=robot_pos, movements=movements)
    return warehouse


def part1(input: str) -> int:
    count = 0
    warehouse = parse_input(input)
    while warehouse.execute_movement():
        pass
    count = warehouse.score()
    return count


def part2(input: str) -> int:
    count = 0
    warehouse = parse_input(input)
    wide_warehouse = Warehouse.widen(warehouse)
    while wide_warehouse.execute_movement_wide():
        pass
    count = wide_warehouse.score()
    return count


"""
Benchmark 1: ./venv/bin/python src/day15.py /var/folders/fm/891_8yt158b05hy09ypkjyt40000gn/T/.sops2761808855/tmp-file576825842
    Time (mean ± σ):     125.7 ms ±  10.2 ms    [User: 107.8 ms, System: 12.2 ms]
    Range (min … max):   110.5 ms … 148.4 ms    22 runs
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (Path(__file__).parent.parent / "inputs" / "day15.txt").read_text()

    assert part1(TEST_INPUT_1) == 2028
    assert part1(EXAMPLE_INPUT) == 10092
    result1 = part1(input_text)
    print(result1)

    assert part2(EXAMPLE_INPUT) == 9021
    assert part2(TEST_INPUT_2) == 105 + 207 + 306
    result2 = part2(input_text)
    print(result2)
