##########################################################################################################################
# Josh Doyle (ID: 20417714)                                                                                              #
#                                                                                                                        #
# GUI and image processing code for TicTacToe:                                                                           #
# This code is GUI and image processing for TicTacToe. For the GUI, it creates a simple interface with the game board.   #
# The image processing part looks for the game board in the image from the webcam and then looks for which tile of the   #
# board has the most green in it (the player makes there move by placing a green marker in the tile they want to make    #
# their move in). It then tells the GUI which tile to place the players move.                                            #
#                                                                                                                        #
#                                                                                                                        #
# [REF]                                                                                                                  #
#   [5]	OpenAI, “ChatGPT,” chat.openai.com, 2024(October 17 version)[Large language model].                              #
#       https://chat.openai.com/chat (accessed Mar. 22, 2024).                                                           #
#                                                                                                                        #
#   [6]	“Finding red color in image using Python & OpenCV,” Stack Overflow.                                              #
#       https://stackoverflow.com/a/55236890 (accessed Mar. 25, 2024).                                                   #
#                                                                                                                        #
# This code initially used ChatGPT [5] to create a very simple image processing method since I didn't know how to do     #
# image processing. I then learnt how to do image processing and was able to redo alot of the code. This code in Stack   #
# Overflow [6] was also used for the image processing (for the part for seperating the red from the image).              #
#                                                                                                                        #
##########################################################################################################################

import numpy as np
import cv2
import tkinter as tk
from tkinter import messagebox
from ticktacktoe import Board, MCTS
import time

class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        root.title('Tic Tac Toe')
        self.root.configure(bg='black')

        #adds a title above the grid
        self.titlelabel = tk.Label(self.root, text="Tic Tac Toe", font=("Helvetica", 35), bg='black', fg='white')
        self.titlelabel.place(relx = 0.5, rely = 0.1, anchor = "center")

        #makes a red frame around the buttons (the grid)
        self.frame = tk.Frame(self.root, bg='red')
        self.frame.pack(padx=20,pady=20)

        self.buttons = [[None,None,None] for _ in range(3)]

        for row in range(3):
            for col in range(3):

                #makes grid tiles (as buttons)
                grid_tile = tk.Button(self.frame, font=("Helvetica", 24), width=6, height=3, padx=10, pady=10, command=lambda r=row, c=col: self.on_button_click(r, c))
                grid_tile.grid(row=row, column=col, padx=10, pady=10)
                
                self.buttons[row][col] = grid_tile

        #adds instructions to the bottom of the screen 
        self.instructions = tk.Label(self.root, text="Press 's' to confirm player move, 'r' to reset the board, and 'q' to quit", font=("Helvetica", 12), bg='black', fg='white')
        self.instructions.place(relx = 0.5, rely = 0.9, anchor = "center")

        #keeps the game board in the center of the screen
        self.frame.place(relx=0.5, rely=0.5, anchor="center")
        

        #initializes the TicTacToe board and the MCTS algorithm
        self.board = Board()
        self.mcts = MCTS()  


    def on_button_click(self, row, col):
        if self.board.position[row, col] == self.board.empty_space and not self.board.is_win() and not self.board.is_draw():
            self.board = self.board.make_move(row, col)
            self.update_boardGUI()

            #if the board is not in a terminal state after player move, wait 1 second and then let the MCTS algorithm move its move
            if not self.board.is_win() and not self.board.is_draw():
                self.root.after(1000, self.move_AI)
            #if there is a win 
            if self.board.is_win():
                winner = 'o' if self.board.current_player == 'x' else 'x'
                messagebox.showinfo("Game Over", f"Player '{winner}' wins!")
            elif self.board.is_draw():
                messagebox.showinfo("Game Over", "It's a draw!")

    def move_AI(self):
        best_move = self.mcts.search(self.board)
        self.board = best_move.board
        self.update_boardGUI()

        if self.board.is_win():
            winner = 'o' if self.board.current_player == 'x' else 'x'
            messagebox.showinfo("Game Over", f"Player '{winner}' wins!")
        elif self.board.is_draw():
            messagebox.showinfo("Game Over", "It's a draw!")

    def update_boardGUI(self):
        for row in range(3):
            for col in range(3):
                player = self.board.position[row, col]
                text = player if player != self.board.empty_space else ''
                self.buttons[row][col].configure(text=text, font=("Helvetica", 24))


