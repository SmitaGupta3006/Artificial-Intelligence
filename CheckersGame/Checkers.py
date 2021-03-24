import time
import random
from os import path
import sys
import operator
positions = {(0, 0): 'a8', (0, 1): 'b8', (0, 2): 'c8', (0, 3): 'd8', (0, 4): 'e8', (0, 5): 'f8', (0, 6): 'g8',
             (0, 7): 'h8',
             (1, 0): 'a7', (1, 1): 'b7', (1, 2): 'c7', (1, 3): 'd7', (1, 4): 'e7', (1, 5): 'f7', (1, 6): 'g7',
             (1, 7): 'h7',
             (2, 0): 'a6', (2, 1): 'b6', (2, 2): 'c6', (2, 3): 'd6', (2, 4): 'e6', (2, 5): 'f6', (2, 6): 'g6',
             (2, 7): 'h6',
             (3, 0): 'a5', (3, 1): 'b5', (3, 2): 'c5', (3, 3): 'd5', (3, 4): 'e5', (3, 5): 'f5', (3, 6): 'g5',
             (3, 7): 'h5',
             (4, 0): 'a4', (4, 1): 'b4', (4, 2): 'c4', (4, 3): 'd4', (4, 4): 'e4', (4, 5): 'f4', (4, 6): 'g4',
             (4, 7): 'h4',
             (5, 0): 'a3', (5, 1): 'b3', (5, 2): 'c3', (5, 3): 'd3', (5, 4): 'e3', (5, 5): 'f3', (5, 6): 'g3',
             (5, 7): 'h3',
             (6, 0): 'a2', (6, 1): 'b2', (6, 2): 'c2', (6, 3): 'd2', (6, 4): 'e2', (6, 5): 'f2', (6, 6): 'g2',
             (6, 7): 'h2',
             (7, 0): 'a1', (7, 1): 'b1', (7, 2): 'c1', (7, 3): 'd1', (7, 4): 'e1', (7, 5): 'f1', (7, 6): 'g1',
             (7, 7): 'h1'}


class Move:
    def __init__(self, rowStart=0, colStart=0, lastRow=0, lastCol=0, state=None, move=None):
        if move == None:
            self.lastRow = lastRow
            self.lastCol = lastCol
            self.firstRow = rowStart
            self.killedOppRow = []
            self.killedOppCol = []
            self.firstCol = colStart
            self.seenRowList = []
            self.seenColList = []
            self.rowStart = rowStart
            self.state = state
            self.colStart = colStart
            self.killedVisited = set()
        else:
            self.firstRow = move.firstRow
            self.killedOppRow = list(move.killedOppRow)
            self.colStart = move.colStart
            self.seenColList = list(move.seenColList)
            self.lastRow = move.lastRow
            self.killedVisited = set(move.killedVisited)
            self.lastCol = move.lastCol
            self.killedOppCol = list(move.killedOppCol)
            self.rowStart = move.rowStart
            self.firstCol = move.firstCol
            self.seenRowList = list(move.seenRowList)
            self.state = move.state


