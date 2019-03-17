# TicTacToe Evolved

Simple yet engaging command line based game featuring player vs. player and player vs. computer play. 

## How to play:
* The grids are labelled starting from the top left as below.
```
       1       2       3
     1 2 3
   1 - - - | - - - | - - -
1  2 - - - | - - - | - - -
   3 - - - | - - - | - - -
    -------|-------|-------
     - - - | - - - | - - -
2    - - - | - - - | - - -
     - - - | - - - | - - -
    -------|-------|-------
     - - - | - - - | - - -
3    - - - | - - - | - - -
     - - - | - - - | - - -
```
* The first player starts in the center grid, denoted (2, 2). They can choose any cell in the center grid to move in. For example, let's say they move in cell (1, 1). The grid becomes as follows:
```
       1       2       3
     1 2 3
   1 - - - | - - - | - - -
1  2 - - - | - - - | - - -
   3 - - - | - - - | - - -
    -------|-------|-------
     - - - | X - - | - - - 
2    - - - | - - - | - - -
     - - - | - - - | - - -
    -------|-------|-------
     - - - | - - - | - - -
3    - - - | - - - | - - -
     - - - | - - - | - - -
```
* Now, the second player can move in any cell of the grid corresponding to the cell in which the previous player moved. In this case, player 2 gets to move anywhere in grid (1, 1). 
```
       1       2       3
     1 2 3
   1 - - - | - - - | - - -
1  2 - - O | - - - | - - -
   3 - - - | - - - | - - -
    -------|-------|-------
     - - - | X - - | - - -
2    - - - | - - - | - - -
     - - - | - - - | - - -
    -------|-------|-------
     - - - | - - - | - - -
3    - - - | - - - | - - -
     - - - | - - - | - - -
```
* Here, player 2 moved in cell (2, 3). So, player 1 now has to move in grid (2, 3).
```
       1       2       3
     1 2 3
   1 - - - | - - - | - - -
1  2 - - O | - - - | - - -
   3 - - - | - - - | - - -
    -------|-------|-------
     - - - | X - - | - - -
2    - - - | - - - | - - -
     - - - | - - - | X - -
    -------|-------|-------
     - - - | - - - | - - -
3    - - - | - - - | - - -
     - - - | - - - | - - -
```
* And so on...

################################################################################
* When any player gets a row of three in any grid, they become the owner of that grid.
```
       1       2       3
     1 2 3
   1 - - - | - - O | - - -
1  2 - O O | - - - | - - -
   3 - - - | - - - | - X -
    -------|-------|-------
     X - - | X X - | - - -
2    - - - | - - - | - - -
     - - - | - - - | X - -
    -------|-------|-------
     - - - | - - - | - - -
3    - O - | - - - | O - -
     - - - | - - X | - - -
```
```
       1       2       3
     1 2 3
   1 - - - | - - O | - - -
1  2 - O O | - - - | - - -
   3 - - - | - - - | - X -
    -------|-------|-------
     X - - |       | - - -
2    - - - |   X   | - - -
     - - - |       | X - -
    -------|-------|-------
     - - - | - - - | - - -
3    - O - | - - - | O - -
     - - - | - - X | - - -
```
* Upon winning a grid, the standard movement rules still apply. In the above case, O will have to move in grid (1, 3). However, if a player is supposed to move in a grid that has already been owned by anyone, they get to go in any available grid of their choice. For example, if O goes in cell (2, 2) of grid (1, 3) in the above case: 
```
       1       2       3
     1 2 3
   1 - - - | - - O | - - -
1  2 - O O | - - - | - O -
   3 - - - | - - - | - X -
    -------|-------|-------
     X - - |       | - - -
2    - - - |   X   | - - -
     - - - |       | X - -
    -------|-------|-------
     - - - | - - - | - - -
3    - O - | - - - | O - -
     - - - | - - X | - - -
```
* X now has the ability to go in any grid of their choice.
```
       1       2       3
     1 2 3
   1 - - - | - - O | - - -
1  2 - O O | - - - | - O -
   3 - - - | - - - | - X -
    -------|-------|-------
     X - - |       | - - -
2  > - - - |   X   | - X -
     - - - |       | X - -
    -------|-------|-------
     - - - | - - - | - - -
3    - O - | - - - | O - -
     - - - | - - X | - - -
                       ^
```
*  Ownership of the grid is irrelevant in this regard, because even if O lands on grid (2, 2) now, they can pick any grid to move in.
```
       1       2       3
     1 2 3
   1 - - - | - - O | - - -
1  2 - O O | - - - | - O -
   3 - - - | - - - | - X -
    -------|-------|-------
     X - - |       | - - -
2    - - - |   X   | - X -
     - - - |       | X - -
    -------|-------|-------
   > - - O | - - - | - - -
3    - O - | - - - | O - -
     - - - | - - X | - - -
         ^
```
################################################################################
* In order to win, a player must own 3 grids in a row on the major grid. For example, O has won in the case below:
```
       |       |
   X   |   O   |   X
       |       |
-------|-------|-------
 O - - |       | O X -
 O O X |   O   | O - O
 - X X |       | - - -
-------|-------|-------
       |       | O - -
   X   |   O   | X - X
       |       | O X O
```
* You can play against the computer at 4 levels of difficulty, ranging from easy to beat to pretty darn hard to win against, even for me. Level 4 can also take a _lot_ of time to compute moves, so don't play against it on a potato. Good luck and have fun!