def image_processing(image, gui):
    #This converts the RGB image to a HSV image. This is because HSV is better for object colour detection
    image_in_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #defines the upper and lower bounds for the red colour we want to detect
    #lower bounds of the red color range values (0 - 10)
    red_lowerbound1 = np.array([0, 100, 20])
    red_upperbound1 = np.array([10, 255, 255])

    #upper bounds of the red color range values (160 - 180)
    red_lowerbound2 = np.array([160,100,20])
    red_upperbound2 = np.array([179,255,255])

    #makes masks for both upper and lower boundaries
    redmask1 = cv2.inRange(image_in_HSV, red_lowerbound1, red_upperbound1)
    redmask2 = cv2.inRange(image_in_HSV, red_lowerbound2, red_upperbound2)

    #combines red masks to make final red mask
    final_redmask = redmask1 + redmask2

    #defines the upper and lower bounds for the green colour we want to detect
    green_lowerbound = np.array([40, 40, 40])
    green_upperbound = np.array([80, 255, 255])

    #isolates all green from the image by making a green mask
    greenmask = cv2.inRange(image_in_HSV, green_lowerbound, green_upperbound)

    #combines the red and green masks
    final_combinedmask = cv2.bitwise_or(final_redmask, greenmask)

    #overlay the combined mask with the original image so we can see the colours (for troubleshooting)
    final_filteredImage = cv2.bitwise_or(image.copy(), image.copy(), mask=final_combinedmask)

    #defines the grid in the image
    rows, cols = 3, 3
    gridHeight = image.shape[0] // rows
    gridWidth = image.shape[1] // cols

    currentMaxGreen = 0
    currentMaxGreen_cell = None

    #goes through grid to find the region with the most green
    for r in range(rows):
        for c in range(cols):
            #defines the current grid region
            y1 = r * gridHeight
            y2 = (r+1) * gridHeight

            x1 = c * gridWidth
            x2 = (c+1) * gridWidth

            #finds the current green concentration in the region
            currentGreen = np.count_nonzero(greenmask[y1:y2,x1:x2])

            #updates the new cell with the max concentration of green
            if currentGreen > currentMaxGreen:
                currentMaxGreen = currentGreen
                currentMaxGreen_cell = (r, c)


    #after it's went through the grid and found the cell with the most green, it will fine the same corresponding cell in the GUI and update the players move there
    if currentMaxGreen_cell is not None:
        #calculates the center coordinates of the cell
        x_cellCenter = (currentMaxGreen_cell[1]*gridWidth)+(gridWidth // 2)
        y_cellCenter = (currentMaxGreen_cell[0]*gridHeight)+(gridHeight // 2)

        #finds the corresponding cell in the grid
        rowOfCell = y_cellCenter // gridHeight
        colOfCell = x_cellCenter // gridWidth

        #updates the GUI of the corresponding cell that the most green was in
        gui.on_button_click(rowOfCell, colOfCell)

    #shows the final filtered image for troubleshootin
    cv2.imshow("Final filtered image", final_filteredImage)
    cv2.waitKey(1)


def play_TicTacToe():
    root = tk.Tk()
    root.title("Tic Tac Toe")
    tictactoe_GUI = TicTacToeGUI(root)

    #makes it fullscreen
    root.attributes('-fullscreen', True)
    
    #opens up webcam window so we can make sure the grid is fully in frame
    cap = cv2.VideoCapture(0)
    webcam_window = cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL) 

    quit = False  

    def on_key_press(event):
        nonlocal quit
        key = event.keysym
        if key == 's':
            ret, frame = cap.read()
            image_processing(frame, tictactoe_GUI)
        elif key == 'q':
            quit = True
        elif key == 'r':
            #resets the game board
            tictactoe_GUI.board = Board()
            #updates GUI to clear board
            tictactoe_GUI.update_boardGUI() 

    root.bind('<KeyPress>', on_key_press)

    while not quit:
        ret, frame = cap.read()
        cv2.imshow("Webcam", frame)

        cv2.setWindowProperty("Webcam", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        #updates everything so the player can see
        root.update_idletasks()
        root.update()

    #closes everything down (only accessed if the player presses the 'q' key)
    cap.release()
    cv2.destroyAllWindows()
    root.quit()

if __name__ == "__main__":
    play_TicTacToe()