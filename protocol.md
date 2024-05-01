# Protocol

## On connection

### You

PL:<name> - Give your player name

### Server

ER:<error> - Error and disconnected

## Game start

### Server

AK:<player name> - Acknowledge and start game
TU: - Turn to play
BO:<moves> - The board with 0, 1, 2 (0: nothing, 1: you, 2: other player)
ER:<error> - Error (not your turn or impossible move)

### You

MV:<move> -
BA: - Ask for the board
RQ: - Rage quit

## Game end

### Server

GE:<int> - 0: tie, 1: you win, 2: you loose

### You

RP: - replay
QU: - quit
