import pygame
import sys
import solver


pygame.init()
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 800
BOARD_HEIGHT = 700
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
BACKGROUND = pygame.image.load("assets/Background.png")
GAME_MODE_MEDIUM = 50
GAME_MODE_HARD = 60
GAME_MODE_EASY = 40
GAME_MODE = None
DEFAULT_GAME_MODE = GAME_MODE_MEDIUM


def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)


def change_game_mode(game_mode):
    GAME_MODE = game_mode


class Button():
    def __init__(self, pos, text_input, font, base_color, hovering_color, image=None):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) \
                and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if self.checkForInput(position):
            self.text = self.font.render(
                self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(
                self.text_input, True, self.base_color)


class Grid():
    def __init__(self, rows, cols, width, height):
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height
        self.model = None
        self.selected = None
        if not GAME_MODE:
            self.board = solver.generate_board(DEFAULT_GAME_MODE)
        else:
            self.board = solver.generate_board(GAME_MODE)
        self.cubes = [[Cube(self.board[i][j], i, j, width, height)
                       for j in range(cols)] for i in range(rows)]
        self.start_model = [[self.cubes[i][j].value for j in range(
            self.cols)] for i in range(self.rows)]
        self.added_nums = []
        self.start_nums = [(i, j) for i in range(rows)
                           for j in range(cols) if self.start_model[i][j] != 0]

    def update_model(self):
        self.model = [[self.cubes[i][j].value for j in range(
            self.cols)] for i in range(self.rows)]

    def place(self, val):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set(val)
            self.update_model()
            self.added_nums.append((row, col))
            if solver.valid(self.model, val, (row, col)):
                return True
            else:
                self.cubes[row][col].set(0)
                self.cubes[row][col].set_temp(0)
                self.update_model()
                return False

    def sketch(self, val):
        row, col = self.selected
        self.cubes[row][col].set_temp(val)

    def draw(self, win):
        # Draw Gridlines
        gap = self.width / 9
        for i in range(self.rows + 1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(win, (0, 0, 0), (0, i * gap),
                             (self.width, i * gap), thick)
            pygame.draw.line(win, (0, 0, 0), (i * gap, 0),
                             (i * gap, self.height), thick)
        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) in self.added_nums:
                    self.cubes[i][j].draw(win, "Blue")
                else:
                    self.cubes[i][j].draw(win, "Black")

    def select(self, row, col):
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False
        self.cubes[row][col].selected = True
        self.selected = (row, col)

    def clear(self):
        row, col = self.selected
        if self.cubes[row][col].value != 0 and (row, col) in self.added_nums and not self.is_finished():
            self.cubes[row][col].set(0)
            self.added_nums.remove((row, col))

    def click(self, pos):
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width/9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y), int(x))
        else:
            return None

    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j] != 0:
                    return False
        return True

    def solve_model(self, win):
        solver.solve(self.start_model)
        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) not in self.start_nums:
                    self.cubes[i][j].set(self.start_model[i][j])
                    self.added_nums.append((i, j))
                    self.cubes[i][j].draw(win, "Green")


class Cube():
    ROWS = 9
    COLS = 9

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.temp = 0
        self.selected = False

    def draw(self, win, color):
        fnt = pygame.font.SysFont("", 40)
        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), 1, (128, 128, 128))
            win.blit(text, (x+5, y+5))
        elif not (self.value == 0):
            text = fnt.render(str(self.value), 1, color)
            win.blit(text, (x + (gap/2 - text.get_width() / 2),
                     y + gap/2 - text.get_height()/2))
        if self.selected:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

    def set(self, val):
        self.value = val

    def set_temp(self, val):
        self.temp = val


class BlankGrid(Grid):
    def __init__(self, rows, cols, width, height):
        super().__init__(rows, cols, width, height)
        self.board = solver.generate_empty_board()
        self.cubes = [[Cube(self.board[i][j], i, j, self.width, self.height)
                       for j in range(self.cols)] for i in range(self.rows)]
        self.model = [[self.cubes[i][j].value for j in range(
            self.cols)] for i in range(self.rows)]
        self.added_nums = []

    def solve_model(self, win):
        solver.solve(self.model)
        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) not in self.added_nums:
                    self.cubes[i][j].set(self.model[i][j])
                    # self.added_nums.append((i, j))
                    self.cubes[i][j].draw(win, "Blue")
        print(self.added_nums)

    def draw(self, win):
        # Draw Gridlines
        gap = self.width / 9
        for i in range(self.rows + 1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(win, (0, 0, 0), (0, i * gap),
                             (self.width, i * gap), thick)
            pygame.draw.line(win, (0, 0, 0), (i * gap, 0),
                             (i * gap, self.height), thick)
        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) in self.added_nums:
                    self.cubes[i][j].draw(win, "Black")
                else:
                    self.cubes[i][j].draw(win, "Blue")


