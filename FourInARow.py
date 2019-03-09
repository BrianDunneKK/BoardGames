# To Do: Button labels not centered

import sys
sys.path.append("../pygame-cdkk")
from PyGameApp import *
from BoardGames import *

MNK_COLS = 7   # m
MNK_ROWS = 6   # n
MNK_INAROW = 4 # k

### --------------------------------------------------

class Sprite_mnkGame_Button(Sprite_TextBox):
    def __init__(self, name, event_on_click, centerx, centery, event_on_unclick=None):
        super().__init__(name)
        self.text = name
        self.setup_text(36, "black")
        self.setup_textbox(120, 35, "black", 36, ["gray80", "black"])
        self.setup_mouse_events(event_on_click, event_on_unclick)
        self.rect.center = (centerx, centery)

class Sprite_mnkGame_Label(Sprite_TextBox):
    def __init__(self, name, posx, posy):
        super().__init__(name)
        self.setup_textbox(150, 35, "black", 36)
        self.text_format = name + ": {0}"
        self.set_text("12345")
        self.rect.left = posx
        self.rect.centery = posy

class Sprite_mnkGame_Winner(Sprite_TextBox):
    def __init__(self, centerx, centery):
        super().__init__("Winner")
        self.rect.size = (400, 70)
        self.colours = ["yellow1","red4"]
        self.setup_text(48, "red4", "Winner: {0}")
        self.rect.center = (centerx, 42)

### --------------------------------------------------

class Sprite_mnkGame_Piece(Sprite_BoardGame_Piece):
    mnkGame_board = None
    mnkGame_piece_shape = Sprite_BoardGame_Piece.PIECE_CIRLCE
    mnkGame_piece_colours = ["red1", None, "darkgoldenrod1"]

    def __init__(self, name, col, row, player):
        super().__init__(name, self.mnkGame_board, col, row)
        self.rect.set_acceleration(0, self.rect.gravity*2)
        self.rect.multiplier = 100
        self.setup_piece(self.mnkGame_piece_shape, self.mnkGame_piece_colours, (player == "1"))

    def update(self):
        super().update()
        self.rect.move_physics()

### --------------------------------------------------

class Manager_mnkGame(SpriteManager):
    def __init__(self, limits, name = "Board Manager"):
        super().__init__(name)
        board = Sprite_BoardGame_Board("Board")
        cell_size = int(min((limits.height * 0.75) / MNK_ROWS, (limits.width * 0.75) / MNK_COLS))
        colour_scheme = ["white", "blue", None]
        board.setup_grid(colour_scheme, cell_size, MNK_COLS, EventManager.gc_event("Board"), MNK_ROWS, None, 10)
        board.rect.center = limits.center
        self.add(board)
        Sprite_mnkGame_Piece.mnkGame_board = self.sprite("Board")
        
        self._mnk_game = Board_mnkGame(MNK_COLS, MNK_ROWS, MNK_INAROW)
        self._mnk_game.setup()
        self._piece_shape = Sprite_BoardGame_Piece.PIECE_CIRLCE
        self._piece_colours = ["red1", None, "darkgoldenrod1"]
        self._current_piece = None
        self.startup()

        self._next_player = Sprite_mnkGame_Label("Next", limits.width * 0.2, limits.height * 0.95)
        self._next_player.set_text(self._mnk_game.current_player_name)
        self.add(self._next_player)

        self._game_over = Sprite_mnkGame_Winner(limits.width * 0.5, limits.height * 0.5)

        ev_Restart = EventManager.gc_event("StartGame")
        ev_Quit = EventManager.gc_event("Quit")

        self.add(Sprite_mnkGame_Button("Restart", ev_Restart, limits.width * 0.6, limits.height * 0.95))
        self.add(Sprite_mnkGame_Button("Quit", ev_Quit, limits.width * 0.8, limits.height * 0.95))
        
    def startup(self):
        self.remove_by_class("Sprite_mnkGame_Piece")
        self._mnk_game.setup()
        for p in self._mnk_game.pieces:
            self.add_piece(p[0], p[1], p[2])
        self._next_piece = None
        self.prep_next_piece()

    def event(self, e):
        dealt_with = super().event(e)
        if not dealt_with and e.type == EVENT_GAME_CONTROL:
            dealt_with = True
            if e.action == "MouseMotion" and self._mnk_game.in_progress:
                x, y = e.info['pos']
                col, row = self.sprite("Board").find_cell(x, y, True)
                col = max (0, col)
                col = min (MNK_COLS-1, col)
                self._next_piece.set_pos(col, -1)
                dealt_with = True
            elif e.action == "Board" and self._mnk_game.in_progress:
                x, y = e.pos
                col, row = self.sprite("Board").find_cell(x, y)
                if self.play_piece(col) is None:
                    self.prep_next_piece()
            elif e.action == "StartGame":
                self.startup()
                self.remove(self._game_over) # Hide Game Over
                self.add(self._next_player)
            elif e.action == "Print":
                self._mnk_game.print_board()
            else:
                dealt_with = False
        return dealt_with

    def play_piece(self, col):
        changes, go = self._mnk_game.play_piece(col, 0)
        if changes is not None:
            for c in changes:
                if c[3] == "add":
                    self.add_piece(c[0], c[1], c[2])
        if go is not None: # Game Over
            self._game_over.set_text(self._mnk_game.player_name(go))
            self.add(self._game_over)
            self.remove(self._next_piece)
            self.remove(self._next_player)
        return go

    def prep_next_piece(self):
        if self._next_piece is not None:
            self.remove(self._next_piece)
        player = self._mnk_game.current_player_code
        self._next_piece = Sprite_mnkGame_Piece("Next Piece", 3, -1, player)
        self.add(self._next_piece)

    def add_piece(self, col, row, player):
        name = "{0:02d}-{1:02d}".format(col, row)
        piece = Sprite_mnkGame_Piece(name, col, -1, player)
        destination = self.sprite("Board").cell_rect(col, row)
        piece.rect.add_limit(Physics_Limit(destination, LIMIT_OVERLAP, AT_LIMIT_Y_CLEAR_VEL_Y))
        piece.rect.go()
        self._current_piece = name
        self.add(piece)

    def update(self):
        super().update()
        if self._mnk_game.in_progress:
            self.sprite("Next").set_text(self._mnk_game.current_player_name)

### --------------------------------------------------

class BoardGameApp(PyGameApp):
    def init(self):
        super().init()
        pygame.display.set_caption("Board Game")
        self.background_fill = "burlywood"
        self.add_sprite_mgr(Manager_mnkGame(self.boundary))
        self.event_mgr.keyboard_event(pygame.K_q, "Quit")
        self.event_mgr.keyboard_event(pygame.K_p, "Print")
        self.event_mgr.keyboard_event(pygame.K_r, "StartGame")

### --------------------------------------------------

theApp = BoardGameApp()
theApp.execute()
