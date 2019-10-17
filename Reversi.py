# To Do: "Draw" (no winner) not displayed

import cdkk
import pygame
from BoardGames import *

# --------------------------------------------------


class Sprite_Reversi_Winner(cdkk.Sprite_DynamicText):
    def __init__(self, centerx, centery):
        super().__init__("Winner")
        self.text_format = "Winner: {0}"
        self.set_text("12345")
        self.rect.center = (centerx, centery)

# --------------------------------------------------


class Manager_Reversi(cdkk.SpriteManager):
    def __init__(self, limits, name="Board Manager"):
        super().__init__(name)
        board = cdkk.Sprite_BoardGame_Board(name="Board", style={
                                            "fillcolour": "green", "altcolour": None, "outlinecolour": "black", "outlinewidth": 2})
        cell_size = int(min((limits.height * 0.8) /
                            8, (limits.width * 0.8) / 8))
        board.setup_board_grid(
            cell_size, 8, cdkk.EventManager.gc_event("Board"))
        board.rect.center = limits.center
        self.add(board)

        self._reversi = Board_Reversi(8, 8)
        self._reversi.setup()

        label_style = {"fillcolour": None, "width": 200, "height": 35}
        self._black_score = cdkk.Sprite_DynamicText("Black", style=label_style)
        self._black_score.rect.center = (
            limits.width * 0.2, limits.height * 0.05)
        self._black_score.set_text_format(
            "Black: {0}", self._reversi.count_player_pieces(1))
        self.add(self._black_score)

        self._next_player = cdkk.Sprite_DynamicText("Next", style=label_style)
        self._next_player.rect.center = (
            limits.width * 0.5, limits.height * 0.05)
        self._next_player.set_text_format(
            "Next: {0}", self._reversi.current_player_name)
        self.add(self._next_player)

        self._white_score = cdkk.Sprite_DynamicText("White", style=label_style)
        self._white_score.rect.center = (
            limits.width * 0.8, limits.height * 0.05)
        self._white_score.set_text_format(
            "White: {0}", self._reversi.count_player_pieces(2))
        self.add(self._white_score)

        winner_style = {"textcolour": "red3", "textsize": 64, "fillcolour": "yellow1",
                        "outlinecolour": "red3", "width": 400, "height": 80}
        self._winner = cdkk.Sprite_DynamicText("Winner", style=winner_style)
        self._winner.rect.center = (limits.width * 0.5, limits.height * 0.5)
        self._winner.set_text_format("Winner: {0}", "")

        ev_Pass = cdkk.EventManager.gc_event("Pass")
        ev_Hint = cdkk.EventManager.gc_event("Hint")
        ev_ClearHint = cdkk.EventManager.create_event(cdkk.EVENT_GAME_TIMER_1)
        ev_Restart = cdkk.EventManager.gc_event("StartGame")
        ev_Quit = cdkk.EventManager.gc_event("Quit")

        button_style = {"width": 120, "height": 35}
        self.add(cdkk.Sprite_Button(
            "Pass", event_on_click=ev_Pass, style=button_style))
        self.add(cdkk.Sprite_Button("Hint", event_on_click=ev_Hint,
                                    event_on_unclick=ev_ClearHint, style=button_style))
        self.add(cdkk.Sprite_Button(
            "Restart", event_on_click=ev_Restart, style=button_style))
        self.add(cdkk.Sprite_Button(
            "Quit", event_on_click=ev_Quit, style=button_style))

        self.sprite("Pass").rect.center = (
            limits.width * 0.2, limits.height * 0.95)
        self.sprite("Hint").rect.center = (
            limits.width * 0.4, limits.height * 0.95)
        self.sprite("Restart").rect.center = (
            limits.width * 0.6, limits.height * 0.95)
        self.sprite("Quit").rect.center = (
            limits.width * 0.8, limits.height * 0.95)

    def start_game(self):
        self.remove_by_class("Sprite_BoardGame_Piece")
        self.remove(self._winner)  # Hide Game Over
        self._reversi.setup()
        for p in self._reversi.pieces:
            self.add_piece(p[0], p[1], p[2])

    def event(self, e):
        dealt_with = super().event(e)
        if not dealt_with and e.type == cdkk.EVENT_GAME_CONTROL:
            dealt_with = True
            if e.action == "Board":
                x, y = e.pos
                col, row = self.sprite("Board").find_cell((x, y))
                self.play_piece(col, row)
            elif e.action == "Pass":
                self._reversi.next_player()
            elif e.action == "Hint":
                moves = self._reversi.next_moves()
                self.sprite("Board").highlight_cells(moves)
                self.timer = cdkk.Timer(1, cdkk.EVENT_GAME_TIMER_1)
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
            self._winner.set_text(self._reversi.player_name(go))
            self.add(self._winner)

    def add_piece(self, col, row, player):
        name = "{0:02d}-{1:02d}".format(col, row)
        piece = cdkk.Sprite_BoardGame_Piece(
            name, self.sprite("Board"), col, row)
        if player == "1":
            piece.flip()
        self.add(piece)

    def update(self):
        super().update()
        self.sprite("Black").set_text(self._reversi.count_player_pieces(1))
        self.sprite("White").set_text(self._reversi.count_player_pieces(2))
        self.sprite("Next").set_text(self._reversi.current_player_name)

# --------------------------------------------------


class BoardGameApp(cdkk.PyGameApp):

    def init(self):
        super().init()
        pygame.display.set_caption("Board Game")
        self.background_fill = "burlywood"
        self.add_sprite_mgr(Manager_Reversi(self.boundary))
        key_map = {
            pygame.K_q: "Quit",
            pygame.K_p: "Print",
            pygame.K_r: "StartGame",
            pygame.K_h: "Hint"
        }
        user_event_map = {
            cdkk.EVENT_GAME_TIMER_1: "ClearHint"
        }
        self.event_mgr.event_map(
            key_event_map=key_map, user_event_map=user_event_map)


# --------------------------------------------------

app_config = {
    "width": 1500, "height": 1000,
    "background_fill": "burlywood",
    "caption": "Reversi",
    "auto_start": True
}
BoardGameApp(app_config).execute()
