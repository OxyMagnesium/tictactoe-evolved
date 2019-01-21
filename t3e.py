import t3e_renderer as t3e_r

winner = None
X = 1
O = 5

################################################################################

def switchplayer(i):
    if i == X:
        return O
    elif i == O:
        return X

def chk_win(grid, sum):
    if sum == 3*X:
        if type(grid) == sub_grid:
            grid.owner = X
            return
        else:
            winner = X
            return
    if sum == 3*O:
        if type(grid) == type:
            grid.owner = O
            return
        else:
            winner = O
            return

def chk_grid(grid):
    if type(grid) == sub_grid:
        contents = grid.contents
    else:
        contents = grid
    try:
        for r in range(3):
            cell_sum = 0
            for c in range(3):
                cell_sum += contents[r][c]
            chk_win(grid, cell_sum)

        for c in range(3):
            cell_sum = 0
            for r in range(3):
                cell_sum += contents[r][c]
            chk_win(grid, cell_sum)

        cell_sum = 0
        for d1 in range(3):
            cell_sum += contents[d1][d1]
        chk_win(grid, cell_sum)

        cell_sum = 0
        for d2 in range(3):
            cell_sum += contents[d2][2 - d2]
        chk_win(grid, cell_sum)
    except TypeError:
        pass

################################################################################

class sub_grid:
    def __init__(self, r, c):
        self.owner = None
        self.location = (r, c)
        self.contents = [[0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0]]
    def update_cell(self, r, c, player):
        self.contents[r][c] = player

grid_00 = sub_grid(0, 0)
grid_01 = sub_grid(0, 1)
grid_02 = sub_grid(0, 2)

grid_10 = sub_grid(1, 0)
grid_11 = sub_grid(1, 1)
grid_12 = sub_grid(1, 2)

grid_20 = sub_grid(2, 0)
grid_21 = sub_grid(2, 1)
grid_22 = sub_grid(2, 2)

major_grid = [[grid_00, grid_01, grid_02],
              [grid_10, grid_11, grid_12],
              [grid_20, grid_21, grid_22]]

focus_grid = major_grid[1][1]
player = X #Change to accept from user later
print("{0}'s TURN.".format(t3e_r.displayer(player)))
print(t3e_r.render(major_grid))

################################################################################

while True:
    print("\nYou are moving in grid ({0}, {1}).".format(str(focus_grid.location[0] + 1), str(focus_grid.location[1] + 1)))

    while True:
        try:
            r_coord = int(input("Enter row coordinate of your move: ")) - 1
            c_coord = int(input("Enter col coordinate of your move: ")) - 1
            if focus_grid.contents[r_coord][c_coord] == 0:
                focus_grid.update_cell(r_coord, c_coord, player)
                break
            else:
                print("\nInvalid coordinates.\n")
        except KeyboardInterrupt:
            print("\n\nExiting due to keyboard interrupt.")
            exit()
        except Exception:
            print("\nInvalid coordinates.\n")

    chk_grid(focus_grid)
    if focus_grid.owner:
        print("\n{0} has won grid ({1}, {2})!".format(t3e_r.displayer(focus_grid.owner), str(focus_grid.location[0] + 1), str(focus_grid.location[1] + 1)))
        major_grid[focus_grid.location[0]][focus_grid.location[1]] = focus_grid.owner
        chk_grid(major_grid)
        if winner:
            print(t3e_r.render(major_grid))
            break
    print(t3e_r.render(major_grid))

    player = switchplayer(player)
    print("\n\n{0}'s TURN.".format(t3e_r.displayer(player)))

    focus_grid = major_grid[r_coord][c_coord]
    if type(focus_grid) == int:
        print("\nThe grid you landed on is already owned. Select a new grid to move in.")
        while True:
            try:
                r_coord = int(input("Enter row coordinate of new grid: ")) - 1
                c_coord = int(input("Enter col coordinate of new grid: ")) - 1
                if type(major_grid[r_coord][c_coord]) == sub_grid:
                    focus_grid = major_grid[r_coord][c_coord]
                    break
                else:
                    print("\nInvalid coordinates.\n")
            except KeyboardInterrupt:
                print("\n\nExiting due to keyboard interrupt.")
                exit()
            except Exception:
                print("\nInvalid coordinates.\n")

print("\n\n{0} has won the game!".format(t3e_r.displayer(winner)))
pause = input("Press enter to exit.")
