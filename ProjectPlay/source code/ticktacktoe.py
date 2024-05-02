##########################################################################################################################
# Josh Doyle (ID: 20417714)                                                                                              #
#                                                                                                                        #
# TicTacToe code:                                                                                                        #
# This code is the implementation of the game TicTacToe.                                                                 #   
#                                                                                                                        #
# [REF]                                                                                                                  #
#   [3]	“Coding tic tac toe AI using reinforcement learning (MCTS): intro & demo,”                                       #
#        www.youtube.com. https://youtu.be/-GRls60yRsQ?list=PLLfIBXQeu3aanwI5pYz6QyzYtnBEgcsZ8 (accessed Mar. 18, 2024). #
#                                                                                                                        #
# This code was inspired by this video [REF][3] about implementing MCTS in python and using it in TicTacToe.             #
##########################################################################################################################

from copy import deepcopy
from mcts import *

#Board class
class Board():
    # create constructor (init board class instance)
    def __init__(self, board=None):
        # define players
        self.player_1 = 'x'
        self.player_2 = 'o'
        self.empty_space = '.'
        
        # define board position
        self.position = {}
        
        # initialize current player
        self.current_player = self.player_1
        
        # reset board
        self.init_board()
        
        # create a copy of a previous board state if available
        if board is not None:
            self.__dict__ = deepcopy(board.__dict__)
    
    # reset board
    def init_board(self):
        # loop over board rows
        for row in range(3):
            # loop over board columns
            for col in range(3):
                # set every board square to empty space
                self.position[row, col] = self.empty_space
    
    # make move
    def make_move(self, row, col):
        # create new board instance that inherits from the current state
        board = Board(self)
        
        # make move
        board.position[row, col] = board.current_player
        
        # swap players
        (board.player_1, board.player_2) = (board.player_2, board.player_1)
        board.current_player = board.player_1 if board.current_player == board.player_2 else board.player_2
        
        # return new board state
        return board
    
    
    # get whether the game is won
    def is_win(self):
        ##################################
        # vertical sequence detection
        ##################################
        
        # loop over board columns
        for col in range(3):
            # define win sequence list
            win_sequence = []
            
            # loop over board rows
            for row in range(3):
                # if found same next element in the row
                if self.position[row, col] == self.player_2:
                    # update win sequence
                    win_sequence.append((row, col))
                    
                # if we have 3 elements in the row
                if len(win_sequence) == 3:
                    # return the game is won state
                    return True
        
        ##################################
        # horizontal sequence detection
        ##################################
        
        # loop over board columns
        for row in range(3):
            # define win sequence list
            win_sequence = []
            
            # loop over board rows
            for col in range(3):
                # if found same next element in the row
                if self.position[row, col] == self.player_2:
                    # update win sequence
                    win_sequence.append((row, col))
                    
                # if we have 3 elements in the row
                if len(win_sequence) == 3:
                    # return the game is won state
                    return True
    
        ##################################
        # 1st diagonal sequence detection
        ##################################
        
        # define win sequence list
        win_sequence = []
        
        # loop over board rows
        for row in range(3):
            # init column
            col = row
        
            # if found same next element in the row
            if self.position[row, col] == self.player_2:
                # update win sequence
                win_sequence.append((row, col))
                
            # if we have 3 elements in the row
            if len(win_sequence) == 3:
                # return the game is won state
                return True
        
        ##################################
        # 2nd diagonal sequence detection
        ##################################
        
        # define win sequence list
        win_sequence = []
        
        # loop over board rows
        for row in range(3):
            # init column
            col = 3 - row - 1
        
            # if found same next element in the row
            if self.position[row, col] == self.player_2:
                # update win sequence
                win_sequence.append((row, col))
                
            # if we have 3 elements in the row
            if len(win_sequence) == 3:
                # return the game is won state
                return True
        
        # by default return non-winning state
        return False
    
    # get whether the game is drawn
    def is_draw(self):
        # loop over board squares
        for row, col in self.position:
            #if there is an empty space available
            if self.position[row, col] == self.empty_space:
                #it's not a draw
                return False
        
        # by default we return a draw
        return True
    
    # generate legal moves to play in the current position
    def generate_states(self):
        # define states list (move list - list of available actions to consider)
        possible_actions = []
        
        # loop over board rows
        for row in range(3):
            # loop over board columns
            for col in range(3):
                # make sure that current square is empty
                if self.position[row, col] == self.empty_space:
                    # append available action/board state to action list
                    possible_actions.append(self.make_move(row, col))
        
        # return the list of available actions (board class instances)
        return possible_actions
    
    # main game loop
    def game_loop(self):
        print('  Type "exit" to exit the game')
        print('  Move format is x,y :  where x is column and y is row')
        
        # print board
        print(self)
        
        # create MCTS instance
        mcts = MCTS()
                
        # game loop
        while True:
            # get user input
            player_input = input('> ')
        
            # escape condition
            if player_input == 'exit': break
            
            # skip empty input
            if player_input == '': continue
            
            try:
                # parse user input (move format [col, row]: 1,2) 
                row = int(player_input.split(',')[1]) - 1
                col = int(player_input.split(',')[0]) - 1

                # check if move is legal
                if self.position[row, col] != self.empty_space:
                    print(' Illegal move!')
                    continue

                # make move on board
                self = self.make_move(row, col)
                
                # print board
                print(self)
                
                # search for the best move
                best_move = mcts.search(self)
                
                # legal moves available
                try:
                    # make AI move here
                    self = best_move.board
                
                # game over
                except:
                    pass
                
                # print board
                print(self)
                
                # check if the game is won
                if self.is_win():
                    print('player "%s" has won!\n' % self.player_2)
                    break
                
                # check if the game is drawn
                elif self.is_draw():
                    print('The game is drawn!\n')
                    break
            
            except Exception as e:
                print('  Error:', e)

                print('  Illegal move!')
                print('  Move format is x,y : where x is column and y is row')
        
    # print board state
    def __str__(self):
        # define board string representation
        string_of_board = ''
        
        # loop over board rows
        for row in range(3):
            # loop over board columns
            for col in range(3):
                string_of_board += ' %s' % self.position[row, col]
            
            # print new line every row
            string_of_board += '\n'
        
        # prepend side to move
        if self.player_1 == 'x':
            string_of_board = '\n------------\n "o" turn:\n------------\n\n' + string_of_board
        
        elif self.player_1 == 'o':
            string_of_board = '\n------------\n "x" turn:\n------------\n\n' + string_of_board
                        
        # return board string
        return string_of_board

# main
if __name__ == '__main__':
    #make board instance
    board = Board()
    
    #start game loop
    board.game_loop()

    #make MCTS instance
    mcts = MCTS()