class CheckersGame:
    def __init__(self, game=None):
        self.board = []
        self.N = 8
        self.gameType = "SINGLE"
        if game != None:
            self.board = [[game.board[i][j] for j in range(self.N)] for i in range(self.N)]
            self.currPlayer = game.currPlayer
            self.timeLimit = game.timeLimit
        else:
            self.board = [[1111 for i in range(self.N)] for j in range(self.N)]
            self.currPlayer = 1
            self.timeLimit = 1

    def getDefaultBoard(self):
        return [[0 for i in range(self.N)] for j in range(self.N)]

    def new_game(self):
        self.board = self.getDefaultBoard()

        def assignValue(a, b):
            if (i & 1 ==1):
                self.board[i][j+1] = a
                self.board[i][j] = b
            else:
                self.board[i][j] = a
                self.board[i][j+1] =b

        for i in range(0, self.N):
            for j in range(0, self.N, 2):
                if i < 3:
                    assignValue(-1, 1)
                if i >=3 and i < 5:
                    assignValue(-1, 0)
                if i >=5 and i<self.N:
                    assignValue(-1, 2)


    def executeBoard(self, input):
        try:
            map = {'w': 2,
                   'W': 4,
                    'b': 1,
                   'B': 3,
                   '.': 0}
            self.board = self.getDefaultBoard()
            if input:
                f= open(input)
            else:
                f = open(r'input.txt')

            data = [line.strip() for line in f]
            self.gameType = data[0]
            self.maxPlayer = 1 if data[1] == "BLACK" else 2
            self.currPlayer = 1 if data[1] == "BLACK" else 2
            self.timeLimit = float(data[2])
            for i in range(self.N):
                b = data[3 + i]
                for j in range(0, self.N, 2):
                    flag = (i & 1 == 1)
                    self.board[i][j] = map[b[j]] if flag else -1
                    self.board[i][j+1] = -1 if flag else map[b[j + 1]]
        except:
            return False
        return True

    def findValidMoves(self, state):
        simpleMoves = []
        jumpMoves = []

        def _getMoves(i, j, check1):
            if (self.board[i][j] == check1 or self.board[i][j] == check1+2):
                self.findJumpMoves(jumpMoves, None, self.board[i][j], i, j, state)
                if len(jumpMoves) == 0:
                    self.findStrideMoves(simpleMoves, self.board[i][j], i, j, self.board)

        for i in range(0, self.N):
            for j in range(0,  self.N):
                flag = 1 if self.currPlayer == 1 else 2
                _getMoves(i, j, flag)

        if len(jumpMoves) != 0:
            return jumpMoves
        else:
            return simpleMoves

    def findStrideMoves(self, moves, pieceType, rowStart, colStart, state):
        lastRow = []
        lastCol = []

        def _appendI(flag, arr):
            for i in arr:
                if flag == 1:
                    lastRow.append(rowStart+ i)
                else:
                    lastCol.append(colStart + i)

        if pieceType == 1:
            _appendI(1, [1, 1])
            _appendI(2, [1,-1])
        elif pieceType == 2:
            _appendI(1, [-1, -1])
            _appendI(2, [1, -1])
        elif pieceType == 3 or pieceType == 4:
            _appendI(1, [1, 1, -1, -1])
            _appendI(2, [1, -1, 1, -1])


        for i in range(len(lastRow)):

            comp1= lastRow[i]
            comp2 = lastCol[i]
            if (comp1 < 0 or comp1 > 7 or comp2 < 0 or comp2 > 7 or state[comp1][comp2] != 0):
                continue

            m = Move(rowStart, colStart,comp1, comp2, state)
            moves.append(m)

    def findJumpMoves(self, moves, move, pieceType, rowStart, colStart, state):

        lastRow = []
        lastCol = []
        captureRow = []
        captureCol = []

        def _appendI(flag, arr1, arr2):
            for i in range(len(arr1)):
                if flag == 1:
                    lastRow.append(rowStart + arr1[i])
                    captureRow.append(rowStart + arr2[i])
                else:
                    lastCol.append(colStart + arr1[i])
                    captureCol.append(colStart + arr2[i])

        if (pieceType == 1):
            _appendI(1, [2, 2], [1, 1])
            _appendI(2, [-2, 2], [-1,1])

        elif (pieceType == 2):
            _appendI(1, [-2, -2], [-1, -1])
            _appendI(2, [-2, 2], [-1, 1])

        elif (pieceType == 3 or pieceType == 4):
            _appendI(1, [2, 2, -2, -2], [1, 1, -1, -1])
            _appendI(2, [-2, 2, -2, 2], [-1, 1, -1, 1])

        numMoves = len(lastRow)
        anyValidMoves = False
        whichAreValid = [False for i in range(numMoves)]

        for i in range(numMoves):
            comp1= lastRow[i]
            comp2 = lastCol[i]
            if (comp1 < 0 or comp1 > 7 or comp2 < 0 or comp2 > 7):
                continue

            if (move != None):

                if (state[comp1][comp2] != 0 and state[comp1][comp2] != state[move.firstRow][
                    move.firstCol]):
                    continue
                if (captureRow[i], captureCol[i]) in move.killedVisited:
                    continue

            else:
                if (state[comp1][comp2] != 0):
                    continue

            if (self.currPlayer == 1 and not (
                    state[captureRow[i]][captureCol[i]] == 2 or state[captureRow[i]][captureCol[i]] == 4)):
                continue

            if (self.currPlayer == 2 and not (
                    state[captureRow[i]][captureCol[i]] == 1 or state[captureRow[i]][captureCol[i]] == 3)):
                continue

            anyValidMoves = True
            whichAreValid[i] = True

        if (move != None and not anyValidMoves):
            moves.append(move)
            return

        if (move == None and anyValidMoves):
            for i in range(numMoves):
                comp11 = lastRow[i]
                comp22 =  lastCol[i]
                if (whichAreValid[i]):
                    newMove = Move(rowStart, colStart, comp11, comp22, state)
                    newMove.firstRow = rowStart
                    newMove.firstCol = colStart
                    newMove.rowStart = rowStart
                    newMove.colStart = colStart
                    newMove.lastRow = comp11
                    newMove.lastCol = comp22

                    newMove.killedOppRow.append(captureRow[i])
                    newMove.killedOppCol.append(captureCol[i])
                    newMove.seenRowList.append(comp11)
                    newMove.seenColList.append(comp22)
                    newMove.killedVisited.add((captureRow[i], captureCol[i]))
                    self.findJumpMoves(moves, newMove, pieceType, newMove.lastRow, newMove.lastCol, state)

        if (move != None and anyValidMoves):
            for i in range(numMoves):
                comp111= lastRow[i]
                comp222= lastCol[i]
                if (whichAreValid[i]):
                    newMove = Move(rowStart, colStart,comp111, comp222, state, move)
                    newMove.firstRow = move.firstRow
                    newMove.firstCol = move.firstCol
                    newMove.rowStart = rowStart
                    newMove.colStart = colStart
                    newMove.lastRow =comp111
                    newMove.lastCol = comp222
                    newMove.killedOppRow = list(move.killedOppRow)
                    newMove.killedOppCol = list(move.killedOppCol)
                    newMove.seenRowList = list(move.seenRowList)
                    newMove.seenColList = list(move.seenColList)
                    newMove.killedOppRow.append(captureRow[i])
                    newMove.killedOppCol.append(captureCol[i])
                    newMove.seenRowList.append(comp111)
                    newMove.seenColList.append(comp222)
                    newMove.killedVisited.add((captureRow[i], captureCol[i]))

                    self.findJumpMoves(moves, newMove, pieceType, newMove.lastRow, newMove.lastCol, state)
    def reversePlayer(self):
        if self.currPlayer ==1:
            self.currPlayer = 2
        else:
            self.currPlayer = 1

    def executeMove(self, move, state):
        if len(move.killedOppRow) > 0:
            for i in range(len(move.killedOppRow)):
                state[move.killedOppRow[i]][move.killedOppCol[i]] = 0
            initial_state = state[move.firstRow][move.firstCol]
            state[move.lastRow][move.lastCol] = initial_state
            if ((initial_state == 1 and move.lastRow == 7) or (initial_state == 2 and move.lastRow == 0)):
                state[move.lastRow][move.lastCol] += 2

            state[move.firstRow][move.firstCol] = 0
        else:
            currState = state[move.rowStart][move.colStart]
            state[move.lastRow][move.lastCol] = currState
            if ((currState == 1 and move.lastRow == 7) or (currState == 2 and move.lastRow == 0)):
                state[move.lastRow][move.lastCol] += 2
            state[move.rowStart][move.colStart] = 0


        self.reversePlayer()


