import cdkk
import pygame
from BoardGames import *

MM_HOLES = 4
MM_TURNS = 12
MM_OPTIONS = 6

# --------------------------------------------------


class Sprite_CodePeg(cdkk.Sprite_Shape):
    default_style = {"fillcolour": None, "outlinecolour": "gray50",
                     "outlinewidth": 1, "shape": "Ellipse"}
    colours = ["red2", "blue", "yellow1", "green3", "magenta", "orange",
               "black", "darkorchid3", "gray50"]

    def __init__(self, rect, ev_click=None, turn=None):
        super().__init__("CodePeg", rect, style=Sprite_CodePeg.default_style)
        self.setup_mouse_events(ev_click)
        self._code = None
        self.set_desc("turn", turn)

    def enable(self, enable=True):
        outline = "black" if enable else "gray50"
        self.set_style("outlinecolour", outline)

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, new_code):
        self._code = new_code
        fill = None if new_code is None else Sprite_CodePeg.colours[new_code]
        self.set_style("fillcolour", fill)
        self.draw(cdkk.Sprite.DRAW_AFTER_CLEAR)


class Sprite_ScorePeg(cdkk.Sprite_Shape):
    default_style = {"fillcolour": None, "outlinecolour": "sepia",
                     "outlinewidth": 1, "shape": "Rectangle"}
    colours = ["white", "black"]

    def __init__(self, rect, turn=None):
        super().__init__("ScorePeg", rect, style=Sprite_ScorePeg.default_style)
        self._score = None
        self.set_desc("turn", turn)

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, new_score):
        self._score = int(new_score) if new_score != " " else -1
        fill = None if self.score < 0 else Sprite_ScorePeg.colours[self.score]
        self.set_style("fillcolour", fill)
        self.draw(cdkk.Sprite.DRAW_AFTER_CLEAR)


class Sprite_CodePeg_Set(cdkk.SpriteGridSet):
    def __init__(self, turn, rect, xcols, yrows=1, evl_click=None, peg_name=None):
        super().__init__("GuessPegs", rect, xcols, yrows, margin=10)
        for i in range(xcols):
            for j in range(yrows):
                offset = i+j*xcols
                ev_click = None if evl_click is None else evl_click[offset]
                peg = Sprite_CodePeg(rect, ev_click, turn)
                if peg_name is not None:
                    peg.set_desc("name", peg_name)
                self.add_shape_xy(peg, i, j)

    def update(self, guess):
        for i in range(len(guess)):
            x = i % self.xcols
            y = (i - x) // self.xcols
            s = self.find_shape_xy(x, y)
            s.code = guess[i]

    def enable(self, enable=True):
        for s in self.sprites():
            s.enable()


class Sprite_ScorePeg_Set(cdkk.SpriteGridSet):
    def __init__(self, turn, rect, xcols, yrows):
        super().__init__("ScorePegs", rect, xcols, yrows, margin=2)
        for i in range(xcols):
            for j in range(yrows):
                offset = i+j*xcols
                peg = Sprite_ScorePeg(rect, turn)
                self.add_shape_xy(peg, i, j)

    def update(self, score):
        for i in range(len(score)):
            x = i % self.xcols
            y = (i - x) // self.yrows
            s = self.find_shape_xy(x, y)
            s.score = score[i]

# --------------------------------------------------


