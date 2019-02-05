
neutral = 15
X = 1
O = 3

def chk_potential(sum, player):
    if player == X:
        if sum == 2*X:
            return 10
        elif sum == 2*O:
            return -10
    if player == O:
        if sum == 2*X:
            return -10
        elif sum == 2*O:
            return 10
    return 5

def process_potential(potential):
    if potential == 10:
        return 1
    if potential == -10:
        return -4
    return 0

def assign_cell_scores(grid, score, row_col, type):
    if type == 'r':
        for i in range(3):
            if grid[row_col][i] == 0:
                grid[row_col][i] = score
    if type == 'c':
        for j in range(3):
            if grid[j][row_col] == 0:
                grid[j][row_col] = score
    if type == 'd1':
        for m in range(3):
            if grid[m][m] == 0:
                grid[m][m] = score
    if type == 'd2':
        for n in range(3):
            if grid[n][2 - n] == 0:
                grid[n][2 - n] = score

def scan_grid(focus_grid, player):
    score_grid = [[0, 0, 0],
                  [0, 0, 0],
                  [0, 0, 0]]
    cell_sum = 0
    for i in range(3):
        for j in range(3):
            focus_grid[i][j] += cell_sum
        assign_cell_scores(score_grid, chk_potential(cell_sum, player), i, 'r')

    cell_sum = 0
    for h in range(3):
        for k in range(3):
            focus_grid[k][h] += cell_sum
        assign_cell_scores(score_grid, chk_potential(cell_sum, player), h, 'c')

    cell_sum = 0
    for m in range(3):
        focus_grid[m][m] += cell_sum
    assign_cell_scores(score_grid, chk_potential(cell_sum, player), m, 'd1')

    cell_sum = 0
    for n in range(3):
        focus_grid[n][2 - n] += cell_sum
    assign_cell_scores(score_grid, chk_potential(cell_sum, player), n, 'd2')

    return score_grid

def scan_path(major_grid, start_loc, iterations, player):
    if iterations >= 0:
        score_grid = scan_grid(major_grid[start_loc[0]][start_loc[1]], player)
        further_moves = []
        max = score_grid[0][0]
        for r in range(3):
            for c in range(3):
                if score_grid[r][c] >= max:
                    further_moves.append((r, c))
                    max = score_grid[r][c]
        for loc in further_moves:
            #major_grid_c = copy(major_grid)
            #major_grid_c[start_loc[0]][start_loc[1]].contents[loc[0][loc[1]]] = switch_player(player)
            #scan_grid(major_grid_c, loc, iterations - 1, switch_player(player))
        
