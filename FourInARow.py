import sys
sys.path.append("../pygame-cdkk")
from cdkkPyGameApp import *
from cdkkSpriteExtra import *
from BoardGames import *

MNK_COLS = 7   # m
MNK_ROWS = 6   # n
MNK_INAROW = 4 # k

### --------------------------------------------------

class Sprite_mnkGame_Piece(Sprite_BoardGame_Piece):
    default_style = { "fillcolour":"red1", "altcolour":"darkgoldenrod1", "piecemargin":5}
    mnkGame_board = None

    def __init__(self, name, col, row, player):
        super().__init__(name, self.mnkGame_board, col, row, Sprite_mnkGame_Piece.default_style)
        self.rect.set_acceleration(0, self.rect.gravity*2)
        self.rect.multiplier = 100
        if player != '1':
            self.flip()

    def update(self):
        super().update()
        self.rect.move_physics()

### --------------------------------------------------

class Manager_mnkGame(SpriteManager):
    def __init__(self, limits, name = "Board Manager"):
        super().__init__(name)
        board = Sprite_BoardGame_Board("Board", {"fillcolour":None, "altcolour":None, "fillimage":"Images/board.png", "outlinecolour":None})
        # board = Sprite_BoardGame_Board("Board")
        cell_size = int(min((limits.height * 0.75) / MNK_ROWS, (limits.width * 0.75) / MNK_COLS))
        board.setup_grid(cell_size, MNK_COLS, EventManager.gc_event("Board"), MNK_ROWS, None)
        board.rect.center = limits.center
        self.add(board, layer=9)
        Sprite_mnkGame_Piece.mnkGame_board = board
        
        self._mnk_game = Board_mnkGame(MNK_COLS, MNK_ROWS, MNK_INAROW)
        self._mnk_game.setup()
        self._current_piece = None

        _next_player_style = {"fillcolour":None, "align_horiz":"L"}
        self._next_player = Sprite_DynamicText("Next", cdkkRect(limits.width * 0.3, limits.height * 0.9, 150, 35), style=_next_player_style)
        self._next_player.set_text_format("Next: {0}", "")
        self.add(self._next_player)

        winner_style = { "textcolour":"red3", "textsize":48, "fillcolour":"yellow1", "outlinecolour":"red3", "shapewidth":400, "shapeheight":80}
        self._winner = Sprite_DynamicText("Winner", rect=cdkkRect(limits.width/2-200, 25, 400, 70), style=winner_style)
        self._winner.set_text_format("Winner: {0}", "")

        ev_Restart = EventManager.gc_event("StartGame")
        ev_Quit = EventManager.gc_event("Quit")
        rect = cdkkRect(limits.width * 0.5, limits.height * 0.9, 120, 35)
        self.add(Sprite_Button("Restart", rect, ev_Restart))
        rect.left = limits.width * 0.65
        self.add(Sprite_Button("Quit", rect, ev_Quit))

        self.start_game()

    def start_game(self):
        super().start_game()
        self.remove_by_class("Sprite_mnkGame_Piece")
        self._mnk_game.setup()
        for p in self._mnk_game.pieces:
            self.add_piece(p[0], p[1], p[2])
        self._next_piece = None
        self.prep_next_piece()
        self.remove(self._winner) # Hide Game Over
        self.add(self._next_player)

    def end_game(self):
        self.add(self._winner)
        self.remove(self._next_piece)
        self.remove(self._next_player)
    
    def event(self, e):
        dealt_with = super().event(e)
        if not dealt_with and e.type == EVENT_GAME_CONTROL:
            dealt_with = True
            if e.action == "MouseMotion" and self.game_is_active:
                x, y = e.info['pos']
                col, row = self.sprite("Board").find_cell(x, y, True)
                col = max (0, col)
                col = min (MNK_COLS-1, col)
                self._next_piece.set_pos(col, -1)
                dealt_with = True
            elif e.action == "Board" and self.game_is_active:
                x, y = e.pos
                col, row = self.sprite("Board").find_cell(x, y)
                if self.play_piece(col) is None:
                    self.prep_next_piece()
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
            self._winner.set_text(self._mnk_game.player_name(go))
            EventManager.post_game_control("GameOver")
        return go

    def prep_next_piece(self):
        if self._next_piece is not None:
            self.remove(self._next_piece)
        player = self._mnk_game.current_player_code
        print("Prep next piece piece: {0}".format(player))
        self._next_piece = Sprite_mnkGame_Piece("Next Piece", 3, -1, player)
        self.add(self._next_piece)

    def add_piece(self, col, row, player):
        name = "{0:02d}-{1:02d}".format(col, row)
        print("Add piece: {0}".format(player))
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
        super().init(fullscreen=True)
        pygame.display.set_caption("Board Game")
        self.background_fill = "burlywood"
        self.add_sprite_mgr(Manager_mnkGame(self.boundary))
        self.event_mgr.keyboard_event(pygame.K_q, "Quit")
        self.event_mgr.keyboard_event(pygame.K_p, "Print")
        self.event_mgr.keyboard_event(pygame.K_r, "StartGame")

### --------------------------------------------------

theApp = BoardGameApp()
theApp.execute()
