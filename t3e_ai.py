#Contains logic for computer moves.

import t3e_resources as t3e_u
import random
from multiprocessing import Pool
from os import cpu_count
from time import time
from copy import deepcopy

NEG_INF = -32768
POS_INF = 32767
NEUTRAL = 20
X = 1
O = 5

#Recursion lengths
NORMAL_ITERS = 1
HARD_ITERS = 3
LEG_ITERS = 7

#Scores
WIN_PLAYER = 13
WIN_OPPONENT = 5
WIN_NONE = 1

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

def chk_cells_sum(sum, player, mode):
    if player == X:
        if sum == 2*X:
            return WIN_PLAYER
        elif sum == 2*O:
            return WIN_OPPONENT*mode
    elif player == O:
        if sum == 2*X:
            return WIN_OPPONENT*mode
        elif sum == 2*O:
            return WIN_PLAYER
    return WIN_NONE*(mode + 1)/2

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

def scan_grid(grid, player, mode = 1):
    if type(grid[1][1]) == t3e_u.sub_grid:
        grid = [[grid[a][b].owner for b in range(3)] for a in range(3)]
    score_grid = [[1 for a in range(3)] for b in range(3)]
    cells_sum = 0
    for i in range(3):
        for j in range(3):
            cells_sum += grid[i][j]
        assign_scores(score_grid, grid, i, 'r', chk_cells_sum(cells_sum, player, mode))
        cells_sum = 0
    for i in range(3):
        for j in range(3):
            cells_sum += grid[j][i]
        assign_scores(score_grid, grid, i, 'c', chk_cells_sum(cells_sum, player, mode))
        cells_sum = 0
    for i in range(3):
        cells_sum += grid[i][i]
    assign_scores(score_grid, grid, -1, 'd1', chk_cells_sum(cells_sum, player, mode))
    cells_sum = 0
    for i in range(3):
        cells_sum += grid[i][2 - i]
    assign_scores(score_grid, grid, -1, 'd2', chk_cells_sum(cells_sum, player, mode))
    cells_sum = 0
    return score_grid

def correct_for_owner(major_grid, start_loc, iters, player, cutoff):
    if major_grid[start_loc[0]][start_loc[1]].owner:
        if iters % 2 != 0:
            iters -= 1
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
    c_cutoff = 4.5
    for i in range(3):
        for j in range(3):
            if major_grid[start_loc[0]][start_loc[1]].contents[i][j]:
                score_grid[i][j] = NEG_INF
                continue
            major_grid_copy = copy_grid(major_grid)
            major_grid_copy[start_loc[0]][start_loc[1]].update_cell(i, j, player)
            t3e_u.chk_grid(major_grid_copy[start_loc[0]][start_loc[1]])
            if not major_grid_copy[start_loc[0]][start_loc[1]].owner:
                new_grid = scan_grid(major_grid_copy[start_loc[0]][start_loc[1]].contents,
                                     player, -1)
                for a, b, c in new_grid:
                    score_grid[i][j] += (a + b + c)/2
            else:
                score_grid[i][j] += WIN_PLAYER*4
                winner = t3e_u.chk_grid(major_grid_copy)
                if winner:
                    return POS_INF
            if iters > 0 and cutoff > time():
                c_cutoff -= 1
                a_cutoff = cutoff - (cutoff - time())*c_cutoff/9
                score_grid[i][j] -= scan_path(major_grid_copy, (i, j), iters - 1,
                                              t3e_u.switch_player(player), a_cutoff)*mult_grid[i][j]/6
    return max(max(score_grid))

def compute_move(major_grid, start_loc, difficulty, player, turn):
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
        cutoff = time() + 1*(1.1**turn)
    elif difficulty == 3:
        iters = HARD_ITERS
        cutoff = time() + 2*(1.1**turn)
    elif difficulty == 4:
        iters = LEG_ITERS
        cutoff = time() + 4*(1.1**turn)

    start_loc = correct_for_owner(major_grid, start_loc, 1, player, cutoff)
    score_grid = scan_grid(major_grid[start_loc[0]][start_loc[1]].contents, player)
    mult_grid = scan_grid(major_grid, player)
    print("Initial grid scores: " + str(score_grid))
    print("Initial board scores: " + str(mult_grid))
    pool = Pool(processes = 9)
    results = {}
    for i in range(3):
        for j in range(3):
            if major_grid[start_loc[0]][start_loc[1]].contents[i][j]:
                score_grid[i][j] = NEG_INF
                continue
            major_grid_copy = copy_grid(major_grid)
            major_grid_copy[start_loc[0]][start_loc[1]].contents[i][j] = player
            t3e_u.chk_grid(major_grid_copy[start_loc[0]][start_loc[1]])
            if not major_grid_copy[start_loc[0]][start_loc[1]].owner:
                new_grid = scan_grid(major_grid_copy[start_loc[0]][start_loc[1]].contents,
                                     player)
                for a, b, c in new_grid:
                    score_grid[i][j] += (a + b + c)/2
            else:
                score_grid[i][j] += WIN_PLAYER*4
                winner = t3e_u.chk_grid(major_grid_copy)
                if winner:
                    score_grid[i][j] = POS_INF
                    continue
            player = t3e_u.switch_player(player)
            results[(i, j)] = pool.apply_async(scan_path, args = (major_grid_copy,
                                                                  (i, j), iters,
                                                                  player, cutoff))

    pool.close()
    for loc in results:
        score_grid[loc[0]][loc[1]] -= results[loc].get()*mult_grid[i][j]/6
    pool.join()
    print("Final scores: " + str((score_grid)))

    return ((start_loc[0], start_loc[1]), random.choice(get_max_locs(score_grid)))
