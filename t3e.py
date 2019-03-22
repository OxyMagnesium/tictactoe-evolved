#Main program.

import threading
from copy import deepcopy
from time import sleep

import t3e_renderer as t3e_r
import t3e_resources as t3e_u
from t3e_resources import NEUTRAL, X, O
from t3e_ai import compute_move

VERSION = '0.9.2'

################################################################################

class save_state:
    def __init__(self):
        self.grid = []
        self.player = 0
        self.r = 0
        self.c = 0
        self.loaded = True
    def save(self, major_grid, player, r_coord, c_coord, loaded):
        self.grid = deepcopy(major_grid)
        self.player = player
        self.r = r_coord
        self.c = c_coord
        self.loaded = loaded

#Output will start with one of the following with the content in double quotes:
#INF - Simply display following content
#REQ - Ask for input with following content

class io_handler:
    def __init__(self, use_secondary = False):
        self.use_secondary = use_secondary
        self.primary = ['']
        self.in_primary_queue = 0
        self.secondary = ['']
        self.in_secondary_queue = 0
    def send(self, intake, primary = True):
        try:
            if intake.split('"')[0] == '' and intake.split('"')[2] == '':
                intake = 'INF ' + intake
        except IndexError:
            pass
        if primary:
            self.primary.append(intake)
            self.in_primary_queue += 1
        else:
            self.secondary.append(intake)
            self.in_secondary_queue += 1
        sleep(0.1)
    def get(self, primary = False):
        if primary or not self.use_secondary:
            while self.in_primary_queue == 0:
                sleep(0.1)
            self.in_primary_queue -= 1
            return self.primary.pop(1)
        else:
            while self.in_secondary_queue == 0:
                sleep(0.1)
            self.in_secondary_queue -= 1
            return self.secondary.pop(1)

def process_coords(io_h):
    while True:
        input = io_h.get()
        if input == 'KBI':
            raise KeyboardInterrupt
        else:
            try:
                return (int(input.split(',')[0]), int(input.split(',')[1]))
            except ValueError:
                io_h.send('REQ "The values you have entered are invalid. Try again: "')

################################################################################

