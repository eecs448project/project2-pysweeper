import pygame as pg
import os
from constants import (CELLWIDTH, CELLHEIGHT,
                      MARGIN, BORDER, COLOR, TOOLBARHEIGHT)
class GUI():
    """ GUI Class:
        Handles all window elements.
    """
    def __init__(self, board):
        """ A constructor for GUI().
            Calculate the game window based on board size.
            Defaults: ROWS=10, COLS=10
            Parameter: a Board object, from the Board class. The Board object
            will have all the sizes we need.
        """
        pg.display.set_caption("Minesweeper")
        self.font = pg.font.SysFont(None, 18)
        self.board = board
        self.width = ((CELLWIDTH + MARGIN) * board.columns) + \
                      (BORDER * 2)
        self.height = ((CELLHEIGHT + MARGIN) * board.rows) + \
                      (BORDER * 3) + TOOLBARHEIGHT
        if self.width < 284:
            self.width = 284
        self.window = pg.display.set_mode((self.width, self.height))

    def drawBoard(self):
        """ drawBoard() draws the board given to it on initialization.
            The self.board is always the current board. Iterate over
            each cell object in the box and space according to DEFAULTS
        """
        for row in range(self.board.rows):
            for col in range(self.board.columns):
                # Calucate the x-offset for each box.
                cellX = ((MARGIN + CELLWIDTH) * col + MARGIN) + BORDER
                # Calculate the y-offset for each box.
                cellY = ((MARGIN + CELLHEIGHT) * row + MARGIN) \
                        + (BORDER * 2) \
                        + TOOLBARHEIGHT # Toolbar offset from the top of window
                cellColor = COLOR['WHITE']
                if self.board.grid[row][col].revealed:
                    cellColor = COLOR['GRAY']
                    if self.board.grid[row][col].mine:
                        cellColor = COLOR['RED']
                elif self.board.grid[row][col].flagged:
                    cellColor = COLOR['GREEN']
                cell = pg.Rect([cellX, cellY, CELLWIDTH, CELLHEIGHT])
                pg.draw.rect(self.window, cellColor, cell)

                #display nearby mines if the cell is revealed and not a mine
                if cellColor == COLOR['GRAY']:
                    nearbyMines = self.board.countNearbyMines(row, col)
                    if (nearbyMines > 0):
                        text = self.font.render(str(nearbyMines), \
                                                True, \
                                                COLOR['BLACK'])
                        # Need offsets in x,y to prevent text being centered
                        #+on 0,0.
                        self.window.blit(text, (cellX + CELLWIDTH // 3, \
                                                cellY + CELLHEIGHT // 4))

                if cellColor == COLOR['RED']:
                    mineImage = pg.image.load("resources/trump.png")
                    self.window.blit(mineImage,(cellX,cellY))
                if cellColor == COLOR['GREEN']:
                    flagImg = pg.image.load("resources/flag.png")
                    self.window.blit(flagImg,(cellX,cellY))


    def mouseClick(self, event):
        """ mouseClick(event) takes an event argument, in this case a
        mouse click from the user on the board object,and handles any mouse
        event within the display.  The starting column and row positions are
        adjusted for the tool bar and margin. The 0,0 coordinate is the first
        cell generated on the board.
        Preconditions: a board object and GUI object have been defined.
        Parameters: an event defined by pygame, a button but specifically for
        this case a mouse click (event.button 1 is left click, event.button 2
        is right click).
        Postconditions: revealCell from the board class is called on a
        GUI object when the user clicks the left mouse button. flagCell from
        the board class when the user clicks the right mouse button.
        """
        mousePosition = pg.mouse.get_pos()
        column = (mousePosition[0] - BORDER) // \
                 (CELLWIDTH + MARGIN)
        row = (mousePosition[1] - (BORDER * 2) - TOOLBARHEIGHT) // \
              (CELLHEIGHT + MARGIN)
        if event.button == 1:
            self.board.revealCell(row, column)
        elif event.button == 3:
            self.board.flagCell(row, column)

#Code Based on https://stackoverflow.com/questions/46390231/how-to-create-a-text-input-box-with-pygame/46390412

class UIElement():
    """ Handles creation of all UI elements.
    This includes background, splash screen, and text.
    """
    def __init__(self, x, y, w, h, screen, text=''):
        """ A constructor for UIElement().
        Parameters: an x postion, a y position, the width of the object in
        pixels, the height if the object in pixels, a GUI object(screen), and
        text to be displayed.
        Note: use the empty string if there is no text.
        """
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR['WHITE']
        self.screen = screen
        self.text = text
        self.active = False

    def draw(self):
        """ Draws boxes on top of the screen or, in the case of text, combines
        draws the object directly to the surface of the screen.
        Preconditions: Must have a defined object to draw.
        Postconditions: The object will be displayed on the screen.
        """
        pg.draw.rect(self.screen.window, COLOR['BLACK'], self.rect)
        self.txt_surface = self.screen.font.render(self.text, True, self.color)
        self.screen.window.blit(self.txt_surface, (self.rect.x, self.rect.y))

class InputBox(UIElement):
    def __init__(self, x, y, w, h, screen, maxValue=0, minValue=0, text=''):
        super().__init__(x, y, w, h, screen, text)
        self.maxValue = maxValue
        self.minValue = minValue

    def update(self, field, value=0):
        """ This updates the input fields and any game attribute associated
            with that field.
        """
        if value.isnumeric():
            if (int(value) > self.maxValue):
                value = self.maxValue
            if (int(value) < self.minValue):
                value = self.minValue
            setattr(self.screen.board, field, int(value))
            self.screen.board.generateGrid()
            self.screen = GUI(self.screen.board)
            self.text = str(getattr(self.screen.board, field))
            self.draw()
        else:
            self.text = str(getattr(self.screen.board, field))
            self.draw()

    def draw(self):
        self.txt_surface = self.screen.font.render(self.text, True, COLOR['WHITE'])
        self.screen.window.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        self.color = COLOR['RED'] if self.active else COLOR['WHITE']
        pg.draw.rect(self.screen.window, self.color, self.rect, 1)

class InputButton(UIElement):
    def __init__(self, x, y, w, h, screen, text):
        super().__init__(x, y, w, h, screen, text)

    def restart(self, gui, board):
        self.active = False
        board.generateGrid()
        gui = GUI(board)

    def draw(self):
        self.txt_surface = self.screen.font.render(self.text, True, COLOR['WHITE'])
        self.screen.window.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        self.color = COLOR['RED'] if self.active else COLOR['WHITE']
        pg.draw.rect(self.screen.window, self.color, self.rect, 1)
