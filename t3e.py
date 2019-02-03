import t3e_renderer as t3e_r

winner = 0
neutral = 20
X = 1
O = 5

################################################################################

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
    global winner
    if sum == 3*X:
        if type(grid) == sub_grid:
            grid.owner = X
            return
        else:
            winner = X
            return
    if sum == 3*O:
        if type(grid) == sub_grid:
            grid.owner = O
            return
        else:
            winner = O
            return

def chk_grid(grid):
    global winner
    draw = 0
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
        chk_win(grid, cell_sum)
        draw += chk_draw(cell_sum)

    for c in range(3):
        cell_sum = 0
        for r in range(3):
            if type(grid) == sub_grid:
                cell_sum += contents[r][c]
            else:
                cell_sum += contents[r][c].owner
        chk_win(grid, cell_sum)
        draw += chk_draw(cell_sum)

    cell_sum = 0
    for d1 in range(3):
        if type(grid) == sub_grid:
            cell_sum += contents[d1][d1]
        else:
            cell_sum += contents[d1][d1].owner
    chk_win(grid, cell_sum)
    draw += chk_draw(cell_sum)

    cell_sum = 0
    for d2 in range(3):
        if type(grid) == sub_grid:
            cell_sum += contents[d2][2 - d2]
        else:
            cell_sum += contents[d2][2 - d2].owner
    chk_win(grid, cell_sum)
    draw += chk_draw(cell_sum)

    if draw == 8:
        if type(grid) == sub_grid:
            grid.owner = neutral
            return
        else:
            winner = neutral
            return

################################################################################

class sub_grid:
    def __init__(self, r, c):
        self.owner = 0
        self.location = (r, c)
        self.contents = [[0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0]]
    def update_cell(self, r, c, player):
        self.contents[r][c] = player

major_grid = [[sub_grid(0, 0), sub_grid(0, 1), sub_grid(0, 2)],
              [sub_grid(1, 0), sub_grid(1, 1), sub_grid(1, 2)],
              [sub_grid(2, 0), sub_grid(2, 1), sub_grid(2, 2)]]
r_coord = 1
c_coord = 1

class save_state:
    def __init__(self):
        self.l_major_grid = [[sub_grid(0, 0), sub_grid(0, 1), sub_grid(0, 2)],
                             [sub_grid(1, 0), sub_grid(1, 1), sub_grid(1, 2)],
                             [sub_grid(2, 0), sub_grid(2, 1), sub_grid(2, 2)]]
        self.l_r_coord = 1
        self.l_c_coord = 1
    def save(self, major_grid, r_coord, c_coord):
        for i in range(3):
            for j in range(3):
                self.l_major_grid[i][j].owner = major_grid[i][j].owner
                self.l_major_grid[i][j].location = major_grid[i][j].location
                self.l_major_grid[i][j].contents = major_grid[i][j].contents[:]
        self.l_r_coord = r_coord
        self.l_c_coord = c_coord
    def load(self):
        global major_grid
        global r_coord
        global c_coord
        for i in range(3):
            for j in range(3):
                major_grid[i][j].owner = self.l_major_grid[i][j].owner
                major_grid[i][j].location = self.l_major_grid[i][j].location
                major_grid[i][j].contents = self.l_major_grid[i][j].contents[:]
        r_coord = self.l_r_coord
        c_coord = self.l_c_coord

front_save = save_state()
back_save = save_state()
player = X #Change to accept from user later

################################################################################

while True:
    back_save.save(front_save.l_major_grid, front_save.l_r_coord, front_save.l_c_coord)
    front_save.save(major_grid, r_coord, c_coord)

    try:
        print("\n################################################################################\n{0}'s TURN."
              .format(t3e_r.displayer(player)))
        print(t3e_r.render(major_grid))

        focus_grid = major_grid[r_coord][c_coord]
        if focus_grid.owner:
            print("\nThe grid you landed on is already owned. Select a new grid to move in.")
            while True:
                try:
                    tr_coord = int(input("Enter row coordinate of new grid: ")) - 1
                    tc_coord = int(input("Enter col coordinate of new grid: ")) - 1
                    if type(major_grid[tr_coord][tc_coord]) == sub_grid:
                        r_coord = tr_coord
                        c_coord = tc_coord
                        focus_grid = major_grid[r_coord][c_coord]
                        break
                    else:
                        print("\nInvalid coordinates.\n")
                except Exception:
                    print("\nInvalid coordinates.\n")
        print("\nYou are moving in grid ({0}, {1}).".format(str(focus_grid.location[0] + 1),
                                                            str(focus_grid.location[1] + 1)))

        while True:
            try:
                tr_coord = int(input("Enter row coordinate of your move: ")) - 1
                tc_coord = int(input("Enter col coordinate of your move: ")) - 1
                if focus_grid.contents[tr_coord][tc_coord] == 0:
                    r_coord = tr_coord
                    c_coord = tc_coord
                    focus_grid.update_cell(r_coord, c_coord, player)
                    break
                else:
                    print("\nInvalid coordinates.\n")
            except Exception:
                print("\nInvalid coordinates.\n")

        chk_grid(focus_grid)
        if focus_grid.owner and focus_grid.owner != neutral:
            print("\n{0} has won grid ({1}, {2})!".format(t3e_r.displayer(focus_grid.owner),
                                                          str(focus_grid.location[0] + 1),
                                                          str(focus_grid.location[1] + 1)))
            chk_grid(major_grid)
            if winner:
                print("\n################################################################################\n"
                      .format(t3e_r.displayer(player)))
                print(t3e_r.render(major_grid))
                break
        if focus_grid.owner == neutral:
            print("\nGrid ({0}, {1}) is drawn - no winner possible.".format(str(focus_grid.location[0] + 1),
                                                                            str(focus_grid.location[1] + 1)))
            major_grid[focus_grid.location[0]][focus_grid.location[1]] = focus_grid.owner
            chk_grid(major_grid)
            if winner == neutral:
                print(t3e_r.render(major_grid))
                break
        player = switch_player(player)

    except KeyboardInterrupt:
        print("\n\nKeyboard interrupt menu:\n1. Revert turn\n2. Exit game\n3. Cancel")
        choice = int(input("Enter your choice (1/2/3): "))
        if choice == 1:
            print("Continuing from previous turn.")
            back_save.load()
            player = switch_player(player)
            continue
        elif choice == 2:
            pause = input("Game ended. Press enter to exit.")
            exit()
        elif choice == 3:
            print("Resuming game.")
        else:
            print("Invalid choice. Resuming game.")

if winner != neutral:
    print("\n\n{0} has won the game!".format(t3e_r.displayer(winner)))
else:
    print("Game is drawn!")
pause = input("Press enter to exit.")
exit()
