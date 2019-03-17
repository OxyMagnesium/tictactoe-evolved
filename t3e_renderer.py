#Logic for rendering both the primary and secondary grids.

import t3e_resources as t3e_u

NEUTRAL = 20
X = 1
O = 5

'''
 0 0 0 | 0 0 0 | 0 0 0
 0 0 0 | 0 0 0 | 0 0 0
 0 0 0 | 0 0 0 | 0 0 0
-------|-------|-------
 0 0 0 | 0 0 0 | 0 0 0
 0 0 0 | 0 0 0 | 0 0 0
 0 0 0 | 0 0 0 | 0 0 0
-------|-------|-------
 0 0 0 | 0 0 0 | 0 0 0
 0 0 0 | 0 0 0 | 0 0 0
 0 0 0 | 0 0 0 | 0 0 0
'''

def render_line(grid, m_row, s_row):
    line = ' '
    for i in range(3):
        if grid[m_row][i].owner:
            if s_row == 1:
                line += '  {0}   '.format(t3e_u.displayer(grid[m_row][i].owner))
            else:
                line += '      '
        else:
            for j in range(3):
                line += '{0} '.format(t3e_u.displayer(grid[m_row][i].contents[s_row][j]))

        line += '| '
    return line[:-2]

def render_divider():
    return '-------|-------|-------'

def render(grid):
    output = '\n'
    for i in range(3):
        for j in range(3):
            output += render_line(grid, i, j) + '\n'
        output += render_divider() + '\n'
    return output[:-25]