class Manager_Mastermind(cdkk.SpriteManager):
    def __init__(self, limits, name="Board Manager"):
        super().__init__(name)
        self._mm_game = BoardGame_Mastermind(MM_HOLES, MM_TURNS, MM_OPTIONS)

        # --- Set up the board
        self.cp_hole_size = int(min((limits.height * 0.9) / MM_TURNS,
                                    (limits.width * 0.9) / MM_HOLES))

        self._board_rect = cdkk.cdkkRect(
            0, 0, (self.cp_hole_size+self.sp_hole_size)*MM_HOLES + 10, self.cp_hole_size*MM_TURNS+10)
        self._board_rect.center = limits.center
        self.add(cdkk.Sprite_Shape("Board Background", self._board_rect, {
                 "fillcolour": "tan4", "outlinecolour": None}))

        # --- Set up each turn
        for i in range(MM_TURNS):
            evl_click = []
            for j in range(MM_HOLES):
                evl_click.append(cdkk.EventManager.gc_event("PlaceCodePeg",
                                                            guess=(i, j)))

            self.add(Sprite_CodePeg_Set(i, self.code_peg_rect(
                i), MM_HOLES, evl_click=evl_click))
            self.add(Sprite_ScorePeg_Set(i, self.score_pegs_rect(i),
                                         int((MM_HOLES+1)/2), 2))

        # --- Code peg options and picker
        options = [i for i in range(MM_OPTIONS)]
        evl_click = [cdkk.EventManager.gc_event(
            "SelectCodePeg", guess=i) for i in range(MM_OPTIONS)]
        options_rect = cdkk.cdkkRect(limits.left+limits.width*0.2,
                                     limits.top+limits.height/2-self.cp_hole_size*MM_OPTIONS/2,
                                     self.cp_hole_size-10, self.cp_hole_size*MM_OPTIONS)
        cp = Sprite_CodePeg_Set(999, options_rect, 1,
                                MM_OPTIONS, evl_click, "CodePegOptions")
        cp.update(options)
        self.add(cp)

        self._peg_picker = Sprite_CodePeg(self.code_peg_rect(0, 0))
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

        self._winner = cdkk.Sprite_GameOver(limits)

        self.start_game()

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

    def code_peg_rect(self, turn, peg=None):
        if peg is None:
            return cdkk.cdkkRect(self._board_rect.left + 20,
                                 self._board_rect.top + self.cp_hole_size*turn + 10,
                                 self.cp_hole_size*MM_HOLES, self.cp_hole_size-10)
        else:
            return cdkk.cdkkRect(self._board_rect.left + self.cp_hole_size*peg + 20,
                                 self._board_rect.top + self.cp_hole_size*turn + 10,
                                 self.cp_hole_size-10, self.cp_hole_size-10)

    def score_pegs_rect(self, turn):
        rect = cdkk.cdkkRect(self._board_rect.left + self.cp_hole_size*MM_HOLES + 30,
                             self._board_rect.top + self.cp_hole_size*turn +
                             10 + self.cp_hole_size/2 - self.sp_hole_size,
                             self.sp_hole_size*2-2, self.sp_hole_size*2-2)
        return rect

    def clear_guess(self):
        self._current_guess = [None] * MM_HOLES

    def set_guess(self, guess, hole, option):
        if guess == self._mm_game.turn_num:
            self._current_guess[hole] = option
            self._current_codes.update(self._current_guess)
        return (guess == self._mm_game.turn_num)

    def find_current_pegs(self):
        self._current_codes = None
        self._current_scores = None

        sprites = self.find_sprites_by_desc("name", "CodePeg",
                                            "turn", self._mm_game.turn_num)
        if len(sprites) > 0:
            for grp in sprites[0].groups():
                if isinstance(grp, Sprite_CodePeg_Set):
                    self._current_codes = grp
        if self._current_codes is not None:
            self._current_codes.enable()

        sprites = self.find_sprites_by_desc("name", "ScorePeg",
                                            "turn", self._mm_game.turn_num)
        if len(sprites) > 0:
            for grp in sprites[0].groups():
                if isinstance(grp, Sprite_ScorePeg_Set):
                    self._current_scores = grp

    def clear_board(self):
        self.remove(self._winner)
        for s in self.find_sprites_by_desc("name", "CodePeg"):
            s.code = None
            s.enable(False)

        for s in self.find_sprites_by_desc("name", "ScorePeg"):
            s.score = " "

    def start_game(self):
        self.clear_board()
        super().start_game()
        self._mm_game.start_game()
        self.clear_guess()
        self._current_codes = None
        self.find_current_pegs()

    def end_game(self):
        if self._mm_game.current_context["game over"] == "1":
            self._winner.text = "You won!"
        else:
            self._winner.text = "You lost!"
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
            elif e.action == "SelectCodePeg":
                self._peg_picker.code = e.info["guess"]
            elif e.action == "PlaceCodePeg":
                (guess, hole) = e.info["guess"]
                if self.set_guess(guess, hole, self._peg_picker.code):
                    self._peg_picker.code = None
            elif e.action == "GuessCode":
                outcome = self._mm_game.play_piece(
                    context={"guess": self._current_guess})
                self._current_scores.update(outcome["score"])
                if outcome["game over"] is None:
                    self.clear_guess()
                    self.find_current_pegs()
                    print(self._mm_game.to_str()+"\n")
                    print(self._mm_game.code)
                else:
                    cdkk.EventManager.post_game_control("GameOver")

        return dealt_with

# --------------------------------------------------


class BoardGameApp(cdkk.PyGameApp):
    def init(self):
        super().init()
        self.add_sprite_mgr(Manager_Mastermind(self.boundary))
        key_map = {
            pygame.K_q: "Quit",
            pygame.K_s: "StartGame"
        }
        self.event_mgr.event_map(key_event_map=key_map)

# --------------------------------------------------


app_config = {
    "background_fill": "gray65",
    "caption": "Mastermind",
    "image_path": "BoardGames\\Images\\"
}
theApp = BoardGameApp(app_config)
theApp.execute()
