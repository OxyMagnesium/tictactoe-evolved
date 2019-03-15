#Contains logic for computer moves.

import t3e_resources as t3e_u
import random
from multiprocessing import Pool
from os import cpu_count
from time import time
from copy import deepcopy

NEG_INF = -32768
NEUTRAL = 20
X = 1
O = 5

#Recursion lengths
NORMAL_ITERS = 2
HARD_ITERS = 4
LEG_ITERS = 8

#Scores
WIN_PLAYER = 18
WIN_OPPONENT = 10
WIN_NONE = 2

def copy_grid(major_grid):
    return deepcopy(major_grid)

def get_max_locs(score_grid):
    locs = []
    max = score_grid[1][1]
    for i in range(3):
        for j in range(3):
            if score_grid[i][j] > max:
                max = score_grid[i][j]
    for i in range(3):
        for j in range(3):
            if score_grid[i][j] == max:
                locs.append((i, j))
    return locs

def chk_cells_sum(sum, player):
    if player == X:
        if sum == 2*X:
            return WIN_PLAYER
        elif sum == 2*O:
            return WIN_OPPONENT
    elif player == O:
        if sum == 2*X:
            return WIN_OPPONENT
        elif sum == 2*O:
            return WIN_PLAYER
    return WIN_NONE

def assign_scores(score_grid, actual_grid, r_or_c, type, score):
    if type == 'r':
        for i in range(3):
            if not actual_grid[r_or_c][i]:
                score_grid[r_or_c][i] += score
    elif type == 'c':
        for i in range(3):
            if not actual_grid[i][r_or_c]:
                score_grid[i][r_or_c] += score
    elif type == 'd1':
        for i in range(3):
            if not actual_grid[i][i]:
                score_grid[i][i] += score
    elif type == 'd2':
        for i in range(3):
            if not actual_grid[i][2 - i]:
                score_grid[i][2 - i] += score

def scan_grid(grid, player):
    if type(grid[1][1]) == t3e_u.sub_grid:
        grid = [[grid[a][b].owner for b in range(3)] for a in range(3)]
    score_grid = [[0 for a in range(3)] for b in range(3)]
    cells_sum = 0
    for i in range(3):
        for j in range(3):
            cells_sum += grid[i][j]
        assign_scores(score_grid, grid, i, 'r', chk_cells_sum(cells_sum, player))
        cells_sum = 0
    for i in range(3):
        for j in range(3):
            cells_sum += grid[j][i]
        assign_scores(score_grid, grid, i, 'c', chk_cells_sum(cells_sum, player))
        cells_sum = 0
    for i in range(3):
        cells_sum += grid[i][i]
    assign_scores(score_grid, grid, -1, 'd1', chk_cells_sum(cells_sum, player))
    cells_sum = 0
    for i in range(3):
        cells_sum += grid[i][2 - i]
    assign_scores(score_grid, grid, -1, 'd2', chk_cells_sum(cells_sum, player))
    cells_sum = 0
    return score_grid

def correct_for_owner(major_grid, start_loc, iters, player, cutoff):
    if iters % 2 == 0:
        iters -= 1
    if major_grid[start_loc[0]][start_loc[1]].owner:
        score_grid = [[NEG_INF for a in range(3)] for b in range(3)]
        for i in range(3):
            for j in range(3):
                if not major_grid[i][j].owner:
                    score_grid[i][j] = scan_path(copy_grid(major_grid), (i, j),
                                                 iters, player, cutoff)
        return random.choice(get_max_locs(score_grid))
    else:
        return start_loc

def scan_path(major_grid, start_loc, iters, player, cutoff):
    start_loc = correct_for_owner(major_grid, start_loc, iters, player, cutoff)
    score_grid = scan_grid(major_grid[start_loc[0]][start_loc[1]].contents, player)
    mult_grid = scan_grid(major_grid, player)
    for i in range(3):
        for j in range(3):
            score_grid[i][j] -= mult_grid[i][j]
    if iters > 0 and cutoff > time():
        for i in range(3):
            for j in range(3):
                if major_grid[start_loc[0]][start_loc[1]].contents[i][j]:
                    score_grid[i][j] = NEG_INF
                    continue
                major_grid_copy = copy_grid(major_grid)
                major_grid_copy[start_loc[0]][start_loc[1]].update_cell(i, j, player)
                t3e_u.chk_grid(major_grid_copy[start_loc[0]][start_loc[1]])
                if not major_grid_copy[start_loc[0]][start_loc[1]].owner:
                    score_grid[i][j] += max(max(scan_grid(major_grid_copy[start_loc[0]][start_loc[1]].contents,
                                                          player)))*2
                score_grid[i][j] -= scan_path(major_grid_copy, (i, j), iters - 1,
                                              t3e_u.switch_player(player), cutoff)*mult_grid[i][j]/2

    final_loc = random.choice(get_max_locs(score_grid))
    return score_grid[final_loc[0]][final_loc[1]]

def compute_move(major_grid, start_loc, difficulty, player):
    random.seed()

    if difficulty == 1:
        while major_grid[start_loc[0]][start_loc[1]].owner:
            start_loc = (random.randrange(0, 3), random.randrange(0, 3))
        move = (random.randrange(0, 3), random.randrange(0, 3))
        while major_grid[start_loc[0]][start_loc[1]].contents[move[0]][move[1]]:
            move = (random.randrange(0, 3), random.randrange(0, 3))
        return move

    elif difficulty == 2:
        iters = NORMAL_ITERS
        cutoff = time() + 1
    elif difficulty == 3:
        iters = HARD_ITERS
        cutoff = time() + 3
    elif difficulty == 4:
        iters = LEG_ITERS
        cutoff = time() + 7

    start_loc = correct_for_owner(major_grid, start_loc, 1, player, cutoff)
    score_grid = scan_grid(major_grid[start_loc[0]][start_loc[1]].contents, player)
    player = t3e_u.switch_player(player)
    pool = Pool(processes = 9)
    results = {}
    mult_grid = scan_grid(major_grid, player)
    for i in range(3):
        for j in range(3):
            score_grid[i][j] -= mult_grid[i][j]
    for i in range(3):
        for j in range(3):
            if major_grid[start_loc[0]][start_loc[1]].contents[i][j]:
                score_grid[i][j] = NEG_INF
                continue
            major_grid_copy = copy_grid(major_grid)
            major_grid_copy[start_loc[0]][start_loc[1]].contents[i][j] = player
            t3e_u.chk_grid(major_grid_copy[start_loc[0]][start_loc[1]])
            if not major_grid_copy[start_loc[0]][start_loc[1]].owner:
                score_grid[i][j] += max(max(scan_grid(major_grid_copy[start_loc[0]][start_loc[1]].contents,
                                                  player)))*2
            results[(i, j)] = pool.apply_async(scan_path, args = (major_grid_copy,
                                                                  (i, j), iters,
                                                                  player, cutoff))

    pool.close()
    for loc in results:
        score_grid[loc[0]][loc[1]] -= results[loc].get()*mult_grid[i][j]/2
    pool.join()
    print("Scores: " + str(score_grid))

    return random.choice(get_max_locs(score_grid))
