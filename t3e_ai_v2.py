from random import choice
from time import time
from math import exp
import numpy as np

import t3e_resources as gl

inf = np.inf
debug = False
log = True

indices = [(i, j) for j in range(3) for i in range(3)]

################################################################################

# Returns a sorted list of the evaluations of all possible moves in {loc}.
def calc_base_scores(m_grid, loc, mode, player):
    scores = [evaluate_move(m_grid, loc, mode, player, index)
              for index in indices if not get_cont(m_grid, loc, index)]
    scores.sort(key = lambda x: x[1])
    return scores

# Updates the threat values stored in the given grid.
def update_threats(m_grid, loc, threats, player):
    opponent = gl.switch_player(player)
    if loc == None:
        grid = m_grid
    else:
        grid = m_grid.get_obj(loc)
    grid.threats[player] += threats[0]
    grid.threats[opponent] -= threats[1]

# Returns the highest value from the given grid.
def get_max_score(scores):
    return max(max(row) for row in scores)

# Returns the location of the maximum value in the given grid.
def get_max_score_loc(scores):
    max = get_max_score(scores)
    return choice([index for index in indices if scores[index] == max])

# Faster implementation of m_grid.get_threats
def get_threats(m_grid, loc = None, player = None):
    if loc:
        if player:
            return m_grid.contents[loc[0]][loc[1]].threats[player]
        else:
            return m_grid.contents[loc[0]][loc[1]].threats
    else:
        return m_grid.threats[player] if player else m_grid.threats

# Faster implementation of m_grid.get_contents
def get_cont(m_grid, loc = None, cell = None):
    if loc:
        if cell:
            return m_grid.contents[loc[0]][loc[1]].contents[cell[0]][cell[1]]
        else:
            return m_grid.contents[loc[0]][loc[1]].contents
    else:
        return [[s_grid.owner for s_grid in row] for row in m_grid.contents]

################################################################################

