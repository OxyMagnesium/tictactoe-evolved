#Main program.

import t3e_resources as t3e_u
import t3e_renderer as t3e_r
from t3e_ai import compute_move

winner = None
NEUTRAL = 20
X = 1
O = 5

major_grid = [[t3e_u.sub_grid(a, b) for b in range(3)] for a in range(3)]

class save_state:
    def __init__(self):
        self.loaded = True
        self.l_r_coord = 1
        self.l_c_coord = 1
    def save(self, e_r_coord, e_c_coord):
        self.loaded = False
        self.l_r_coord = e_r_coord
        self.l_c_coord = e_c_coord
    def load(self):
        if self.loaded:
            print("Can't revert twice. Resuming game.")
            return
        global major_grid
        global r_coord
        global c_coord
        global turn
        nl_r_coord = front_save.l_r_coord
        nl_c_coord = front_save.l_c_coord
        l_r_coord = self.l_r_coord
        l_c_coord = self.l_c_coord
        major_grid[nl_r_coord][nl_c_coord].contents[r_coord][c_coord] = 0
        major_grid[l_r_coord][l_c_coord].contents[nl_r_coord][nl_c_coord] = 0
        r_coord = l_r_coord
        c_coord = l_c_coord
        turn -= 2
        self.loaded = True

turn = 1
r_coord = 1
c_coord = 1
front_save = save_state()
back_save = save_state()
save = save_state()

################################################################################

if __name__ == "__main__":
    print("Welcome to TicTacToe Evolved by Om Gupta!")

    ai_enabled = True if input("\nSelect player count (1/2): ") == '1' else False
    if ai_enabled:
        ai_player = input("Select your type (X/O, X goes first): ")
        ai_player = O if ai_player == 'X' else X
        print("Select difficulty level:\n1. Easy\n2. Normal\n3. Hard\n4. Legendary")
        difficulty = int(input("Enter your choice (1/2/3/4): "))

    player = X
    print("\nStarting game.")

    while True:
        try:
            print("\n################################################################################\n{0}'s TURN."
                  .format(t3e_u.displayer(player)))
            print(t3e_r.render(major_grid))
            focus_grid = major_grid[r_coord][c_coord]

            if not ai_enabled or player != ai_player:
                if focus_grid.owner:
                    print("\nThe grid you landed on is already owned. Select a new grid to move in.")
                    while True:
                        try:
                            tr_coord = int(input("Enter row coordinate of new grid: ")) - 1
                            tc_coord = int(input("Enter col coordinate of new grid: ")) - 1
                            if not major_grid[tr_coord][tc_coord].owner:
                                focus_grid = major_grid[tr_coord][tc_coord]
                                break
                            else:
                                print("\nInvalid coordinates.\n")
                        except Exception:
                            print("\nInvalid coordinates.\n")

                print("\nYou are moving in grid ({0}, {1})."
                      .format(str(focus_grid.location[0] + 1),
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
            else:
                print("\nAI's move.")
                ai_move = compute_move(major_grid, focus_grid.location, difficulty,
                                       player, turn)
                focus_grid = major_grid[ai_move[0][0]][ai_move[0][1]]
                r_coord = ai_move[1][0]
                c_coord = ai_move[1][1]
                focus_grid.update_cell(r_coord, c_coord, player)

            t3e_u.chk_grid(focus_grid)
            if focus_grid.owner and focus_grid.owner != NEUTRAL:
                print("\n{0} has won grid ({1}, {2})!"
                      .format(t3e_u.displayer(focus_grid.owner),
                              str(focus_grid.location[0] + 1),
                              str(focus_grid.location[1] + 1)))
                winner = t3e_u.chk_grid(major_grid)
                if winner:
                    print("\n################################################################################\n"
                          .format(t3e_u.displayer(player)))
                    print(t3e_r.render(major_grid))
                    break
            elif focus_grid.owner == NEUTRAL:
                print("\nGrid ({0}, {1}) is drawn - no winner possible."
                      .format(str(focus_grid.location[0] + 1),
                              str(focus_grid.location[1] + 1)))
                t3e_u.chk_grid(major_grid)
                if winner == NEUTRAL:
                    print(t3e_r.render(major_grid))
                    break
            player = t3e_u.switch_player(player)
            turn += 1

        except KeyboardInterrupt:
            print("\n\nKeyboard interrupt menu:\n1. Revert turn\n2. Exit game\n3. Cancel")
            choice = int(input("Enter your choice (1/2/3): "))
            if choice == 1:
                print("Continuing from previous turn.")
                save.load()
                continue
            elif choice == 2:
                pause = input("Game ended. Press enter to exit.")
                exit()
            elif choice == 3:
                print("Resuming game.")
            else:
                print("Invalid choice. Resuming game.")

        save.save(back_save.l_r_coord, back_save.l_c_coord)
        back_save.save(front_save.l_r_coord, front_save.l_c_coord)
        front_save.save(r_coord, c_coord)

    if winner != NEUTRAL:
        print("\n\n{0} has won the game!".format(t3e_u.displayer(winner)))
    else:
        print("Game is drawn!")
    pause = input("Press enter to exit.")
    exit()
