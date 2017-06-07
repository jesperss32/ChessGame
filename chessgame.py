# Jesper van Duuren
# 10780793
# Amber Ligtvoet
# 10909176


from __future__ import print_function
from copy import deepcopy
import sys

## Helper functions

# Translate a position in chess notation to x,y-coordinates
# Example: c3 corresponds to (2,5)
def to_coordinate(notation):
    x = ord(notation[0]) - ord('a')
    y = 8 - int(notation[1])
    return (x, y)

# Translate a position in x,y-coordinates to chess notation
# Example: (2,5) corresponds to c3
def to_notation(coordinates):
    (x,y) = coordinates
    letter = chr(ord('a') + x)
    number = 8 - y
    return letter + str(number)

# Translates two x,y-coordinates into a chess move notation
# Example: (1,4) and (2,3) will become b4c5
def to_move(from_coord, to_coord):
    return to_notation(from_coord) + to_notation(to_coord)

## Defining board states

# These Static classes are used as enums for:
# - Material.Rook
# - Material.King
# - Material.Pawn
# - Side.White
# - Side.Black
class Material:
    Rook, King, Pawn = ['r','k','p']
class Side:
    White, Black = range(0,2)

# A chesspiece on the board is specified by the side it belongs to and the type
# of the chesspiece
class Piece:
    def __init__(self, side, material):
        self.side = side
        self.material = material


