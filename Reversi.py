# To Do: Drawing Game over text not working
# To Do: Button labels not centered

import sys
sys.path.append("../pygame-cdkk")
from PyGameApp import *
from BoardGames import *

### --------------------------------------------------

class Sprite_Reversi_Button(Sprite_TextBox):
    def __init__(self, name, event_on_click, centerx, centery, event_on_unclick=None):
        super().__init__(name)
        self.text = name
        self.setup_textbox(120, 35, "black", 36, ["gray80", "black"])
        self.setup_mouse_events(event_on_click, event_on_unclick)
        self.rect.center = (centerx, centery)

class Sprite_Reversi_Label(Sprite_TextBox):
    def __init__(self, name, centerx, centery):
        super().__init__(name)
        self.setup_textbox(200, 35, "black", 36)
        self.text_format = name + ": {0}"
        self.rect.center = (centerx, centery)

class Sprite_Reversi_Winner(Sprite_TextBox):
    def __init__(self, centerx, centery):
        super().__init__("Winner")
        self.text_format = "Winner: {0}"
        self.set_text("12345")
        self.rect.center = (centerx, centery)

### --------------------------------------------------

class Manager_Reversi(SpriteManager):
    def __init__(self, limits, name = "Board Manager"):
        super().__init__(name)
        board = Sprite_BoardGame_Board("Board")
        cell_size = int(min((limits.height * 0.8) / 8, (limits.width * 0.8) / 8))
        colour_scheme = ["green", "black", None, "palegreen3"]
        board.setup_grid(colour_scheme, cell_size, 8, EventManager.gc_event("Board"))
        board.rect.center = limits.center
        self.add(board)
        
        self._reversi = Board_Reversi(8,8)
        self._reversi.setup()
        self._piece_shape = Sprite_BoardGame_Piece.PIECE_CIRLCE
        self._piece_colours = ["black", None, "white"]
        self.startup()

        self.add(Sprite_Reversi_Label("Black", limits.width * 0.2, limits.height * 0.05))
        self.sprite("Black").set_text(self._reversi.count_player_pieces(1))

        self.add(Sprite_Reversi_Label("Next", limits.width * 0.5, limits.height * 0.05))
        self.sprite("Next").set_text(self._reversi.current_player_name)

        self.add(Sprite_Reversi_Label("White", limits.width * 0.8, limits.height * 0.05))
        self.sprite("White").set_text(self._reversi.count_player_pieces(2))

        self._game_over = Sprite_Reversi_Winner(limits.width * 0.5, limits.height * 0.5)

        ev_Pass = EventManager.gc_event("Pass")
        ev_Hint = EventManager.gc_event("Hint")
        ev_ClearHint = EventManager.create_event(EVENT_GAME_TIMER_1)
        ev_Restart = EventManager.gc_event("StartGame")
        ev_Quit = EventManager.gc_event("Quit")

        self.add(Sprite_Reversi_Button("Pass", ev_Pass, limits.width * 0.2, limits.height * 0.95))
        self.add(Sprite_Reversi_Button("Hint", ev_Hint, limits.width * 0.4, limits.height * 0.95, ev_ClearHint))
        self.add(Sprite_Reversi_Button("Restart", ev_Restart, limits.width * 0.6, limits.height * 0.95))
        self.add(Sprite_Reversi_Button("Quit", ev_Quit, limits.width * 0.8, limits.height * 0.95))
        
    def startup(self):
        self.remove_by_class("Sprite_BoardGame_Piece")
        self._reversi.setup()
        for p in self._reversi.pieces:
            self.add_piece(p[0], p[1], p[2])

    def event(self, e):
        dealt_with = super().event(e)
        if not dealt_with and e.type == EVENT_GAME_CONTROL:
            dealt_with = True
            if e.action == "Board":
                x, y = e.pos
                col, row = self.sprite("Board").find_cell(x, y)
                self.play_piece(col, row)
            elif e.action == "Pass":
                self._reversi.next_player()
            elif e.action == "StartGame":
                self.startup()
                self.remove(self._game_over) # Hide Game Over
            elif e.action == "Hint":
                moves = self._reversi.next_moves()
                self.sprite("Board").highlight_cells(moves)
                self.timer = Timer(1, EVENT_GAME_TIMER_1)
            elif e.action == "ClearHint":
                self.timer.stop_event()
                moves = self._reversi.next_moves()
                self.sprite("Board").highlight_cells(moves, False)
            elif e.action == "Print":
                self._reversi.print_board()
            else:
                dealt_with = False
        return dealt_with

    def play_piece(self, col, row):
        changes, go = self._reversi.play_piece(col, row)
        if changes is not None:
            for c in changes:
                if c[3] == "add":
                    self.add_piece(c[0], c[1], c[2])
                elif c[3] == "flip":
                    name = "{0:02d}-{1:02d}".format(c[0], c[1])
                    self.sprite(name).flip()
            
        if go is not None:
            self._game_over.set_text(self._reversi.player_name(go))
            self.add(self._game_over)

    def add_piece(self, col, row, player):
        name = "{0:02d}-{1:02d}".format(col, row)
        piece = Sprite_BoardGame_Piece(name, self.sprite("Board"), col, row)
        piece.setup_piece(self._piece_shape, self._piece_colours, (player == '1'))
        self.add(piece)

    def update(self):
        super().update()
        self.sprite("Black").set_text(self._reversi.count_player_pieces(1))
        self.sprite("White").set_text(self._reversi.count_player_pieces(2))
        self.sprite("Next").set_text(self._reversi.current_player_name)

### --------------------------------------------------

class BoardGameApp(PyGameApp):

    def init(self):
        super().init()
        pygame.display.set_caption("Board Game")
        self.background_fill = "burlywood"
        self.add_sprite_mgr(Manager_Reversi(self.boundary))
        self.event_mgr.keyboard_event(pygame.K_q, "Quit")
        self.event_mgr.keyboard_event(pygame.K_p, "Print")
        self.event_mgr.keyboard_event(pygame.K_r, "StartGame")
        self.event_mgr.user_event(EVENT_GAME_TIMER_1, "ClearHint")

### --------------------------------------------------

theApp = BoardGameApp()
theApp.execute()
