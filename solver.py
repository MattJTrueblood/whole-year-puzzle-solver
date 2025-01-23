import time
import random
import argparse

BOARD_MASK = [
            [1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 0, 0]
            ]

BOARD_VALUES = [
            ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", ""],
            ["JUL", "AUG", "SEP", "OCT", "NOV", "DEC", ""],
            ["1", "2", "3", "4", "5", "6", "7"],
            ["8", "9", "10", "11", "12", "13", "14"],
            ["15", "16", "17", "18", "19", "20", "21"],
            ["22", "23", "24", "25", "26", "27", "28"],
            ["", "", "29", "30", "31", "", ""]
            ]


LONG_L_PIECE = [
            [1, 0],
            [1, 0],
            [1, 0],
            [1, 1]
            ]

SHORT_L_PIECE = [
            [1, 0],
            [1, 0],
            [1, 1]
            ]

PLUS_PIECE = [
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0]
            ]

S_PIECE = [
            [1, 1, 0],
            [0, 1, 1]
            ]

Z_PIECE = [
            [1, 1, 0],
            [0, 1, 0],
            [0, 1, 1]
]

P_PIECE = [
            [1, 1],
            [1, 1],
            [1, 0]
]

O_PIECE = [
            [1, 1],
            [1, 1]
]

U_PIECE = [
            [1, 0, 1],
            [1, 1, 1]
]

T_PIECE = [
            [0, 1, 0],
            [1, 1, 1]
]

ALL_PIECES = [O_PIECE, PLUS_PIECE, Z_PIECE, U_PIECE, T_PIECE, P_PIECE, LONG_L_PIECE, S_PIECE, SHORT_L_PIECE]

COLORS = [
    "\033[31m",  # Red
    "\033[32m",  # Green
    "\033[33m",  # Yellow
    "\033[34m",  # Blue
    "\033[35m",  # Magenta
    "\033[36m",  # Cyan
    "\033[91m",  # Bright Red
    "\033[92m",  # Bright Green
    "\033[93m",  # Bright Yellow
]

DEFAULT_COLOR = "\033[0m"


########################


"""
Returns the reflected variation of a piece (e.g. what happens when you physically flip it over)
"""
def flip_piece(piece):
    return piece[::-1]


"""
Returns the 90-degrees rotated variation of a piece
"""
def rotate_piece(piece):
    return [list(row) for row in zip(*piece[::-1])]

"""
Takes a list of pieces and returns a list with all duplicate pieces removed
"""
def remove_duplicate_pieces(pieces):
    unique_pieces = []
    for piece in pieces:
        if not any(piece == unique for unique in unique_pieces):
            unique_pieces.append(piece)
    return unique_pieces


"""
Get all non-duplicate rotated and flipped variations of a piece
"""
def find_all_variations(piece):
    variations = []
    variations.append(piece)

    rotated_once = rotate_piece(piece)
    rotated_twice = rotate_piece(rotated_once)
    rotated_thrice = rotate_piece(rotated_twice)
    variations.extend([rotated_once, rotated_twice, rotated_thrice])

    flipped_piece = flip_piece(piece)
    flipped_rotated_once = rotate_piece(flipped_piece)
    flipped_rotated_twice = rotate_piece(flipped_rotated_once)
    flipped_rotated_thrice = rotate_piece(flipped_rotated_twice)
    variations.extend([flipped_piece, flipped_rotated_once, flipped_rotated_twice, flipped_rotated_thrice])

    return remove_duplicate_pieces(variations)


"""
Using a month and day (e.g. "Jan" and 12), returns the board mask with those tiles in the puzzle set to -2 (inacessible) or -1 (empty)
We reserve values 0 and above for the indices of pieces (to store the board state)
"""
def generate_puzzle_for_month_day(month, day):
    puzzle = []
    for board_row, mask_row in zip(BOARD_VALUES, BOARD_MASK):
        puzzle_row = []
        for val, mask_val in zip(board_row, mask_row):
            if mask_val == 0 or str(val) == str(month) or str(val) == str(day):
                puzzle_row.append(-2)
            else:
                puzzle_row.append(-1)
        puzzle.append(puzzle_row)
    return puzzle


def can_place_piece(piece, puzzle_state, row, col):
    for i, piece_row in enumerate(piece):
        for j, val in enumerate(piece_row):
            if val == 1:
                r, c = row + i, col + j
                if not (0 <= r < len(puzzle_state) and 0 <= c < len(puzzle_state[0])):
                    return False
                if puzzle_state[r][c] != -1:
                    return False
    return True


def place_piece(piece, puzzle_state, row, col, piece_index):
    for i, piece_row in enumerate(piece):
        for j, val in enumerate(piece_row):
            if val == 1:
                r, c = row + i, col + j
                puzzle_state[r][c] = piece_index


def find_solution_recursive(current_puzzle_state, all_pieces_variations, current_piece_index):
    # if all pieces are placed
    if current_piece_index >= len(all_pieces_variations):
        return current_puzzle_state

    for current_variation in all_pieces_variations[current_piece_index]:
        # Try every possible position
        for row in range(len(current_puzzle_state)):
            for col in range(len(current_puzzle_state[0])):
                if can_place_piece(current_variation, current_puzzle_state, row, col):
                    new_puzzle = [row[:] for row in current_puzzle_state]
                    place_piece(current_variation, new_puzzle, row, col, current_piece_index)
                    solution = find_solution_recursive(new_puzzle, all_pieces_variations, current_piece_index + 1)
                    if solution:
                        return solution
    return None



def print_board_state(state):
    for row in state:
        for cell in row:
            if cell == -2:
                print(" . ", end="")
            else:
                color = COLORS[cell % len(COLORS)]
                print(f"{color} {cell} {DEFAULT_COLOR}", end="")
        print()
    print()


"""
Using a puzzle (masked array of 0s and 1s) find a solution
"""
def find_solution(puzzle):
    all_pieces_variations = [find_all_variations(piece) for piece in ALL_PIECES]
    solution = find_solution_recursive(puzzle, all_pieces_variations, 0)
    print_board_state(solution)


"""
Finds solution for the puzzle given a month and a day
"""
def get_solution_for_month_day(month, day):
    puzzle = generate_puzzle_for_month_day(month, day)
    find_solution(puzzle)


def main():
    parser = argparse.ArgumentParser(description='solves the whole year puzzle')
    parser.add_argument('month', type=str, help='month (3 letter abbreviation all caps)')
    parser.add_argument('day', type=int, help='day (1-31)')

    args = parser.parse_args()

    print(f"finding solution for {args.month} {args.day}")

    random.shuffle(ALL_PIECES)
    start_time = time.time()
    get_solution_for_month_day(args.month, args.day)
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Elapsed time: {elapsed} seconds")
    return


if __name__ == "__main__":
    main()