# A chess configuration is specified by whose turn it is and a 2d array
# with all the pieces on the board
class ChessBoard:

    def __init__(self, turn):
        # This variable is either equal to Side.White or Side.Black
        self.turn = turn
        self.board_matrix = None


    ## Getter and setter methods
    def set_board_matrix(self,board_matrix):
        self.board_matrix = board_matrix

    # Note: assumes the position is valid
    def get_boardpiece(self,position):
        (x,y) = position
        return self.board_matrix[y][x]

    # Note: assumes the position is valid
    def set_boardpiece(self,position,piece):
        (x,y) = position
        self.board_matrix[y][x] = piece

    # Read in the board_matrix using an input string
    def load_from_input(self,input_str):
        self.board_matrix = [[None for _ in range(8)] for _ in range(8)]
        x = 0
        y = 0
        for char in input_str:
            if y == 8:
                if char == 'W':
                    self.turn = Side.White
                elif char == 'B':
                    self.turn = Side.Black
                return
            if char == '\r':
                continue
            if char == '.':
                x += 1
                continue
            if char == '\n':
                x = 0
                y += 1
                continue

            if char.isupper():
                side = Side.White
            else:
                side = Side.Black
            material = char.lower()

            piece = Piece(side, material)
            self.set_boardpiece((x,y),piece)
            x += 1

    # Print the current board state
    def __str__(self):
        return_str = ""

        return_str += "   abcdefgh\n\n"
        y = 8
        for board_row in self.board_matrix:
            return_str += str(y) + "  "
            for piece in board_row:
                if piece == None:
                    return_str += "."
                else:
                    char = piece.material
                    if piece.side == Side.White:
                        char = char.upper()
                    return_str += char
            return_str += '\n'
            y -= 1

        turn_name = ("White" if self.turn == Side.White else "Black")
        return_str += "It is " + turn_name + "'s turn\n"

        return return_str

    # Given a move string in chess notation, return a new ChessBoard object
    # with the new board situation
    # Note: this method assumes the move suggested is a valid, legal move
    def make_move(self, move_str):

        start_pos = to_coordinate(move_str[0:2])
        end_pos = to_coordinate(move_str[2:4])

        if self.turn == Side.White:
            turn = Side.Black
        else:
            turn = Side.White

        # Duplicate the current board_matrix
        new_matrix = [row[:] for row in self.board_matrix]

        # Create a new chessboard object
        new_board = ChessBoard(turn)
        new_board.set_board_matrix(new_matrix)

        # Carry out the move in the new chessboard object
        piece = new_board.get_boardpiece(start_pos)
        new_board.set_boardpiece(end_pos, piece)
        new_board.set_boardpiece(start_pos, None)

        return new_board

    def is_king_dead(self, side):
        seen_king = False
        for x in range(8):
            for y in range(8):
                piece = self.get_boardpiece((x,y))
                if piece != None and piece.side == side and \
                        piece.material == Material.King:
                    seen_king = True
        return not seen_king

    # This function should return, given the current board configuation and
    # which players turn it is, all the moves possible for that player
    # It should return these moves as a list of move strings, e.g.
    # [c2c3, d4e5, f4f8]
    # TODO: write an implementation for this function
    def legal_moves(self):
        possible_moves = []
        for i in range(0, 8):
            for j in range(0, 8):
                #print ("test legal move %d %d" % (i, j))
                begin_position = (i,j)
                for k in range (0, 8):
                    for l in range (0, 8):
                        end_position = (k,l)
                        move = (begin_position, end_position)
                        if(self.is_legal_move(move)):
                            possible_moves.append(to_move(begin_position, end_position))
        print('possible moves')
        print (possible_moves)
        return

    # This function should return, given the move specified (in the format
    # 'd2d3') whether this move is legal
    # TODO: write an implementation for this function, implement it in terms
    # of legal_moves()
    # TODO: check method for different games
    # TODO: check for other objects on the field
    def is_legal_move(self, move):
        (begin_position, end_position) = move
        if(self.check_position(begin_position)==False):
            return False
        piece = self.get_boardpiece(begin_position)
        if(piece.material == 'p'):
            #print ('This is a pawn')
            if(self.check_movement_pawns(begin_position, end_position) == False):
                return False
        elif(piece.material == 'k'):
            if(self.check_movement_kings(begin_position, end_position) == False):
                return False
        elif(piece.material == 'r'):
            if(self.check_movement_rooks(begin_position, end_position) == False):
                return False
        return True

    # method to check if the object in the position belongs to the player
    def check_position(self, position):
        piece = self.get_boardpiece(position)
        if (piece == None):
            return False
        if((piece.side == self.turn) == False):
            return False
        return True

    # method checks for enemy object and returns true if enemy is detected
    def check_for_enemy_object(self, position):
        piece = self.get_boardpiece(position)
        if (piece == None):
            return False
        if(piece.side == self.turn):
            return False
        else:
            return True

    # method to check the movement of a pawn
    # TODO: a hit of a pawn
    def check_movement_pawns(self, begin_position, end_position):
        #print('check_movement of pawn')
        (x_begin, y_begin) = begin_position
        (x_end, y_end) = end_position
        piece = self.get_boardpiece(begin_position)
        if(piece.side == Side.White):
            if((y_begin + 1 == y_end and x_begin == x_end) == False):
                return False
        elif(piece.side == Side.Black):
            if ((y_begin - 1 == y_end and x_begin == x_end) == False):
                return False
        if(self.check_position(end_position)):
            return False
        if(self.check_for_enemy_object(end_position)):
            return False
        return True

    # method to check the movement of a king
    # TODO: check for other objects
    def check_movement_kings(self, begin_position, end_position):
        #print('check movement of king')
        (x_begin, y_begin) = begin_position
        (x_end, y_end) = end_position
        if (x_begin == x_end and y_begin == y_end):
            #print('move nog possible, no movement detected')
            return False
        elif (x_begin == x_end):
            #print ('move possible equal x')
            return True
        elif (y_begin == y_end):
            #print ('move possible equal y')
            return True
        elif(x_begin - y_begin == x_end - y_end):
            #print('schuine verplaatsing')
            return True
        elif(x_begin-x_end == y_end - y_begin):
            #print('schuine verplaatsing')
            return True
        else:
            #print("no move possible")
            return False

    # method to check the movement of a rook
    # TODO: check for other objects
    def check_movement_rooks(self, begin_position, end_position):
        #print('check movement of rook')
        (x_begin, y_begin) = begin_position
        (x_end, y_end) = end_position


        if(x_begin == x_end and y_begin == y_end):
            #print('move nog possible, no movement detected')
            return False
        elif(x_begin == x_end):
            for y in range(y_begin, y_end):
                # control if no objects
            return True
        elif(y_begin == y_end):
            for x in range(x_begin, x_end)
                # control no objects
            #print ('move possible equal y')
            return True
        else:
            #print('move not possible')
            return False







