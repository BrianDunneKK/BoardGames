import sys
sys.path.insert(0, "cdkk")
import cdkk
import pygame
from BoardGames import *


MM_HOLES = 4
MM_GUESSES = 12
MM_OPTIONS = 6

# --------------------------------------------------


class Sprite_Peg(cdkk.Sprite_Shape):
    default_style = {
        "fillcolour": None, "outlinecolour": "black", "outlinewidth": 1, "shape": "Ellipse"}

    def __init__(self, rect, colour, ev_click=None, style=None):
        super().__init__("Peg", rect, style=cdkk.merge_dicts(
            Sprite_Peg.default_style, {"fillcolour": colour}, style))
        self.setup_mouse_events(ev_click)


class Sprite_CodePeg(Sprite_Peg):
    colours = ["red2", "blue", "yellow1", "green3", "magenta", "orange",
               "black", "darkorchid3", "gray50"]

    def __init__(self, rect, code=None, ev_click=None, enable=True):
        colour = None if code is None else Sprite_CodePeg.colours[code]
        style = {} if enable else { "outlinecolour":"gray50"}
        super().__init__(rect, colour, ev_click, style)


class Sprite_ScorePeg(Sprite_Peg):
    colours = ["black", "white"]

    def __init__(self, rect, score=None):
        colour = None if score is None else Sprite_ScorePeg.colours[score]
        style = None if colour is not None else {
            "outlinecolour": "sepia", "shape": "Rectangle"}
        super().__init__(rect, colour, style=style)


class Sprite_PegPicker(Sprite_CodePeg):
    def __init__(self, rect):
        super().__init__(rect, None)
        self._selection = None

    @property
    def selection(self):
        return self._selection

    @selection.setter
    def selection(self, new_selection):
        self._selection = new_selection
        if new_selection is not None:
            self.set_style("fillcolour", Sprite_CodePeg.colours[new_selection])
        else:
            self.set_style("fillcolour", None)


class Sprite_CodePeg_Set(cdkk.SpriteGridSet):
    def __init__(self, guess, rect, xcols=None, yrows=1, evl_click=None, enable_num=None):
        if xcols is None:
            xcols = len(guess)
        super().__init__("Guess", rect, xcols, yrows, margin=10)
        for i in range(xcols):
            for j in range(yrows):
                offset = i+j*xcols
                enable = True if enable_num is None else (j==enable_num)
                guess_peg = None if guess is None else guess[offset]
                ev_click = None if evl_click is None else evl_click[offset]
                peg = Sprite_CodePeg(rect, guess_peg, ev_click, enable)
                self.add_shape_xy(peg, i, j)


class Sprite_ScorePeg_Set(cdkk.SpriteGridSet):
    def __init__(self, scores, rect, xcols, yrows):
        super().__init__("Score", rect, xcols, yrows, margin=2)
        for i in range(xcols):
            for j in range(yrows):
                offset = i+j*xcols
                score_peg = None if scores is None else scores[offset]
                peg = Sprite_ScorePeg(rect, score_peg)
                self.add_shape_xy(peg, i, j)

# --------------------------------------------------