def play():
    board = Grid(9, 9, SCREEN_WIDTH, BOARD_HEIGHT)
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        pygame.display.set_caption("Play")
        SCREEN.fill("White")

        """
        PLAY_TEXT = get_font(45).render(
            "This is the PLAY screen.", True, "Black")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(640, 260))
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)

        """

        PLAY_BACK = Button(image=None, pos=(600, 750),
                           text_input="QUIT", font=get_font(30), base_color="Red", hovering_color="Green")

        PLAY_SOLVE = Button(image=None, pos=(100, 750),
                            text_input="SOLVE", font=get_font(30), base_color="Red", hovering_color="Green")

        PLAY_SOLVE.changeColor(PLAY_MOUSE_POS)
        PLAY_SOLVE.update(SCREEN)
        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)

        key = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()
                if PLAY_SOLVE.checkForInput(PLAY_MOUSE_POS):
                    board.solve_model(SCREEN)
                clicked = board.click(PLAY_MOUSE_POS)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_BACKSPACE:
                    board.clear()
                    key = None
                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.cubes[i][j].temp != 0:
                        if board.place(board.cubes[i][j].temp):
                            print("Sucess")
                        else:
                            print("Fail")
                        key = None
                        if board.is_finished():
                            print("Game over")
                            pygame.quit()
                            sys.exit()

        if board.selected and key != None:
            board.sketch(key)
        board.draw(SCREEN)
        pygame.display.update()


def options():
    while True:
        global GAME_MODE
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill((3, 252, 186))

        OPTIONS_TEXT = get_font(35).render(
            "Select Difficulty", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(SCREEN_WIDTH // 2, 100))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_EASY = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(SCREEN_WIDTH // 2, 250),
                              text_input="EASY", font=get_font(50), base_color="Black", hovering_color="Green")

        OPTIONS_MEDIUM = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(SCREEN_WIDTH // 2, 400),
                                text_input="MEDIUM", font=get_font(50), base_color="Black", hovering_color="Orange")

        OPTIONS_HARD = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(SCREEN_WIDTH // 2, 550),
                              text_input="HARD", font=get_font(50), base_color="Black", hovering_color="Red")

        OPTIONS_BACK = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(SCREEN_WIDTH // 2, 700),
                              text_input="BACK", font=get_font(50), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)
        OPTIONS_EASY.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_EASY.update(SCREEN)
        OPTIONS_MEDIUM.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_MEDIUM.update(SCREEN)
        OPTIONS_HARD.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_HARD.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()
                if OPTIONS_EASY.checkForInput(OPTIONS_MOUSE_POS):
                    GAME_MODE = GAME_MODE_EASY
                    main_menu()
                if OPTIONS_MEDIUM.checkForInput(OPTIONS_MOUSE_POS):
                    GAME_MODE = GAME_MODE_MEDIUM
                    main_menu()
                if OPTIONS_HARD.checkForInput(OPTIONS_MOUSE_POS):
                    GAME_MODE = GAME_MODE_HARD
                    main_menu()

        pygame.display.update()


def solve_puzzle():
    board = BlankGrid(9, 9, SCREEN_WIDTH, BOARD_HEIGHT)

    pygame.display.set_caption("Solve Puzzle")
    while True:
        mouse_pos = pygame.mouse.get_pos()
        SCREEN.fill("White")

        BACK = Button(image=None, pos=(600, 750),
                      text_input="QUIT", font=get_font(30), base_color="Red", hovering_color="Green")

        SOLVE = Button(image=None, pos=(100, 750),
                       text_input="SOLVE", font=get_font(30), base_color="Red", hovering_color="Green")

        SOLVE.changeColor(mouse_pos)
        SOLVE.update(SCREEN)
        BACK.changeColor(mouse_pos)
        BACK.update(SCREEN)

        key = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK.checkForInput(mouse_pos):
                    main_menu()
                if SOLVE.checkForInput(mouse_pos):
                    board.solve_model(SCREEN)
                clicked = board.click(mouse_pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_BACKSPACE:
                    board.clear()
                    key = None
                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.cubes[i][j].temp != 0:
                        if board.place(board.cubes[i][j].temp):
                            print("Sucess")
                        else:
                            print("Fail")
                        key = None
                        if board.is_finished():
                            print("Game over")
                            pygame.quit()
                            sys.exit()
        if key != None:
            i, j = board.selected
            if board.place(key):
                print("Sucess")
            else:
                print("Fail")
            key = None
            if board.is_finished():
                print("Game over")
                pygame.quit()
                sys.exit()
        board.draw(SCREEN)
        pygame.display.update()


def main_menu():
    pygame.display.set_caption("Menu")
    while True:
        SCREEN.fill((3, 252, 186))
        # SCREEN.blit(BACKGROUND, (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(80).render("Sudoku", True, "White")
        MENU_RECT = MENU_TEXT.get_rect(center=(SCREEN_WIDTH // 2, 100))
        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(SCREEN_WIDTH // 2, 250),
                             text_input="PLAY", font=get_font(60), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(SCREEN_WIDTH // 2, 400),
                                text_input="OPTIONS", font=get_font(60), base_color="#d7fcd4", hovering_color="White")
        SOLVE_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(SCREEN_WIDTH // 2, 550),
                              text_input="SOLVE", font=get_font(60), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, SOLVE_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if SOLVE_BUTTON.checkForInput(MENU_MOUSE_POS):
                    solve_puzzle()

        pygame.display.update()


main_menu()
