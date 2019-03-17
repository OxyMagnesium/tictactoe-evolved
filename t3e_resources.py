#Contains resources used in multiple modules.

NEUTRAL = 20
X = 1
O = 5

class sub_grid:
    def __init__(self, r, c):
        self.owner = 0
        self.location = (r, c)
        self.contents = [[0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0]]
    def update_cell(self, r, c, player):
        self.contents[r][c] = player

def displayer(i):
    if i == X:
        return 'X'
    elif i == O:
        return 'O'
    elif i == NEUTRAL:
        return ' '
    elif i == 0:
        return '-'

def switch_player(i):
    if i == X:
        return O
    elif i == O:
        return X

def chk_draw(sum):
    if sum != 0 and (sum != X and sum != 2*X) and (sum != O and sum != 2*O):
        return 1
    else:
        return 0

def chk_win(grid, sum):
    if sum == 3*X:
        if type(grid) == sub_grid:
            grid.owner = X
            return None
        else:
            return X
    if sum == 3*O:
        if type(grid) == sub_grid:
            grid.owner = O
            return None
        else:
            return O

def chk_grid(grid):
    draw = 0
    winner = None
    if type(grid) == sub_grid:
        contents = grid.contents
    else:
        contents = grid

    for r in range(3):
        cell_sum = 0
        for c in range(3):
            if type(grid) == sub_grid:
                cell_sum += contents[r][c]
            else:
                cell_sum += contents[r][c].owner
        winner = chk_win(grid, cell_sum)
        draw += chk_draw(cell_sum)
        if winner:
            return winner

    for c in range(3):
        cell_sum = 0
        for r in range(3):
            if type(grid) == sub_grid:
                cell_sum += contents[r][c]
            else:
                cell_sum += contents[r][c].owner
        winner = chk_win(grid, cell_sum)
        draw += chk_draw(cell_sum)
        if winner:
            return winner

    cell_sum = 0
    for d1 in range(3):
        if type(grid) == sub_grid:
            cell_sum += contents[d1][d1]
        else:
            cell_sum += contents[d1][d1].owner
    winner = chk_win(grid, cell_sum)
    draw += chk_draw(cell_sum)
    if winner:
        return winner

    cell_sum = 0
    for d2 in range(3):
        if type(grid) == sub_grid:
            cell_sum += contents[d2][2 - d2]
        else:
            cell_sum += contents[d2][2 - d2].owner
    winner = chk_win(grid, cell_sum)
    draw += chk_draw(cell_sum)
    if winner:
        return winner

    if draw == 8:
        if type(grid) == sub_grid:
            grid.owner = NEUTRAL
        else:
            winner = NEUTRAL
    return winner