# Returns the threat evaluation score of the {move} cell in the {loc} grid.
def evaluate_move(m_grid, loc, mode, player, move):
    # Initialize variables.
    grid_cont = get_cont(m_grid, loc)
    opponent = gl.switch_player(player)
    using_d1 = (move[0] == move[1])
    using_d2 = (move[0] + move[1] == 2)

    # Compute file sums (doing this every time is somehow cheaper than keeping
    # and updating a table of sums, don't know how).
    row_sum = 0
    col_sum = 0
    d1_sum = 0
    d2_sum = 0
    for i in range(3):
        row_sum += grid_cont[move[0]][i]
        col_sum += grid_cont[i][move[1]]
    if using_d1:
        for i in range(3):
            d1_sum += grid_cont[i][i]
    if using_d2:
        for i in range(3):
            d2_sum += grid_cont[2 - i][i]

    # If this move captures the grid, no need to check any further.
    if 2*player in (row_sum, col_sum, d1_sum, d2_sum):
        score = 200
        if loc and mode >= 3:
            score += 10*get_threats(m_grid, loc, opponent)
        return (move, score, (0, 0), True)

    # Initialize accumulators.
    delta_friend_threats = 0
    delta_foe_threats = 0
    score = 0

    # Diagonals (and the centre cell) are slightly more valuable.
    if move[0] == move[1]:
        score += 1
    if move[0] + move[1] == 2:
        score += 1


    # If the move row previously only had a friendly occupied cell, then a new
    # friendly threat is being created.
    if row_sum == player:
        delta_friend_threats += 1
        score += 5

        # Find the column in this row which will be empty after the move. If the
        # cell so obtained corresponds to the active grid, an occupied grid, or
        # a grid that has foe threats in it, this threat isn't as strong. If
        # evaluating at board level and the threat subgrid already has a
        # friendly threat, then this is a very good capture.
        if mode >= 3:
            for i in range(3):
                if grid_cont[move[0]][i] == 0 and i != move[1]:
                    empty_col = i
                    break
            threat_cell = (move[0], empty_col)
            if not loc:
                score += 15*get_threats(m_grid, threat_cell, player)
            elif threat_cell == loc or m_grid.get_owner(threat_cell):
                score -= 10
            else:
                tgt_foe_threats = get_threats(m_grid, threat_cell, opponent)
                score -= 5*tgt_foe_threats if tgt_foe_threats <= 2 else 10

    # If the move row previously had two foe occupied cells, then a foe threat
    # is being eliminated.
    elif row_sum == 2*opponent:
        delta_foe_threats += 1
        score += 5


    # If the move col previously only had a friendly occupied cell, then a new
    # friendly threat is being created.
    if col_sum == player:
        delta_friend_threats += 1
        score += 5

        # Find the row in this column which will be empty after the move. If the
        # cell so obtained corresponds to the active grid, an occupied grid, or
        # a grid that has foe threats in it, this threat isn't as strong. If
        # evaluating at board level and the threat subgrid already has a
        # friendly threat, then this is a very good capture.
        if mode >= 3:
            for i in range(3):
                if grid_cont[i][move[1]] == 0 and i != move[0]:
                    empty_row = i
                    break
            threat_cell = (empty_row, move[1])
            if not loc:
                score += 15*get_threats(m_grid, threat_cell, player)
            elif threat_cell == loc or m_grid.get_owner(threat_cell):
                score -= 10
            else:
                tgt_foe_threats = get_threats(m_grid, threat_cell, opponent)
                score -= 5*tgt_foe_threats if tgt_foe_threats <= 2 else 10

    # If the move col previously had two foe occupied cells, then a foe threat
    # is being eliminated.
    elif col_sum == 2*opponent:
        delta_foe_threats += 1
        score += 5


    # If the move indices are equal, then d1 must be checked.
    if using_d1:
        # If diagonal 1 previously only had a friendly occupied cell, then a
        # new friendly threat is being created.
        if d1_sum == player:
            delta_friend_threats += 1
            score += 5

            # Cross diagonal threats are almost never good compared to others
            # as they are easy to eliminate and hard to follow through on.
            if move != (1, 1) and mode >= 2:
                score -= 2

            # Find the cell in diag 1 which will be empty after the move. If the
            # cell so obtained corresponds to the active grid, an occupied grid,
            # or a grid that has foe threats in it, this threat isn't as strong.
            # If evaluating at board level and the threat subgrid already has a
            # friendly threat, then this is a very good capture.
            if mode >= 3:
                for i in range(3):
                    if grid_cont[i][i] == 0 and i != move[0]:
                        empty_d1 = i
                        break
                threat_cell = (empty_d1, empty_d1)
                if not loc:
                    score += 15*get_threats(m_grid, threat_cell, player)
                elif threat_cell == loc or m_grid.get_owner(threat_cell):
                    score -= 10
                else:
                    tgt_foe_threats = get_threats(m_grid, threat_cell, opponent)
                    score -= 5*tgt_foe_threats if tgt_foe_threats <= 2 else 10

        # If diagonal 1 previously had two foe occupied cells, then a foe threat
        # is being removed.
        elif d1_sum == 2*opponent:
            delta_foe_threats += 1
            score += 5


    # If the move indices add up to 2, then d2 must be checked.
    if using_d2:
        # If diagonal 2 previously only had a friendly occupied cell, then a
        # new friendly threat is being created.
        if d2_sum == player:
            delta_friend_threats += 1
            score += 5

            # Cross diagonal threats are almost never good compared to others
            # as they are easy to eliminate and hard to follow through on.
            if move != (1, 1) and mode >= 2:
                score -= 2

            # Find the cell in diag 2 which will be empty after the move. If the
            # cell so obtained corresponds to the active grid, an occupied grid,
            # or a grid that has foe threats in it, this threat isn't as strong.
            # If evaluating at board level and the threat subgrid already has a
            # friendly threat, then this is a very good capture.
            if mode >= 3:
                for i in range(3):
                    if grid_cont[2 - i][i] == 0 and i != move[1]:
                        empty_d2 = i
                        break
                threat_cell = (2 - empty_d2, empty_d2)
                if not loc:
                    score += 15*get_threats(m_grid, threat_cell, player)
                elif threat_cell == loc or m_grid.get_owner(threat_cell):
                    score -= 10
                else:
                    tgt_foe_threats = get_threats(m_grid, threat_cell, opponent)
                    score -= 5*tgt_foe_threats if tgt_foe_threats <= 2 else 10

        # If diagonal 2 previously had two foe occupied cells, then a foe threat
        # is being removed.
        elif d2_sum == 2*opponent:
            delta_foe_threats += 1
            score += 5


    # If friendly threats went up from 0 or foe threats went down to 0, add
    # some bonus points to the score tally.
    if delta_friend_threats:
        if not get_threats(m_grid, loc, player):
            score += 15
    if delta_foe_threats:
        if get_threats(m_grid, loc, opponent) - delta_foe_threats == 0:
            score += 15


    # If a threat is being created and there is an opponent owned cell in
    # the same file as the cell under consideration, then creating a threat
    # here is better relative to other cells in this grid as it'll be harder
    # for the opponent to remove this threat while  keeping an advantage.
    if delta_friend_threats and mode >= 2:
        if row_sum == opponent:
            score += 2
        if col_sum == opponent:
            score += 2
        if d1_sum == opponent:
            score += 2
        if d2_sum == opponent:
            score += 2


    # Return the calculated values.
    return (move, score, (delta_friend_threats, delta_foe_threats), False)

