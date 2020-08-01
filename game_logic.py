import copy
import os
import time
import tkinter as tk
from tkinter.ttk import Style, Button

class Game:
    def makeMove(self, turn):
        raise NotImplementedError

    def play(self):
        raise NotImplementedError


class Point:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value

    def __repr__(self):
        return "{}:{}:{}".format(self.x, self.y, self.value)


class PentagoGame(Game):
    WIDTH, HEIGHT, MAXPOINT, MINPOINT = (6, 6, 100, -100)

    def __init__(self, color, oppColor, depth):
        self.color, self.oppColor, self.depth = color, oppColor, depth
        self.sectionBoard, self.mainBoard = self.makeBoard()

    def makeBoard(self):
        sectionBoard = [[[0]*3, [0]*3, [0]*3], [[0]*3, [0]*3, [0]*3],
                        [[0]*3, [0]*3, [0]*3], [[0]*3, [0]*3, [0]*3]]
        mainBoard = [[Point(j, k, -1) for k in range(PentagoGame.HEIGHT)]
                     for j in range(PentagoGame.WIDTH)]
        # mainBoard[0][1].value = 1

        for k in range(4):
            for i in range(3):
                for j in range(3):
                    sectionBoard[k][i][j] = Point(i, j, -1)

        return (sectionBoard, mainBoard)

    def printBoard(self, board=None):
        board_printed = self.mainBoard
        if board:
            board_printed = board

        for i in range(6):
            print(board_printed[i])

    def isMoveValid(self, point: Point):
        if point.x < PentagoGame.WIDTH and \
                point.y < PentagoGame.HEIGHT:
            return True
        return False

    def getValidMoves(self, board, trun):
        moves = []
        for i in range(PentagoGame.WIDTH):
            for j in range(PentagoGame.HEIGHT):
                if board[i][j].value == -1:
                    moves.append(board[i][j])

        return moves

    def __shawllowCopy(self, srcBoard, copyBoard):
        for index in range(0, 6):
            for j in range(PentagoGame.HEIGHT):
                copyBoard[index][j] = Point(index, j, srcBoard[index][j].value)

    def __tiwstBlocks(self, board):
        def tiwster(board, row_start_index, row_last_index, col_start_index, col_last_index):
            temp_board_anti_clockwise = [
                [0 for i in range(6)] for k in range(6)]
            temp_board_clockwise = [[0 for i in range(6)] for k in range(6)]
            self.__shawllowCopy(board, temp_board_anti_clockwise)
            self.__shawllowCopy(board, temp_board_clockwise)
            index = row_last_index - 1
            # making clock board
            for i in range(row_start_index, row_last_index):
                for j in range(col_start_index, col_last_index):
                    temp_board_anti_clockwise[index -
                                              j][i].value = board[i][j].value
            # making anticlock wise board
            for i in range(row_start_index, row_last_index):
                for j in range(col_start_index, col_last_index):
                    temp_board_clockwise[j][index].value = board[i][j].value
                index -= 1

            return [temp_board_anti_clockwise, temp_board_clockwise]

        boards = []
        for i in [3, PentagoGame.WIDTH]:
            for j in [3, PentagoGame.HEIGHT]:
                temp = tiwster(copy.copy(board), i - 3, i, j - 3, j)
                boards.extend(temp[:])
                
        return boards

    def makeMove(self, turn):
        if turn == self.color:
            best_move, rotate_index = self.__minimaxDecision()
            self.mainBoard = self.__tiwstBlocks(self.mainBoard)[rotate_index]
            self.mainBoard[best_move.x][best_move.y] = Point(
                best_move.x, best_move.y, self.color)
        else:
            x = int(input("insert x value: "))
            y = int(input("insert y value: "))
            rotate = int(input("rotate the board: "))
            board = self.__tiwstBlocks(self.mainBoard)[rotate]
            point = Point(x, y, self.oppColor)
            if self.isMoveValid(point):
                board[x][y] = point
                self.mainBoard = board
                # self.__shawllowCopy(self.mainBoard, board);
            else:
                print("your move is not valid~~~~")
                
                
    def play(self):
        boardFrame = BoardFrame(tk.Tk(), board=self.mainBoard)
        while True:
            if self.__gameOver():
                print("gameOver")
                break
            self.makeMove(self.color)
            self.printBoard()
            boardFrame.board = self.mainBoard
            boardFrame.draw_board()
            print("computer move")
            self.makeMove(self.oppColor)
            boardFrame.board = self.mainBoard
            boardFrame.draw_board()
            
            print("my move")
            # time.sleep(0.5)
        boardFrame.mainloop()
        if self.noMoveLeft(self.mainBoard):
            print("tie")
        else:
            score = self.__score(mainBoard, self.color)
            if score == PentagoGame.MAXPOINT:
                print("your the winner!!!!")
            else:
                print("Computer is winner")

    def newBoard(self):
        return [[Point(j, k, -1) for k in range(PentagoGame.HEIGHT)]
                for j in range(PentagoGame.WIDTH)]

    def __minimaxDecision(self):
        moves = self.getValidMoves(self.mainBoard, self.color)
        # rotate_angle = None
        if len(moves) == 0:
            return False, None
        else:
            best_value = float('-inf')
            best_move = moves[0]
            for move in moves:
                temp_board = self.newBoard()
                self.__shawllowCopy(self.mainBoard, temp_board)
                temp_board[move.x][move.y] = Point(move.x, move.y, move.value)
                predicted_value, index = self.__minimaxValue(
                    temp_board, self.color, self.oppColor, 1
                )
                if predicted_value >= best_value:
                    best_value = predicted_value
                    best_move = move
                    best_twist_block = index

            return (best_move, index)

    def __minimaxValue(self, board, turn, opp, depth):
        points = self.__score(board, turn)
        if depth == self.depth or self.noMoveLeft(board):
            return (points, None)

        if PentagoGame.MAXPOINT == points:
            return (PentagoGame.MAXPOINT, None)
        if PentagoGame.MINPOINT == points:
            return (PentagoGame.MINPOINT, None)

        moves = self.getValidMoves(board, turn)
        if len(moves) == 0:
            return (self.__minimaxValue(board, opp, turn, depth + 1), None)
        else:
            best_value = float('-inf') if turn == self.color else float('+inf')
            block_twist_number = 0
            best_move = moves[0]
            for i in moves:
                board[i.x][i.y] = Point(i.x, i.y, i.value)
                temp_boards = self.__tiwstBlocks(board)
                # make Twisted blocks
                for index, twisted_boards in enumerate(temp_boards):
                    # make move
                    predicted_value = self.__minimaxValue(
                        temp_boards[0], opp, turn, depth + 1
                    )

                    if turn == self.color:
                        if predicted_value[0] >= best_value:
                            best_value = predicted_value[0]
                            block_twist_number = index
                    else:
                        if predicted_value[0] < best_value:
                            best_value = predicted_value[0]
                            block_twist_number = index
                        
            return (best_value, block_twist_number)

    def noMoveLeft(self, board):
        for i in board:
            for j in i:
                if j.value == -1:
                    return False
        return True

    # so fucking bad logic :///////
    def winnerWinnerChickenDinner(self, board, turn, point: Point):
        counter, point_temp = 0, Point(point.x, point.y, point.value)

        for i in range(5):
            point_temp.x = point.x + i
            if self.isMoveValid(point_temp) and board[point.x + i][point.y] == turn:
                counter += 1
        if counter == 5:
            return True

        counter = 0
        for i in range(5):
            point_temp.y = point.y + i
            if self.isMoveValid(point_temp) and board[point.x][point.y + i] == turn:
                counter += 1
        if counter == 5:
            return True

        counter = 0
        for i in range(5):
            point_temp.x, point_temp.y = point.x + i, point.y + i
            if self.isMoveValid(point_temp) and board[point.x + i][point.y + i] == turn:
                counter += 1
        if counter == 5:
            return True

        counter = 0
        for i in range(5):
            point_temp.x, point_temp.y = point.x - i, point.y - i
            if self.isMoveValid(point_temp) and board[point.x - i][point.y - i] == turn:
                counter += 1
        if counter == 5:
            return True

        counter = 0
        for i in range(5):
            point_temp.x, point_temp.y = point.x + i, point.y - i
            if self.isMoveValid(point_temp) and board[point.x + i][point.y - i] == turn:
                counter += 1
        if counter == 5:
            return True

        counter = 0
        for i in range(5):
            point_temp.x, point_temp.y = point.x - i, point.y + i
            if self.isMoveValid(point_temp) and board[point.x - i][point.y + i] == turn:
                counter += 1
        if counter == 5:
            return True

        return False

    def getOpp(self, turn):
        if turn == self.color:
            return self.oppColor
        else:
            return self.color

    def __gameOver(self):
        if self.noMoveLeft(self.mainBoard):
            return True

        if self.__score(self.mainBoard, self.color) != 0:
            return True

        return

    def __score(self, board, turn):
        for i in board:
            for j in i:
                if j.value != -1 and self.winnerWinnerChickenDinner(board, turn, j):
                    return PentagoGame.MAXPOINT

        for i in board:
            for j in i:
                if j.value != -1 and self.winnerWinnerChickenDinner(board, self.getOpp(turn), j):
                    return PentagoGame.MINPOINT

        return 0

