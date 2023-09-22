import random
import copy

GAMEMODE_HARD = 60
GAMEMODE_MEDIUM = 50
GAMEMODE_EASY = 40

# Old functions
# _____________________________________________________________________

"""
Helper function that determines whether input board has a unique solution
"""


def has_unique_solution(board):
    results = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            results.append(count_solutions(board))
    for i in range(len(results)):
        for j in range(i+1, len(results)):
            if not compare_boards(results[i], results[j]):
                return False
    return True


"""
Function that checks whether two boards b1 and b2 are the same. If they are the 
same, returns true, else returns false. Requires b1 and b2 are both boards of the 
same size.
"""


def compare_boards(b1, b2):
    for i in range(len(test_board)):
        for j in range(len(test_board[0])):
            if b1[i][j] != b2[i][j]:
                return False
    return True


test_board = [
    [7, 8, 0, 4, 0, 0, 1, 2, 0],
    [6, 0, 0, 0, 7, 5, 0, 0, 9],
    [0, 0, 0, 6, 0, 1, 0, 7, 8],
    [0, 0, 7, 0, 4, 0, 2, 6, 0],
    [0, 0, 1, 0, 5, 0, 9, 3, 0],
    [9, 0, 4, 0, 6, 0, 0, 0, 5],
    [0, 7, 0, 3, 0, 0, 0, 1, 2],
    [1, 2, 0, 0, 0, 7, 4, 0, 0],
    [0, 4, 9, 2, 0, 6, 0, 0, 7]
]

# _____________________________________________________________________


"""
Generates a random 9 x 9 sudoku board that has at least 1 solution.
"""


def generate_board(GAME_MODE):
    # Initialize empty board with all 0s
    board = [[0 for i in range(9)]for i in range(9)]
    print("before")
    print_board(board)
    # Adds numbers 1-9 at random positions in the board
    for i in range(1, 10):
        x, y, = random.randint(0, 8), random.randint(0, 8)
        while board[x][y] != 0:
            x, y = random.randint(0, 8), random.randint(0, 8)
        board[x][y] = i
    print("after")
    print_board(board)
    print("______________")
    # Solve this board to generate a full sudoku board
    solve(board)
    print("after solving")
    print_board(board)
    print("______________")
    # Removes some number of numbers from board at random positions to generate
    # a new sudoku puzzle with the solution being the solved board from before
    for i in range(GAME_MODE):
        x, y = random.randint(0, 8), random.randint(0, 8)
        while board[x][y] == 0:
            x, y = random.randint(0, 8), random.randint(0, 8)
        board[x][y] = 0
    print("final board")
    print_board(board)
    return board


def generate_empty_board():
    return [[0 for i in range(9)]for i in range(9)]


def solve(bo):
    find = find_empty(bo)
    if not find:
        return True
    else:
        row, col = find
    for i in range(1, 10):
        if valid(bo, i, (row, col)):
            bo[row][col] = i
            if solve(bo):
                return True
            bo[row][col] = 0
    return False


def count_solutions(bo):
    board = copy.deepcopy(bo)
    find = find_empty(board)
    if not find:
        return 1
    count = 0
    row, col = find
    for i in range(1, 10):
        if valid(board, i, (row, col)):
            board[row][col] = i
            count += count_solutions(board)
            board[row][col] = 0
    return count


def valid(bo, num, pos):
    # Check row
    for i in range(len(bo[0])):
        if bo[pos[0]][i] == num and pos[1] != i:
            return False

    # Check column
    for i in range(len(bo)):
        if bo[i][pos[1]] == num and pos[0] != i:
            return False

    # Check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_y*3, box_y*3 + 3):
        for j in range(box_x * 3, box_x*3 + 3):
            if bo[i][j] == num and (i, j) != pos:
                return False
    return True


def print_board(bo):
    for i in range(len(bo)):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - - - - ")
        for j in range(len(bo[0])):
            if j % 3 == 0 and j != 0:
                print(" | ", end="")
            if j == 8:
                print(bo[i][j])
            else:
                print(str(bo[i][j]) + " ", end="")


def find_empty(bo):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j)  # row, col

    return None


x = generate_board(GAMEMODE_EASY)
print("using solve")
print("_______")
solve(x)
print_board(x)


"""
print_board(board)
solve(board)
print("___________________")
print_board(board)
"""
