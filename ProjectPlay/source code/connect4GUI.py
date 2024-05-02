##########################################################################################################################
# Josh Doyle (ID: 20417714)                                                                                              #
#                                                                                                                        #
# GUI and image processing code for Connect4:                                                                            #
# This code is GUI and image processing for Connect4. For the GUI, it creates a simple interface with the game board.    #
# The image processing part looks for the game board in the image from the webcam and then looks for which tile of the   #    
# board has the most green in it (the player makes there move by placing a green marker in the column they want to make  #
# their move in). It then tells the GUI which column to place the players move. It doesn't matter which row the player   #
# places the marker, the program will just check which column that is in and then tell the GUI to update the board.      #                                      
#                                                                                                                        #
#                                                                                                                        #
# [REF]                                                                                                                  #
#   [5]	OpenAI, “ChatGPT,” chat.openai.com, 2024(October 17 version)[Large language model].                              #
#       https://chat.openai.com/chat (accessed Mar. 22, 2024).                                                           #
#                                                                                                                        #
#   [6]	“Finding red color in image using Python & OpenCV,” Stack Overflow.                                              #
#       https://stackoverflow.com/a/55236890 (accessed Mar. 25, 2024).                                                   #
#                                                                                                                        #
# This code initially used ChatGPT [5] to create a very simple image processing method given the code from               #
# newTicImageGUI. I then made any nessessary changes to made the code into what was required.                            #
# The same image processing code [6] that was used in newTicImageGUI was used to create the image processing part of     #
# this program.                                                                                                          #
#                                                                                                                        #
##########################################################################################################################

import numpy as np
import cv2
import tkinter as tk
from tkinter import messagebox
from connect4 import Board, MCTS
import time

class Connect4GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4")
        self.root.configure(bg='black')

        #adds a title above the grid
        self.titlelabel = tk.Label(self.root, text="Connect 4", font=("Helvetica", 35), bg='black', fg='white')
        self.titlelabel.place(relx = 0.5, rely = 0.05, anchor = "center")

        #makes a red frame around the buttons (the grid)
        self.frame = tk.Frame(self.root, bg='red')
        self.frame.pack(padx=20,pady=20)

        self.buttons = [[None] * 7 for _ in range(6)]

        for row in range(6):
            for col in range(7):
                #makes grid tiles (as buttons)
                grid_tile = tk.Button(self.frame, text='', font=("Helvetica", 20), width=4, height=2, padx=10, pady=10, command=lambda c=col: self.on_button_click(c))
                grid_tile.grid(row=row, column=col, padx=8, pady=8)
                
                self.buttons[row][col] = grid_tile

        #adds instructions to the bottom of the screen 
        self.instructions = tk.Label(self.root, text="Press 's' to confirm player move, 'r' to reset the board, and 'q' to quit", font=("Helvetica", 12), bg='black', fg='white')
        self.instructions.place(relx = 0.5, rely = 0.95, anchor = "center")

        #keeps the game board in the center of the screen
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        #initializes the TicTacToe board and the MCTS algorithm
        self.board = Board()  
        self.mcts = MCTS()  

    def on_button_click(self, col):
        if not self.board.is_win() and not self.board.is_draw():
            self.board = self.board.make_move(col)
            self.update_board_gui()

            #if the board is not in a terminal state after player move, wait 1 second and then let the MCTS algorithm move its move
            if not self.board.is_win() and not self.board.is_draw():
                self.root.after(1000, self.move_AI) 

            if self.board.is_win():
                winner = 'o' if self.board.player_1 == 'x' else 'x'
                messagebox.showinfo("Game Over", f"Player '{winner}' wins!")
            elif self.board.is_draw():
                messagebox.showinfo("Game Over", "It's a draw!")

    def move_AI(self):
        best_move = self.mcts.search(self.board)
        self.board = best_move.board
        self.update_boardGUI()

        if self.board.is_win():
            winner = 'o' if self.board.player_1 == 'x' else 'x'
            messagebox.showinfo("Game Over", f"Player '{winner}' wins!")
        elif self.board.is_draw():
            messagebox.showinfo("Game Over", "It's a draw!")

    def update_boardGUI(self):
        #updates GUI with new board state
        for row in range(6):
            for col in range(7):
                player = self.board.position[row, col]
                text = player if player != self.board.empty_space else ''
                self.buttons[row][col].configure(text=text, font=("Helvetica", 20))


def image_processing(image, gui):
    #This converts the RGB image to a HSV image. This is because HSV is better for object detection
    image_in_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # [REF][6]
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

    #defines the columns in the grid
    cols = 7
    
    gridWidth = image.shape[1] // cols

    currentMaxGreen = 0
    currentMaxGreen_col = None

    #goes through grid to find the region with the most green
    for c in range(cols):
        #defines the current grid region
        x1 = c * gridWidth
        x2 = (c+1) * gridWidth

        #finds the current green concentration in the region
        green_concentration = np.count_nonzero(greenmask[:, x1:x2])

        #updates the new cell with the max concentration of green
        if green_concentration > currentMaxGreen:
            currentMaxGreen = green_concentration
            currentMaxGreen_col = c

    #updates the GUI of the corresponding cell that the most green was in
    if currentMaxGreen_col is not None:
        gui.on_button_click(currentMaxGreen_col)

    #shows the final filtered image for troubleshooting
    cv2.imshow("Final filtered image", final_filteredImage)
    cv2.waitKey(1)

def play_Connect4():
    root = tk.Tk()
    root.title("Connect 4")
    connect4_gui = Connect4GUI(root)

    #makes it fullscreen
    root.attributes('-fullscreen', True)  

    #opens up webcam window so we can make sure the grid is fully in frame
    cap = cv2.VideoCapture(0)
    webcam_window = cv2.namedWindow('Webcam', cv2.WINDOW_NORMAL)  # Create the webcam window

    quit = False  

    def on_key_press(event):
        nonlocal quit
        key = event.keysym
        if key == 'q':
            quit = True
        elif key == 's':
            ret, frame = cap.read()
            image_processing(frame, connect4_gui)
        elif key == 'r':
            #resets the game board
            connect4_gui.board = Board()  

            #updates GUI to clear board
            connect4_gui.update_boardGUI() 

    root.bind('<KeyPress>', on_key_press)

    while not quit:
        ret, frame = cap.read()
        cv2.imshow("Webcam", frame)

        # Set focus to the webcam window explicitly
        cv2.setWindowProperty("Webcam", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        #updates everything so the player can see
        root.update_idletasks()
        root.update()

    #closes everything down (only accessed if the player presses the 'q' key)
    cap.release()
    cv2.destroyAllWindows()
    root.quit()

if __name__ == "__main__":
    play_Connect4()