class BoardFrame(tk.Frame):
    def __init__(self, master=None, board=None):
        super().__init__(master=master)
        self.board = board

        self.canvas = tk.Canvas(self, width=400, height=400)
        self.columnconfigure(0, pad=3)
        self.columnconfigure(1, pad=3)
        self.columnconfigure(2, pad=3)
        
        self.rowconfigure(0, pad=3)
        self.rowconfigure(1, pad=3)
        self.rowconfigure(2, pad=3)
        self.rowconfigure(3, pad=3)
        style = Style()
        style.configure('W.TButton', font = ('calibri', 10, 'bold', 'underline'), 
                foreground = 'red')
        style.configure('')
        self.button = Button(self, text="start", style="W.TButton")
        self.button.grid(row=0, column=0, padx=10, pady=10)
        
    def draw_board(self):
        self.canvas.delete("all")
        x, y = 50, 20
        for board_x in self.board:
            x = 0
            for board_y in board_x:
                print(board_y)
                if board_y.value == 1:
                    self.canvas.create_rectangle(x, y, x + 20, y + 20, fill='red')
                elif board_y.value == 0:
                    self.canvas.create_rectangle(x, y, x + 20, y + 20, fill='green')
                else:
                    self.canvas.create_rectangle(x, y, x + 20, y + 20, fill=None, outline="red")
                time.sleep(0.075)
                self.__packing();
                x += 30
            y += 25        
        self.__packing()
    
    def __packing(self):
        self.canvas.update()
        # self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        self.canvas.grid(row=1, columnspan=2)
        
        self.pack(fill=tk.BOTH, expand=True)
    