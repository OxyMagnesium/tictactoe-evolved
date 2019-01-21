
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

def displayer(i):
    if i == X:
        return 'X'
    elif i == O:
        return 'O'
    elif i == 0:
        return '-'

def render_line(grid, m_row, s_row):
    line = ' '
    for i in range(3):
        try:
            for j in range(3):
                line += '{0} '.format(displayer(grid[m_row][i].contents[s_row][j]))
        except AttributeError:
            if s_row == 1:
                line += '  {0}   '.format(displayer(grid[m_row][i]))
            else:
                line += '      '
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