class Manager_Mastermind(cdkk.SpriteManager):
    def __init__(self, limits, name="Board Manager"):
        super().__init__(name)
        self._mm_game = BoardGame_Mastermind(MM_HOLES, MM_GUESSES, MM_OPTIONS)

        # --- Set up the board
        self.cp_hole_size = int(min((limits.height * 0.9) / MM_GUESSES,
                                    (limits.width * 0.9) / MM_HOLES))

        self._board_rect = cdkk.cdkkRect(0, 0, (self.cp_hole_size+self.sp_hole_size)*MM_HOLES + 10,
                                         self.cp_hole_size*MM_GUESSES+10)
        self._board_rect.center = limits.center
        codes_rect = cdkk.cdkkRect(self._board_rect.left + 20, self._board_rect.top + 10,
                                   self.cp_hole_size*MM_HOLES, self.cp_hole_size*MM_GUESSES)

        self.add(cdkk.Sprite_Shape("Board Background", self._board_rect,
                                   {"fillcolour": "tan4", "outlinecolour": None}))

        evl_click = []
        for i in range(MM_GUESSES):
            for j in range(MM_HOLES):
                evl_click.append(cdkk.EventManager.gc_event(
                    "SelectPegHole", guess=(i, j)))
        self.add(Sprite_CodePeg_Set(None, codes_rect,
                                    MM_HOLES, MM_GUESSES, evl_click, self._mm_game.turn_num))

        for i in range(MM_GUESSES):
            self.add(Sprite_ScorePeg_Set(None, self.score_pegs_rect(i),
                                         xcols=int((MM_HOLES+1)/2), yrows=2))

        # --- Peg choice options and picker
        options = [i for i in range(MM_OPTIONS)]
        evl_click = [cdkk.EventManager.gc_event(
            "SelectPeg", guess=i) for i in range(MM_OPTIONS)]
        options_rect = cdkk.cdkkRect(limits.left+limits.width*0.2,
                                     limits.top+limits.height/2-self.cp_hole_size*MM_OPTIONS/2,
                                     self.cp_hole_size-10, self.cp_hole_size*MM_OPTIONS)
        self.add(Sprite_CodePeg_Set(
            options, options_rect, 1, MM_OPTIONS, evl_click))

        self._peg_picker = Sprite_PegPicker(self.code_peg_rect(0, 0))
        self.add(self._peg_picker)

        # --- Set up controls
        button_height = 35
        rect = cdkk.cdkkRect(self._board_rect.right + 100,
                             limits.height/2, 120, button_height)

        ev_Guess = cdkk.EventManager.gc_event("GuessCode")
        rect.bottom = limits.height/2 - button_height*2
        self.add(cdkk.Sprite_Button("Guess", rect, ev_Guess))

        ev_Restart = cdkk.EventManager.gc_event("StartGame")
        rect.centery = limits.height/2
        self.add(cdkk.Sprite_Button("Restart", rect, ev_Restart))

        ev_Quit = cdkk.EventManager.gc_event("Quit")
        rect.top = limits.height/2 + button_height*2
        self.add(cdkk.Sprite_Button("Quit", rect, ev_Quit))

        # rect = cdkk.cdkkRect(50, self._board_rect.top,
        #                      self._board_rect.left-100, 80)
        # self.add(cdkk.Sprite_TextBox("Instructions", rect,
        #                              {"textcolour": "black", "textsize": 40, "fillcolour": "yellow1", "outlinecolour": "black"}))

        winner_style = {"textcolour": "red3", "textsize": 48, "fillcolour": "yellow1",
                        "outlinecolour": "red3", "width": 400, "height": 80}
        self._winner = cdkk.Sprite_DynamicText("Winner", rect=cdkk.cdkkRect(
            limits.width/2-200, 25, 400, 70), style=winner_style)
        self._winner.set_text_format("Winner: {0}", "")

        self.start_game()

        # Fill all holes
        # guesses = [random.randint(0, MM_OPTIONS-1)
        #            for i in range(MM_GUESSES*MM_HOLES)]
        # self.add(Sprite_CodePeg_Set(guesses, codes_rect, MM_HOLES, MM_GUESSES))
        # for i in range(MM_GUESSES):
        #     score = []
        #     for j in range(MM_HOLES):
        #         if random.randint(0, 2) == 0:
        #             score.append(random.randint(0, 1))
        #         else:
        #             score.append(None)
        #     # self.add(Sprite_ScorePeg_Set(score, self.score_peg_rl(i)))

    @property
    def cp_hole_size(self):
        # Code Peg Hole Size (includes margin)
        return self._cp_hole_size

    @property
    def sp_hole_size(self):
        # Score Peg Hole Size (includes margin)
        return int((self.cp_hole_size-10)*0.35)

    @cp_hole_size.setter
    def cp_hole_size(self, new_hole_size):
        self._cp_hole_size = new_hole_size

    def code_peg_rect(self, guess, peg):
        return cdkk.cdkkRect(self._board_rect.left + self.cp_hole_size*peg + 20,
                             self._board_rect.top + self.cp_hole_size*guess + 10,
                             self.cp_hole_size-10, self.cp_hole_size-10)

    def score_pegs_rect(self, guess):
        rect = cdkk.cdkkRect(self._board_rect.left + self.cp_hole_size*MM_HOLES + 30,
                             self._board_rect.top + self.cp_hole_size*guess +
                             10 + self.cp_hole_size/2 - self.sp_hole_size,
                             self.sp_hole_size*2-2, self.sp_hole_size*2-2)
        return rect

    # def score_peg_rect(self, guess, peg):
    #     rect = self.code_peg_rect(guess, MM_HOLES-1)
    #     rect.left = rect.right + 30
    #     rect.top = rect.centery - 2 - self.sp_hole_size
    #     rect.size = (self.sp_hole_size-2, self.sp_hole_size-2)

    #     if peg < MM_HOLES/2:
    #         rect.top = rect.bottom + 4

    #     peg = peg % int((MM_HOLES+1)/2)
    #     rect.left += self.sp_hole_size * peg

    #     return rect

    def start_game(self):
        super().start_game()
        self.remove(self._winner)  # Hide Game Over

    def end_game(self):
        self.add(self._winner)
        super().end_game()

    def event(self, e):
        dealt_with = super().event(e)
        if e.type == cdkk.EVENT_GAME_CONTROL:
            if e.action == "MouseMotion":
                x, y = e.info["pos"]
                if x > self._board_rect.right:
                    self._peg_picker.invisible = True
                else:
                    self._peg_picker.invisible = False
                    self._peg_picker.rect.move_to(x, y)
                dealt_with = True
            elif e.action == "SelectPeg":
                self._peg_picker.selection = e.info["guess"]
            elif e.action == "SelectPegHole":
                (guess, hole) = e.info["guess"]
                self._peg_picker.selection = None

        return dealt_with

# --------------------------------------------------


class BoardGameApp(cdkk.PyGameApp):
    def init(self):
        super().init()
        self.add_sprite_mgr(Manager_Mastermind(self.boundary))
        key_map = {
            pygame.K_q: "Quit",
            pygame.K_r: "StartGame"
        }
        self.event_mgr.event_map(key_event_map=key_map)

# --------------------------------------------------


app_config = {
    # "full_screen": True,
    "background_fill": "gray65",
    "caption": "Mastermind",
    "image_path": "BoardGames\\Images\\"
}
theApp = BoardGameApp(app_config)
theApp.execute()