class PlayGame:
    def __init__(self, maxPlayer, maxdepth, timeLimit=1):
        self.maxPlayer = maxPlayer
        self.maxDepth = maxdepth
        self.startTime = 0
        self.N = 8
        self.timeFactor = 1
        self.currentTime = 0
        self.outOfTime = False
        self.selfPieces = 0
        self.selfKings = 0
        self.enemyKings = 0
        self.enemyPieces = 0
        self.timeLimit = timeLimit

    def currentBoardStatus(self, game):

        def _getSamePlayer(flag):
            if game.board[i][j] == 1:
                if flag:
                    self.selfPieces += 1
                else:
                    self.enemyPieces +=1
            elif game.board[i][j] == 2:
                if flag:
                    self.enemyPieces += 1
                else:
                    self.selfPieces += 1
            elif game.board[i][j] == 3:
                if flag:
                    self.selfKings += 1
                else:
                    self.enemyKings += 1
            elif game.board[i][j] == 4:
                if flag:
                    self.enemyKings += 1
                else:
                    self.selfKings += 1
        for i in range(self.N):
            for j in range(self.N):
                if (self.maxPlayer == 1):
                    _getSamePlayer(1)
                else:
                    _getSamePlayer(0)

    def thresholdCheck(self, numMoves, depth):

        if numMoves == 0:
            return True

        if self.maxDepth == depth:
            return True

        return False

    def heuristic(self, game):
        boardVal = 0
        cntOppPieces = 0
        cntOppKings = 0
        cntAllyPieces = 0
        cntAllyKings = 0

        mapp = {"add": operator.add,
                "sub": operator.sub}

        def _assignWeight(i, j, a_and_s, factor, i_val):
            nonlocal boardVal
            boardVal = mapp[a_and_s](boardVal, factor)
            if (j == 0 or j == 7):
                boardVal =mapp[a_and_s](boardVal,  1)
            if (i == i_val):
                boardVal =mapp[a_and_s](boardVal,  4)

        for i in range(self.N):
            for j in range(self.N):
                if (self.maxPlayer == 1):
                    if (game.board[i][j] == 1):
                        factor = 6 + (i * 0.5)
                        _assignWeight(i, j, "add", factor, 0)
                        cntAllyPieces += 1
                    elif (game.board[i][j] == 2):
                        factor = 6 + ((7 - i) * 0.5)
                        _assignWeight(i, j, "sub", factor, 7)
                        cntOppPieces += 1
                    elif ((game.board[i][j] == 3)):
                        _assignWeight(i, j, "add", 10, 0)
                        cntAllyKings += 1
                    elif (game.board[i][j] == 4):
                        _assignWeight(i, j, "sub", 10, 7)
                        cntOppKings += 1
                else:
                    if (game.board[i][j] == 1):
                        factor = 6 + (i * 0.5)
                        _assignWeight(i, j, "sub", factor, 0)
                        cntOppPieces += 1

                    elif (game.board[i][j] == 2):
                        factor =  6 + ((7 - i) * 0.5)
                        _assignWeight(i, j, "add", factor, 7)
                        cntAllyPieces += 1

                    elif (game.board[i][j] == 3):
                        _assignWeight(i, j, "sub", 10, 0)
                        cntOppKings += 1

                    elif (game.board[i][j] == 4):
                        _assignWeight(i, j, "add", 10, 7)
                        cntAllyPieces += 1
        totalOppPieces = cntOppPieces + cntOppKings
        totalAllyPieces = cntAllyPieces + cntAllyKings
        if (totalOppPieces == 0 and totalAllyPieces > 0) or (totalAllyPieces == 0 and totalOppPieces > 0):
            boardVal = float('inf')

        boardVal += (cntAllyKings + cntAllyPieces) - (cntOppKings + cntOppPieces)
        return boardVal

    def setTime(self, minusFactor):
        self.currentTime = time.time()
        if (self.currentTime - self.startTime) >= (self.timeLimit * (self.timeFactor - minusFactor)):
            self.outOfTime = True
            return 0
        return 1


    def playChance(self, game, move, alpha, beta, depth, flag):
        copyGame = CheckersGame(game)
        copyGame.executeMove(move, copyGame.board)
        if flag :
            return self.minimizer(copyGame, alpha, beta, depth+1)
        else:
            return self.maximizer(copyGame, alpha, beta, depth+1)

    def minimizer(self, game, alpha, beta, depth):
        if not self.setTime(0.03):
            return 0

        listLegalMoves = game.findValidMoves(game.board)
        if (self.thresholdCheck(len(listLegalMoves), depth)):
            return self.heuristic(game)

        v = float('inf')

        for move in listLegalMoves:
            v = min(v, self.playChance(game, move, alpha, beta, depth, 0))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    def maximizer(self, game, alpha, beta, depth):
        if not self.setTime(0.05):
            return 0

        listLegalMoves = game.findValidMoves(game.board)
        if (self.thresholdCheck(len(listLegalMoves), depth)):
            calc = self.heuristic(game)
            return calc

        v = float('-inf')
        for move in listLegalMoves:
            v = max(v, self.playChance(game, move, alpha, beta, depth, 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def alphaBetaAlgo(self, game):
        self.startTime = time.time()
        self.currentBoardStatus(game)
        self.outOfTime = False
        bestMove = None
        maxDepthLimit = self.maxDepth
        legalMovesList = game.findValidMoves(game.board)
        if (len(legalMovesList) == 1):
            return legalMovesList[0]

        maxdepth = 0
        while (maxdepth < maxDepthLimit and not (self.outOfTime)):
            bestMoves = []
            bestVal = float('-inf')
            for move in legalMovesList:
                min =  self.playChance(game, move,  float('-inf'),  float('inf'), 0, 0)

                if min > bestVal:
                    bestMoves.clear()
                    bestMoves.append(move)
                    bestVal = min
                elif min == bestVal:
                    bestMoves.append(move)

                if bestVal == float('inf') or self.outOfTime:
                    break

            chosenMove = 0
            if (len(bestMoves) > 1):
                chosenMove = random.randint(0, (len(bestMoves) - 1))

            bestMove = bestMoves[chosenMove]
            bestMoveVal = bestVal

            if bestMoveVal == float('inf'):
                break
            maxdepth += 1

        if (bestMove == None and len(legalMovesList) != 0):
            bestMove = legalMovesList[0]

        return bestMove




def findMaxDepth(start_time, time_remaining, master_time):

    time_remaining = time_remaining - (time.time() - start_time)
    if (master_time > 0):
        percentage = (time_remaining / master_time) * 100
        if percentage > 10:
            depth = 6
            tl = master_time * 0.85 / 100
        elif percentage > 1:
            depth = 3
            tl = master_time * 0.15 / 100
        else:
            depth = 1
            tl = (master_time*percentage*0.12)/100

        return depth, tl


class Main:

    def __init__(self):
        self.p = None

    def writeOutput(self, move):
        if len(move.killedOppRow) == 0:
            start = (move.rowStart, move.colStart)
            end = (move.lastRow, move.lastCol)
            s = "E" + " " + positions[start] + " " + positions[end]

        else:
            start = (move.firstRow, move.firstCol)
            end = (move.seenRowList[0], move.seenColList[0])
            s = "J" + " " + positions[start] + " " + positions[end] + "\n"

            for j in range(1, len(move.seenRowList)):
                start = (move.seenRowList[j - 1], move.seenColList[j - 1])
                end = (move.seenRowList[j], move.seenColList[j])
                s += "J" + " " + positions[start] + " " + positions[end] + "\n"

        fc = open(r"output.txt", 'w')
        fc.write(s)
        fc.close()

    def startGame(self, input = None):

        obj_game = CheckersGame()

        start_time = time.time()
        P1 = PlayGame(1, 5)
        P2 = PlayGame(2, 5)

        if not obj_game.executeBoard(input):
            obj_game.new_game()

        P1.timeLimit = obj_game.timeLimit
        P2.timeLimit = obj_game.timeLimit


        if (obj_game.gameType == "SINGLE"):
            mlist = obj_game.findValidMoves(obj_game.board)
            move = mlist[0]
            self.writeOutput(move)

        elif (obj_game.gameType == "GAME"):
            play_time = obj_game.timeLimit * 0.98
            if not path.exists(r"playdata.txt"):
                master_time = play_time
                f = open(r"playdata.txt", 'w')
                result = '0\n' + str(master_time)
                f.write(str(result))
                f.close()
            else:
                f = open(r"playdata.txt", 'r')
                f.readline().rstrip()
                master_time = float(f.readline().rstrip())
                f.close()

            if (obj_game.currPlayer == 1):
                d, t = findMaxDepth(start_time, play_time, master_time)
                P1.maxDepth = d
                P1.timeLimit = t
                move = P1.alphaBetaAlgo(obj_game)
                self.writeOutput(move)

            elif (obj_game.currPlayer == 2):
                d, t = findMaxDepth(start_time, play_time, master_time)
                P2.maxDepth = d
                P2.timeLimit = t
                move = P2.alphaBetaAlgo(obj_game)
                self.writeOutput(move)


if __name__ == "__main__":
    arg1 = None
    if len(sys.argv) > 1:
        arg1 = sys.argv[1]
    obj = Main()
    obj.startGame(arg1)
