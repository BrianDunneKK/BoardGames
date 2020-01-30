import cdkk
import random

# --------------------------------------------------

class BoardGame_Reversi(cdkk.BoardGame):
    def __init__(self, xsize, ysize, names=["Black", "White"]):
        super().__init__(xsize, ysize)
        self.set_player_names(names)

    def start_game(self):
        super().start_game()
        self._pieces[3][3] = self.player_code(2)
        self._pieces[3][4] = self.player_code(1)
        self._pieces[4][4] = self.player_code(2)
        self._pieces[4][3] = self.player_code(1)

    def flip_piece(self, x, y):
        if self._pieces[y][x] == self.player_code(1):
            self._pieces[y][x] = self.player_code(2)
        elif self._pieces[y][x] == self.player_code(2):
            self._pieces[y][x] = self.player_code(1)

    def flip_pieces(self, flip_list):
        for x, y in flip_list:
            self.flip_piece(x, y)

    def check_move(self, col, row):
        flip_list = []
        if not self.is_piece(col, row):
            for dir in cdkk.Directions.all_dirs:
                flip_list_dir = self.check_move_dir(col, row, dir)
                for f in flip_list_dir:
                    flip_list.append(f)
        return flip_list

    def check_move_dir(self, piece_col, piece_row, dir):
        valid = True
        count_first = 0
        found_second = False
        col = piece_col
        row = piece_row
        flip_list = []

        if self.current_player == 1:
            first = self.player_code(2)
            second = self.player_code(1)
        else:
            first = self.player_code(1)
            second = self.player_code(2)
        while valid and not found_second:
            col += dir.xstep
            row += dir.ystep
            if (col < 0 or col >= 8 or row < 0 or row >= 8):
                valid = False
            else:
                p = self.get_piece(col, row)
                if p == first:
                    count_first += 1
                    flip_list.append((col, row))
                elif p == second:
                    found_second = True
                else:
                    valid = False
        if (not found_second) or (not valid):
            flip_list.clear()
        return flip_list

    def next_moves(self):
        moves = []
        for p in self.find("."):
            flip_list = self.check_move(p[0], p[1])
            if len(flip_list) > 0:
                moves.append([p[0], p[1], len(flip_list)])
        return moves

    def valid_play(self, col, row):
        flip_list = self.check_move(col, row)
        return len(flip_list) > 0

    def execute_play(self, col, row):
        consequences = self.check_move(col, row)
        super().execute_play(col, row)
        return consequences

    def manage_consequences(self, col, row, consequences):
        self.flip_pieces(consequences)

    def calculate_changes(self, c, r, consequences):
        changes = []
        changes.append([c, r, self.get_piece(c, r), "add"])
        for c, r in consequences:
            changes.append([c, r, self.get_piece(c, r), "flip"])
        return changes

    def check_game_over(self, player_num, col, row):
        if (self.count_blanks() == 0):
            p1 = self.count_player_pieces(1)
            p2 = self.count_player_pieces(2)
            if p1 > p2:
                return 1
            elif p2 > p1:
                return 2
            else:
                return 0

# --------------------------------------------------


class BoardGame_mnkGame(cdkk.BoardGame):
    def __init__(self, xsize, ysize, inarow, names=["Red", "Yellow"]):
        super().__init__(xsize, ysize)
        self._inarow = inarow
        self.set_player_names(names)

    def valid_play(self, col, row):
        return self.game_in_progress and self.is_blank(col, 0)

    def calculate_play(self, col, row):
        # Piece drops to lowest available position
        found_play = False
        for y in range(0, self.ysize):
            if not found_play:
                y2 = self.ysize - y - 1
                if self.is_blank(col, y2):
                    found_play = True
        if found_play:
            return (col, y2)
        else:
            return None

    def check_game_over(self, player_num, col, row):
        # Return: Winner's number; 0 = Draw; None = No winner
        winner = None
        if self.game_in_progress:
            for y in range(0, self.ysize):
                for x in range(0, self.xsize):
                    for dir in cdkk.Directions.all_dirs:
                        if winner is None:
                            winner = self.game_over_dir(x, y, dir)
            self.set_game_over(winner is not None)
        return winner

    def game_over_dir(self, col, row, dir):
        winner = None
        still_checking = self.is_piece(col, row)

        if still_checking:
            player = self.get_piece(col, row)
            for i in range(self._inarow):
                c = col + dir.xstep * i
                r = row + dir.ystep * i
                if c < 0 or r < 0 or c >= self.xsize or r >= self.ysize:
                    still_checking = False
                if still_checking:
                    still_checking = (self.get_piece(c, r) == player)

        if still_checking:
            winner = self.player_by_code(player)

        return winner

# --------------------------------------------------


class BoardGame_Mastermind(cdkk.BoardGame):
    def __init__(self, holes=4, guesses=12, options=6, allow_repeats=False, code=None):
        super().__init__(holes*2, guesses, num_players=1)
        self._holes = holes
        self._guesses = guesses
        self._options = options
        self._allow_repeats = allow_repeats
        self._code = None
        self.code = code

    @property
    def code(self):
        # return "".join(self._code)
        return "".join(str(n) for n in self._code)

    @code.setter
    def code(self, new_code):
        if new_code is None:
            # Random code
            if self._allow_repeats:
                self._code = []
                for i in range(self._holes):
                    self._code.append(random.randint(0, self._options-1))
            else:
                self._code = random.sample(range(self._options), self._holes)
        else:
            self._code = list(new_code)

    def valid_play(self, col, row, check_if_blank=False):
        return super().valid_play(col, row, check_if_blank)

    def calculate_play(self, col, row):
        self.game_set_context("score",
                                self.calculate_score(self.game_get_context("guess"), self._code))
        return (col, row)

    def calculate_score(self, guess, code):
        score = ""

        # Copy lists before changing
        code2 = code.copy()
        guess2 = guess.copy()

        # Check for exact match
        for i in range(self._holes):
            if guess2[i] == code2[i]:
                score += "1"
                guess2[i] = None
                code2[i] = None

        # Check for misplaced match
        for i in range(self._holes):
            if guess2[i] is not None:
                for j in range(self._holes):
                    if code2[j] is not None and guess2[i] == code2[j]:
                        score += "0"
                        guess2[i] = None
                        code2[j] = None

        if len(score) < 4:
            score += " " * (4-len(score))

        return score

    def execute_play(self, col, row):
        guess = "".join(str(n) for n in self.game_get_context("guess"))
        guess_score = guess + self.game_get_context("score")
        for i in range(self._holes*2):
            self.set_piece(i, self.turn_num-1, guess_score[i])
        return None

    def check_game_over(self, player_num, col, row):
        # Return: Winner's number; 0 = Draw; None = No winner
        winner = None

        if self.game_get_context("score") == "1111":
            winner = "1"  # Code breaker
        elif self.turn_num == self._guesses:
            winner = "2"  # Code maker

        self.set_game_over(winner is not None)

        return winner

# --------------------------------------------------