def main(io_h, players):
    if players is None:
        io_h.send('REQ "Select player count (1/2): "')
        players = int(io_h.get())
    ai_enabled = True if players == 1 else False
    if ai_enabled:
        io_h.send('REQ "Select your type (X/O; X goes first): "')
        ai_player = io_h.get()
        ai_player = O if ai_player == 'X' else X
        io_h.send('INF "Select difficulty level:\n1. Easy\n2. Normal\n3. Hard\n4. Legendary"')
        io_h.send('REQ "Enter your choice (1/2/3/4): "')
        difficulty = int(io_h.get())

    turn_m0 = save_state()
    turn_m1 = save_state()
    turn_m2 = save_state()
    major_grid = [[t3e_u.sub_grid(a, b) for b in range(3)] for a in range(3)]
    player = X
    r_coord = 1
    c_coord = 1
    turn = 1

    io_h.send('INF "\nStarting game."')

    while True:
        try:
            io_h.send('"\n################################################################################\n"')
            io_h.send('"{0}\'s TURN."'.format(t3e_u.displayer(player)))
            io_h.send('"{0}"'.format(t3e_r.render(major_grid)))
            focus_grid = major_grid[r_coord][c_coord]

            if not ai_enabled or player != ai_player:
                if focus_grid.owner:
                    io_h.send('"\nThe grid you landed on is already owned. Select a new grid to move in."')
                    while True:
                        try:
                            io_h.send('REQ "Enter coordinates of new grid (R, C): "')
                            loc = process_coords(io_h)
                            tr_coord = loc[0] - 1
                            tc_coord = loc[1] - 1
                            if not major_grid[tr_coord][tc_coord].owner:
                                focus_grid = major_grid[tr_coord][tc_coord]
                                break
                            else:
                                io_h.send('"\nInvalid coordinates.\n"')
                        except IndexError:
                            io_h.send('"\nInvalid coordinates.\n"')

                io_h.send('"\nYou are moving in grid ({0}, {1})."'
                          .format(str(focus_grid.location[0] + 1),
                                  str(focus_grid.location[1] + 1)))
                while True:
                    try:
                        io_h.send('REQ "Enter coordinates of your move (R, C): "')
                        loc = process_coords(io_h)
                        tr_coord = loc[0] - 1
                        tc_coord = loc[1] - 1
                        if focus_grid.contents[tr_coord][tc_coord] == 0:
                            r_coord = tr_coord
                            c_coord = tc_coord
                            focus_grid.update_cell(r_coord, c_coord, player)
                            break
                        else:
                            io_h.send('"\nInvalid coordinates.\n"')
                    except IndexError:
                        io_h.send('"\nInvalid coordinates.\n"')
            else:
                io_h.send('"\nWaiting for computer to move."')
                ai_move = compute_move(major_grid, focus_grid.location, difficulty,
                                       player, turn)
                focus_grid = major_grid[ai_move[0][0]][ai_move[0][1]]
                r_coord = ai_move[1][0]
                c_coord = ai_move[1][1]
                focus_grid.update_cell(r_coord, c_coord, player)
                loc = 'grid ({0}, {1}), cell ({2}, {3})'.format(ai_move[0][0] + 1,
                                                                ai_move[0][1] + 1,
                                                                ai_move[1][0] + 1,
                                                                ai_move[1][1] + 1,)
                io_h.send('"{0} moved in {1}."'.format(t3e_u.displayer(player), loc))

            t3e_u.chk_grid(focus_grid)
            if focus_grid.owner and focus_grid.owner != NEUTRAL:
                io_h.send('"\n{0} has won grid ({1}, {2})!"'
                          .format(t3e_u.displayer(focus_grid.owner),
                                  str(focus_grid.location[0] + 1),
                                  str(focus_grid.location[1] + 1)))
                winner = t3e_u.chk_grid(major_grid)
                if winner:
                    io_h.send('"\n################################################################################\n"')
                    io_h.send(t3e_r.render(major_grid))
                    break
            elif focus_grid.owner == NEUTRAL:
                io_h.send('"\nGrid ({0}, {1}) is drawn - no winner possible."'
                          .format(str(focus_grid.location[0] + 1),
                                  str(focus_grid.location[1] + 1)))
                t3e_u.chk_grid(major_grid)
                if winner == NEUTRAL:
                    io_h.send(t3e_r.render(major_grid))
                    break
            player = t3e_u.switch_player(player)
            turn += 1

            turn_m2.save(turn_m1.grid, turn_m1.player, turn_m1.r, turn_m1.c, turn_m1.loaded)
            turn_m1.save(turn_m0.grid, turn_m0.player, turn_m0.r, turn_m0.c, turn_m0.loaded)
            turn_m0.save(major_grid, player, r_coord, c_coord, False)

        except KeyboardInterrupt:
            io_h.send('INF "\n\nMenu:\n1. Revert turn\n2. Exit game\n3. Cancel"')
            io_h.send('REQ "Enter your choice (1/2/3): "')
            choice = int(io_h.get())
            if choice == 1:
                if turn_m2.loaded:
                    io_h.send('"\nCannot revert right now. Resuming game."')
                else:
                    major_grid = deepcopy(turn_m2.grid)
                    player = turn_m2.player
                    r_coord = turn_m2.r
                    c_coord = turn_m2.c
                    turn_m0.loaded = True
                    turn_m1.loaded = True
                    turn_m2.loaded = True
                    io_h.send('"\nContinuing from previous turn."')
            elif choice == 2:
                io_h.send('"\nGame ended."')
                io_h.send('END')
                exit()
            elif choice == 3:
                io_h.send('"\nResuming game."')
            else:
                io_h.send('"\nInvalid choice. Resuming game."')

    if winner != NEUTRAL:
        io_h.send('"\n\n{0} has won the game!"'.format(t3e_u.displayer(winner)))
    else:
        io_h.send('"Game is drawn!"')
    io_h.send('END')
    exit()

def play():
    io_h = io_handler()
    game_thread = threading.Thread(target = main, args = (io_h, None))
    game_thread.start()

    while game_thread.is_alive():
        intake = io_h.get().split('"')
        if intake[0].strip() == 'INF':
            print(intake[1])
        elif intake[0].strip() == 'REQ':
            try:
                io_h.send(input(intake[1]))
            except KeyboardInterrupt:
                io_h.send('KBI')
        elif intake[0].strip() == 'END':
            break
        else:
            print("An internal error occured.")

    input("Press enter to exit. ")
    exit()

if __name__ == '__main__':
    play()
