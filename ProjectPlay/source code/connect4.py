##########################################################################################################################
# Josh Doyle (ID: 20417714)                                                                                              #
#                                                                                                                        #
# Connect4 code:                                                                                                         #
# This is the game code for Connect4.                                                                                    #   
#                                                                                                                        #
#                                                                                                                        #
# [REF]                                                                                                                  #
#   [5]	OpenAI, “ChatGPT,” chat.openai.com, 2024(October 17 version)[Large language model].                              #
#       https://chat.openai.com/chat (accessed Mar. 22, 2024)                                                            #
#                                                                                                                        #
# This code initially used ChatGPT by taking the TicTacToe code and making a similar code layout for Connect4.           #
# This was done to save time.                                                                                            #
##########################################################################################################################

from mcts import MCTS
from copy import deepcopy

class Board():
    def __init__(self, board=None):
        self.player_1 = 'x'
        self.player_2 = 'o' 
        self.empty_space = '.'

        #the number of rows and columns
        self.columns = 7  
        self.rows = 6   

         #defines board position
        self.position = {}

        #reset board
        self.init_board()
        
        # create a copy of a previous board state if available
        if board is not None:
            self.__dict__ = deepcopy(board.__dict__)

    #resets board by changing every space to an empty space again
    def init_board(self):
        for row in range(self.rows):
            for col in range(self.columns):
                self.position[row, col] = self.empty_space

    def make_move(self, col):
        # create new board instance that inherits from the current state
        board = Board(self)
        
        #determines whos turn it is
        player = board.player_1 if board.player_1 else board.player_2

        #iterates through the rows from bottom to top
        for row in range(self.rows - 1, -1, -1):

            #checks if the space is empty
            if board.position[row, col] == self.empty_space:

                #places player's move in that space
                board.position[row, col] = player
                break  

        # swap players
        (board.player_1, board.player_2) = (board.player_2, board.player_1)

        # return new board state
        return board

    
    def __str__(self):
        # define board string representation
        string_of_board = ''
        
        # loop over board rows
        for row in range(6):
            # loop over board columns
            for col in range(7):
                string_of_board += ' %s' % self.position[row, col]
            
            # print new line every row
            string_of_board += '\n'
        
        # prepend side to move
        if self.player_1 == 'x':
            string_of_board = '\n------------\n "x" turn:\n-------------\n\n' + string_of_board
        
        elif self.player_1 == 'o':
            string_of_board = '\n------------\n "o" turn:\n-------------\n\n' + string_of_board
                        
        # return board string
        return string_of_board

    def is_draw(self):
        # loop over board squares
        for row, col in self.position:
            #if there is an empty space available
            if self.position[row, col] == self.empty_space:
                #it's not a draw
                return False
            
            # by default we return a draw
        return True

    def is_win(self):
        #checks win conditions
        for row in range(self.rows):
            for col in range(self.columns):

                #if the current position is empty, skip it
                if self.position[row, col] == self.empty_space:
                    continue

                ##################################
                # Vertical sequence detection
                ##################################
                
                #checks if there are enough rows below the current row to form a vertical win sequence
                if row <= self.rows - 4:

                    #checks if all positions in that column have the same value for the next 4 rows
                    if all(self.position[row+i, col] == self.position[row, col] for i in range(4)):

                        # if they match, returns True because a vertical win was found
                        return True

                ##################################
                # Horizontal sequence detection
                ##################################
                    
                #checks if there are enough columns to the right to form a horizontal win sequence
                if col <= self.columns - 4:

                    #checks if all positions in that row have the same value for the next 4 columns
                    if all(self.position[row, col+i] == self.position[row, col] for i in range(4)):

                        # if they match, returns True because a horizontal win was found
                        return True

                ##################################
                # 1st diagonal sequence detection (top-left to bottom-right)
                ################################## 
                        
                #checks if there are enough rows and columns to form a diagonal win sequence towards bottom right
                if row <= self.rows - 4 and col <= self.columns - 4:

                    #checks if all positions in the diagonal have the same value for the next 4 diagonal positions
                    if all(self.position[row+i, col+i] == self.position[row, col] for i in range(4)):

                        # if they match, returns True because a diagonal win sequence from top-left to bottom-right was found
                        return True

                ##################################
                # 2nd diagonal sequence detection (top-right to bottom-left)
                ################################## 
                        
                #checks if there are enough rows and columns to form a diagonal sequence towards bottom left
                if row <= self.rows - 4 and col >= 3:

                    #checks if all positions in the diagonal have the same value for the next 4 diagonal positions
                    if all(self.position[row + i, col - i] == self.position[row, col] for i in range(4)):

                        # if they match, returns True because a diagonal win sequence from top-right to bottom-left was found
                        return True

        #if no win was found, returns False
        return False


    def game_loop(self):
        print(' Type "exit" to quit')
        print(' Move format col: 1 where 1 is the column number (1 to 7)')
        
        # prints board
        print(self)
        
        # creates MCTS instance
        mcts = MCTS()
                
        # game loop
        while True:
            # gets user input
            user_input = input('> ')
        
            # escape condition
            if user_input == 'exit':
                break
            
            # skips empty input
            if user_input == '':
                continue
            
            try:
                # parses user input (move format [col]: 1)
                col = int(user_input) - 1

                # checks move legality
                if self.position[0, col] != self.empty_space:
                    print(' Illegal move!')
                    continue

                # makes move
                self = self.make_move(col)
                
                # prints board
                print(self)
                
                # checks if the game is won
                if self.is_win():
                    print('Player "%s" has won the game!\n' % self.player_1)
                    break
                
                # check if the game is drawn
                if self.is_draw():
                    print('Game is drawn!\n')
                    break
                
                # searches for the best move
                best_move = mcts.search(self)
                
                # legal moves available
                try:
                    # make AI move here
                    self = best_move.board
                    print(self)
                    
                    # check if the game is won after the AI move
                    if self.is_win():
                        print('Player "%s" has won the game!\n' % self.player_2)
                        break

                # game over
                except:
                    pass
            
            except Exception as e:
                print('  Error:', e)
                print('  Illegal move!')
                print('  Move format col: 1 where 1 is the column number (1 to 7)')

    def generate_states(self):
        actions = []
        for col in range(self.columns):
            if self.position[0, col] == self.empty_space:

                actions.append(self.make_move(col))

        return actions


if __name__ == '__main__':
    # creates board instance
    board = Board()
    
    # start game loop
    board.game_loop()
