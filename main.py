# Imports
import numpy as np
import random
import time
from time import sleep
from operator import itemgetter
from PIL import ImageGrab
import pyautogui
import keyboard

# Globals
GRID_WIDTH = 24
GRID_HEIGHT = 20
tiles = {
    "one": ([25, 118, 210], 1),
    "two": ([56, 142, 60], 2),
    "three": ([211, 47, 47], 3),
    "four": ([123, 31, 162], 4),
    "five": ([255, 143, 0], 5),
    "six": ([0, 151, 167], 6),
}
blanks = {
    "blank1": ([229, 194, 159], -1),
    "blank2": ([215, 184, 153], -1),
}

outputs = []
completed_tiles = []
click_list = []
guess = False
likelies_list = []


# Functions
def out_of_grid(x, y):
    if 980 <= x <= 1580 and 520 <= y <= 1020:
        return False
    return True


def update_board(img):
    for column in range(24):
        for row in range(20):
            pixels = []
            blank = True
            for i in range(25):
                if row * 25 + 13 < 500 and column * 25 + i < 600:
                    pixels.append(list(img[(row * 25) + 13, (column * 25) + i]))
            for key in tiles.keys():
                if tiles[key][0] in pixels:
                    blank = False
                    board[row][column] = tiles[key][1]
            if blank:
                for key in blanks.keys():
                    if blanks[key][0] in pixels:
                        board[row][column] = blanks[key][1]


def check_neighbors(y, x, likelies):
    global board, GRID_WIDTH, GRID_HEIGHT, completed_tiles, click_list, likelies_list
    output = 0
    neighbors = []
    if 0 < y < GRID_HEIGHT - 1:
        if x > 0:
            neighbors.append([board[y - 1][x - 1], board[y][x - 1], board[y + 1][x - 1]])
            neighbors.append([board[y - 1][x], 99, board[y + 1][x]])
        elif x == 0:
            neighbors.append([99, 99, 99])
            neighbors.append([board[y - 1][x], 99, board[y + 1][x]])
        if x < GRID_WIDTH - 1:
            neighbors.append([board[y - 1][x + 1], board[y][x + 1], board[y + 1][x + 1]])
        elif x == GRID_WIDTH - 1:
            neighbors.append([99, 99, 99])
    elif y == 0:
        if x > 0:
            neighbors.append([99, board[y][x - 1], board[y + 1][x - 1]])
            neighbors.append([99, 99, board[y + 1][x]])
        elif x == 0:
            neighbors.append([99, 99, 99])
            neighbors.append([99, 99, board[y + 1][x]])
        if x < GRID_WIDTH - 1:
            neighbors.append([99, board[y][x + 1], board[y + 1][x + 1]])
        elif x == GRID_WIDTH - 1:
            neighbors.append([99, 99, 99])
    elif y == GRID_HEIGHT - 1:
        if x > 0:
            neighbors.append([board[y - 1][x - 1], board[y][x - 1], 99])
            neighbors.append([99, board[y - 1][x], 99])
        elif x == 0:
            neighbors.append([99, 99, 99])
            neighbors.append([99, board[y - 1][x], 99])
        if x < GRID_WIDTH - 1:
            neighbors.append([board[y - 1][x + 1], board[y][x + 1], 99])
        elif x == GRID_WIDTH - 1:
            neighbors.append([99, 99, 99])

    zero_count = 0
    flag_count = 0
    zero_loc = []
    flag_loc = []
    for i in range(len(neighbors)):
        row = neighbors[i]
        for j in range(len(row)):
            if neighbors[i][j] == 0:
                zero_count += 1
                zero_loc.append([i, j])
            if neighbors[i][j] == 9:
                flag_count += 1
                flag_loc.append([i, j])
    value = board[y][x]
    if zero_count + flag_count == value:
        for zero in zero_loc:
            board[y + zero[1] - 1][x + zero[0] - 1] = 9
            """
            zero_x = (x + zero[0] - 1) * 25 + 985
            zero_y = (y + zero[1] - 1) * 25 + 525
            if not out_of_grid(zero_x, zero_y):
                pyautogui.moveTo(zero_x, zero_y)
                sleep(0.005)
                pyautogui.click(button="right")
            """
            output += 1
        completed_tiles.append([y, x])
    elif flag_count == value:
        for zero in zero_loc:
            x = (x + zero[0] - 1) * 25 + 985
            y = (y + zero[1] - 1) * 25 + 525
            if not out_of_grid(x, y):
                pyautogui.moveTo(x, y)
                sleep(0.005)
                pyautogui.click(button='left')
            output += 1
    elif likelies and len(zero_loc) > 0:
        zero = random.choice(zero_loc)
        x = (x + zero[0] - 1) * 25 + 985
        y = (y + zero[1] - 1) * 25 + 525
        z_score = zero_count - value
        likelies_list.append([z_score, [x, y]])

    return output


def process_board(guess):
    global outputs, click_list, run
    click_list = []
    outputs = []
    global board
    for i in range(len(board)):
        row = board[i]
        for j in range(len(row)):
            tile = board[i][j]
            if tile == 0 or tile == -1:
                continue
            elif [i, j] in completed_tiles:
                continue
            if guess:
                likelies = True
            else:
                likelies = False
            outputs.append(check_neighbors(i, j, likelies))


# Main

# Board setup
board = []
for i in range(GRID_WIDTH):
    board.append(0)
board = np.array([board for i in range(GRID_HEIGHT)])

# Loop
run = True
guess_count = 0
while run:
    img = ImageGrab.grab(bbox=(980, 520, 1580, 1020))
    np_img = np.array(img)

    update_board(np_img)
    process_board(guess)
    sum = 0
    for value in outputs:
        sum += value
    if sum == 0:
        guess_count += 1
        if guess_count > 3:
            guess_count = 0
            guess = True
            print("Making a guess...")
            process_board(guess)
    if guess:
        sorted_list = sorted(likelies_list, key=itemgetter(0), reverse=True)
        pick = sorted_list[0]
        pyautogui.moveTo(pick[1][0], pick[1][1])
        pyautogui.click()
        likelies_list = []
        guess = False
        img = ImageGrab.grab(bbox=(980, 520, 1580, 1020))
        np_img = np.array(img)
        update_board(np_img)
    try:
        if keyboard.is_pressed('q'):
            run = False
            break
    except:
        continue