################################################################################

def scan_board(m_grid, loc, mode, player, iters, p_base, p_max, r_all = False):
    # Go though all the unoccupied grids and obtain the maximum base score in
    # each. Create a priority queue on the basis of the highest base scores.
    queue = [(index, calc_base_scores(m_grid, index, mode, player).pop())
             for index in indices if not m_grid.get_owner(index)]
    queue.sort(key = lambda x: x[1][1])

    # If at this point the queue is empty, there are no unoccupied subgrids left
    # and the game must be drawn, so just return 0.
    if not queue:
        return 0

    # Reduce the number of iterations sharply if required.
    drop_size = 2*len(queue)//3
    iters = iters if iters < drop_size else iters - drop_size

    # If this is the final iteration, then just return the highest base score.
    if not iters:
        return queue.pop()[1][1]

    # If r_all is set, create a grid to keep track of the scores.
    if r_all:
        scores = [[-inf*np.ones((3, 3)) for _ in range(3)] for _ in range(3)]
        maxima = -inf*np.ones((3, 3))
    else:
        max_score = -inf

    # Iterate through each location in the queue and obtain the maximum path
    # score (or the entire score grid if r_all is set) for that location.
    while queue:
        loc = queue.pop()[0]
        if r_all:
            scores[loc[0]][loc[1]] = scan_paths(m_grid, loc, mode, player,
                                                iters, -inf, -inf, True)[1]
            maxima[loc[0]][loc[1]] = get_max_score(scores[loc[0]][loc[1]])
        else:
            grid_score = scan_paths(m_grid, loc, mode, player,
                                    iters, p_base, p_max)
            if grid_score > max_score:
                max_score = grid_score
            if p_base - max_score < p_max and pruning_active:
                return max_score

    # Return the required value.
    if r_all:
        max_score_loc = get_max_score_loc(maxima)
        return (max_score_loc, scores[max_score_loc[0]][max_score_loc[1]])
    else:
        if max_score == -inf:
            return 0
        else:
            return max_score


