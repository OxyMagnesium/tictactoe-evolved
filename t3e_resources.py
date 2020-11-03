#Contains resources used in multiple modules.

NEUTRAL = 20
X = 1
O = 5

class sub_grid:
    def __init__(self, s_grid = None):
        if s_grid is None:
            self.owner = 0
            self.threats = {X: 0, O: 0}
            self.contents = [[0 for _ in range(3)] for _ in range(3)]
        else:
            self.owner = s_grid.owner
            self.threats = {X: s_grid.threats[X], O: s_grid.threats[O]}
            self.contents = [row[:] for row in s_grid.contents]

    def get_owner(self):
        return self.owner

    def get_threats(self, player = None):
        if player:
            return self.threats[player]
        else:
            return self.threats

    def get_contents(self, cell = None):
        if cell:
            return self.contents[cell[0]][cell[1]]
        else:
            return self.contents

    def update_cell(self, loc, player, move_caps_grid = None):
        self.contents[loc[0]][loc[1]] = player
        if move_caps_grid is None:
            move_caps_grid = move_won_grid(self, loc, player)
        if move_caps_grid:
            self.owner = player
        elif all(all(row) for row in self.contents):
            self.owner = NEUTRAL
        return self.owner

    def __getitem__(self, index):
        return self.contents[index]


class major_grid:
    def __init__(self, m_grid = None):
        if m_grid is None:
            self.threats = {X: 0, O: 0}
            self.contents = [[sub_grid() for _ in range(3)] for _ in range(3)]
        else:
            self.threats = {X: m_grid.threats[X], O: m_grid.threats[O]}
            self.contents = [[sub_grid(s_grid) for s_grid in row]
                             for row in m_grid.contents]

    def get_obj(self, loc):
        return self.contents[loc[0]][loc[1]]

    def get_owner(self, loc):
        return self.contents[loc[0]][loc[1]].owner

    def get_threats(self, loc = None, player = None):
        if loc:
            return self.contents[loc[0]][loc[1]].get_threats(player)
        else:
            return self.threats[player] if player else self.threats

    def get_contents(self, loc = None, cell = None):
        if loc:
            return self.contents[loc[0]][loc[1]].get_contents(cell)
        else:
            return [[s_grid.owner for s_grid in row] for row in self.contents]

    def __getitem__(self, index):
        return self.contents[index]


def move_won_grid(grid, move, player):
    grid_cont = grid.get_contents()
    row_sum = 0
    col_sum = 0
    d1_sum = 0
    d2_sum = 0
    for i in range(3):
        row_sum += grid_cont[move[0]][i]
        col_sum += grid_cont[i][move[1]]
    if move[0] == move[1]:
        for i in range(3):
            d1_sum += grid_cont[i][i]
    if move[0] + move[1] == 2:
        for i in range(3):
            d2_sum += grid_cont[2 - i][i]
    if 3*player in (row_sum, col_sum, d1_sum, d2_sum):
        return True
    else:
        return False

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