# This static class is responsible for providing functions that can calculate
# the optimal move using minimax
class ChessComputer:

    # This method uses either alphabeta or minimax to calculate the best move
    # possible. The input needed is a chessboard configuration and the max
    # depth of the search algorithm. It returns a tuple of (score, chessboard)
    # with score the maximum score attainable and chessboardmove that is needed
    #to achieve this score.
    @staticmethod
    def computer_move(chessboard, depth, alphabeta=False):
        if alphabeta:
            inf = 99999999
            min_inf = -inf
            return ChessComputer.alphabeta(chessboard, depth, min_inf, inf)
        else:
            return ChessComputer.minimax(chessboard, depth)


    # This function uses minimax to calculate the next move. Given the current
    # chessboard and max depth, this function should return a tuple of the
    # the score and the move that should be executed
    # NOTE: use ChessComputer.evaluate_board() to calculate the score
    # of a specific board configuration after the max depth is reached
    # TODO: write an implementation for this function
    @staticmethod
    def minimax(chessboard, depth):
        return (0, "no implementation written")

    # This function uses alphabeta to calculate the next move. Given the
    # chessboard and max depth, this function should return a tuple of the
    # the score and the move that should be executed.
    # It has alpha and beta as extra pruning parameters
    # NOTE: use ChessComputer.evaluate_board() to calculate the score
    # of a specific board configuration after the max depth is reached
    @staticmethod
    def alphabeta(chessboard, depth, alpha, beta):
        return (0, "no implementation written")

    # Calculates the score of a given board configuration based on the
    # material left on the board. Returns a score number, in which positive
    # means white is better off, while negative means black is better of
    @staticmethod
    def evaluate_board(chessboard, depth_left):
        return 0

# This class is responsible for starting the chess game, playing and user
# feedback
class ChessGame:
    def __init__(self, turn):

        # NOTE: you can make this depth higher once you have implemented
        # alpha-beta, which is more efficient
        self.depth = 4
        self.chessboard = ChessBoard(turn)

        # If a file was specified as commandline argument, use that filename
        if len(sys.argv) > 1:
            filename = sys.argv[1]
        else:
            filename = "board.chb"

        print("Reading from " + filename + "...")
        self.load_from_file(filename)

    def load_from_file(self, filename):
        with open(filename) as f:
            content = f.read()

        self.chessboard.load_from_input(content)

    def main(self):
        while True:
            print(self.chessboard)

            # Print the current score
            score = ChessComputer.evaluate_board(self.chessboard,self.depth)
            print("Current score: " + str(score))

            # Calculate the best possible move
            new_score, best_move = self.make_computer_move()

            print("Best move: " + best_move)
            print("Score to achieve: " + str(new_score))
            print("")
            self.chessboard.legal_moves()
            self.make_human_move()


    def make_computer_move(self):
        print("Calculating best move...")
        return ChessComputer.computer_move(self.chessboard,
                self.depth, alphabeta=True)


    def make_human_move(self):
        # Endlessly request input until the right input is specified
        while True:
            if sys.version_info[:2] <= (2, 7):
                move = raw_input("Indicate your move (or q to stop): ")
            else:
                move = input("Indicate your move (or q to stop): ")
            if move == "q":
                print("Exiting program...")
                sys.exit(0)
            elif self.chessboard.is_legal_move(move):
                break
            print("Incorrect move!")

        self.chessboard = self.chessboard.make_move(move)

        # Exit the game if one of the kings is dead
        if self.chessboard.is_king_dead(Side.Black):
            print(self.chessboard)
            print("White wins!")
            sys.exit(0)
        elif self.chessboard.is_king_dead(Side.White):
            print(self.chessboard)
            print("Black wins!")
            sys.exit(0)

chess_game = ChessGame(Side.White)
chess_game.main()