def scan_paths(m_grid, loc, mode, player, iters, p_base, p_max, r_all = False):
    if not m_grid.get_owner(loc):
        # If r_all is set, create a grid to keep track of the scores.
        if r_all:
            final_scores = -inf*np.ones((3, 3))

        # Initialize variables and obtain base scores for all possible moves.
        max_score = -inf
        opponent = gl.switch_player(player)
        move_evals = calc_base_scores(m_grid, loc, mode, player)
        board_eval = evaluate_move(m_grid, None, mode, player, loc)
        opp_board_eval = evaluate_move(m_grid, None, mode, opponent, loc)
        while move_evals:
            # The last element of base_evals is the move with the highest score.
            mv_eval = move_evals.pop()
            mv_pos = mv_eval[0]
            mv_score = mv_eval[1]
            delta_threats = mv_eval[2]
            move_caps_grid = mv_eval[3]

            # Add extra points on the basis of the move's impact on the board.
            if delta_threats[0]:
                mv_score += board_eval[1]
            if delta_threats[1]:
                mv_score += opp_board_eval[1]

            # If the active subgrid was captured, check for a win. If a win
            # is indeed occuring by moving here, just return a very high value.
            # Also add points proportional to the amount of iterations still
            # available to incentivize the AI to try and win in fewer moves.
            if move_caps_grid:
                mv_score += 20*board_eval[1]
                if board_eval[3]:
                    if r_all:
                        final_scores[mv_pos[0]][mv_pos[1]] = 10000
                        final_scores[mv_pos[0]][mv_pos[1]] += 1000*iters
                        return (loc, final_scores)
                    else:
                        return 10000 + 1000*iters

            # If iterations are still left, create a copy of the board, make
            # the move under consideration in that copy, and then recursively
            # scan from the opponent's perspective in the grid they end up in.
            if iters > 0 and time() - start_time < time_limit and not stop():
                new_iters = iters - 1
                m_grid_copy = gl.major_grid(m_grid)
                focus_grid = m_grid_copy.get_obj(loc)
                focus_grid.update_cell(mv_pos, player, move_caps_grid)
                update_threats(m_grid_copy, loc, delta_threats, player)
                if move_caps_grid:
                    update_threats(m_grid_copy, None, board_eval[2], player)
                else:
                    new_iters -= 2 if new_iters >= 2 else 0
                mv_score -= scan_paths(m_grid_copy, mv_pos, mode, opponent,
                                       new_iters, mv_score, max_score)

            # Record the score of this move if required.
            if r_all:
                final_scores[mv_pos[0]][mv_pos[1]] = mv_score

            # Update the maximum score of this subgrid if required.
            if mv_score > max_score:
                max_score = mv_score

            # If the score of this move is high enough to cause the score of
            # this path in the parent subgrid to go below the highest score,
            # then this score can be returned without checking any further.
            if p_base - max_score < p_max and pruning_active:
                return max_score

        # Return the required value.
        if r_all:
            return (loc, final_scores)
        else:
            if max_score == -inf:
                return 0
            else:
                return max_score

    else:
        # If the active subgrid is occupied, get the result by scanning the full
        # board instead. Note that r_all cannot be set if this is the case.
        return scan_board(m_grid, loc, mode, player, iters, p_base, p_max)


def compute_move_v2(m_grid, loc, mode, player, turn, r_bin, kill_flag):
    # Calculate the number of iterations to perform.
    owned = 81
    for s_grid in ((i, j) for j in range(3) for i in range(3)):
        if not m_grid.get_owner(s_grid):
            owned -= sum(row.count(0) for row in get_cont(m_grid, s_grid))
    iters = 1
    if mode == 1: # Easy
        iters += 2 + 2*int(owned/54)
    elif mode == 2: # Medium
        iters += 8 + 2*int(owned/27)
    elif mode == 3: # Hard
        iters += 14 + 2*int(owned/(81 - owned))
    elif mode == 4: # Debug
        iters += 14 # + 2*round(0.5*owned/(81 - owned)) # - 5.6/(1 + owned))
    else:
        raise ValueError(f'{mode} is not a valid mode for t3eAIv2.')

    # Get the time at which this computation was started. Define an execution
    # time limit after which the algorithm will return whatever its calculated.
    global start_time
    global time_limit
    start_time = time()
    time_limit = 30

    # Set pruning mode (for debugging).
    global pruning_active
    pruning_active = not debug

    # Make the thread kill flag global.
    global stop
    stop = kill_flag

    # Obtain the location and corresponding score grid of the optimal move.
    if not m_grid.get_owner(loc):
        result = scan_paths(m_grid, loc, mode, player, iters, -inf, -inf, True)
    else:
        result = scan_board(m_grid, loc, mode, player, iters, -inf, -inf, True)

    # Put required values in the return bin.
    r_bin.append((result[0], get_max_score_loc(result[1])))
    r_bin.append(result[1])

    # Show whole score grid if debug flag is set.
    if debug:
        print(result[1])
