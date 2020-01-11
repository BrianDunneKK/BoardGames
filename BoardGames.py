import cdkk
import random

class Board:
    def __init__(self, xsize=None, ysize=None):
        self.init_board(xsize, ysize)

    def init_board(self, xsize=None, ysize=None):
        self._pieces = []
        self._size = (xsize, ysize)
        if xsize is not None and ysize is not None:
            for y in range(0,ysize):
                row = []
                for x in range(0,xsize):
                    row.append(".")
                self._pieces.append(row)

    @property
    def xsize(self):
        return self._size[0]

    @property
    def ysize(self):
        return self._size[1]

    def get_piece(self, x, y):
        return self._pieces[y][x]

    def is_piece(self, x, y):
        return (self._pieces[y][x] != ".")

    def is_blank(self, x, y):
        return (self._pieces[y][x] == ".")

    def set_piece(self, x, y, code):
        self._pieces[y][x] = code

    def clear_piece(self, x, y):
        self._pieces[y][x] = "."

    def clear_board(self):
        for y in range(0, len(self._pieces)):
            for x in range(0,len(self._pieces[0])):
                self.clear_piece(x, y)

    def test_piece(self, x, y, value="."):
        return (self._pieces[y][x] == value)

    def test_pieces(self, xy_list, value="."):
        if value is None:
            x, y = xy_list[0]
            value = self.get_piece(x,y)
        found = True
        for xy in xy_list:
            found = found and self.test_piece(xy[0], xy[1], value)
        return found

    def find(self, filter):
        # Filter options: "*" = All pieces, "." = Blank cells, Anything else = Cell contents
        piece_list = []
        for y in range(0, len(self._pieces)):
            for x in range(0,len(self._pieces[0])):
                if filter[0] == "*" and self.is_piece(x,y):
                    piece_list.append([x, y, self.get_piece(x, y)])
                elif filter[0] == "." and not self.is_piece(x,y):
                    piece_list.append([x, y, self.get_piece(x, y)])
                elif filter == self.get_piece(x, y):
                    piece_list.append([x, y, self.get_piece(x, y)])
        return piece_list

    @property
    def pieces(self):
        piece_list = []
        for y in range(0, len(self._pieces)):
            for x in range(0,len(self._pieces[0])):
                if (self.is_piece(x,y)):
                    piece_list.append([x, y, self.get_piece(x, y)])
        return piece_list

    def count_pieces(self, value):
        count = 0
        for y in range(0, len(self._pieces)):
            for x in range(0,len(self._pieces[0])):
                if (self.get_piece(x,y) == value):
                    count += 1
        return count

    def count_blanks(self):
        return self.count_pieces(".")

    def board_to_str(self, rotate=False):
        board_str = ""
        ysize = len(self._pieces)
        xsize = len(self._pieces[0])
        if not rotate:
            board_str = "+" + "-"*xsize*2 + "-+\n"
            for i in range(ysize):
                board_str += "|"
                for j in range(xsize):
                    board_str += " " + self._pieces[i][j]
                board_str += " |\n"
            board_str += "+" + "-"*xsize*2 + "-+"
        else:
            board_str = "+" + "-"*ysize*2 + "-+\n"
            for i in range(xsize):
                board_str += "|"
                for j in range(ysize):
                    board_str += " " + self._pieces[j][i]
                board_str += " |\n"
            board_str += "+" + "-"*ysize*2 + "-+"
        return board_str

    def print_board(self, as_debug=False):
        if not as_debug:
            print(self.board_to_str())
        else:
            ysize = len(self._pieces)
            xsize = len(self._pieces[0])
            cdkk.logger.debug("+"+"-"*xsize*2+"-+")
            for i in range(ysize):
                str = "|"
                for j in range(xsize):
                    str = str + " " + self._pieces[i][j]
                str += " |"
                cdkk.logger.debug(str)
            cdkk.logger.debug("+"+"-"*xsize*2+"-+")

### --------------------------------------------------

class BoardGame(Board):
    def __init__(self, xsize=None, ysize=None, num_players=2):
        self.init_board_game(xsize, ysize, num_players)
    
    def init_board_game(self, xsize=None, ysize=None, num_players=2):
        self.init_board(xsize, ysize)
        self._num_players = num_players
        self._current_player = 1
        self._game_over = False
        self._player_codes = [str(x+1) for x in range(num_players)]
        self._player_names = ["Player {0}".format(x+1) for x in range(num_players)]
        self._current_context = None
        self._turn_num = 0

    @property
    def in_progress(self):
        return not self._game_over

    @property
    def num_players(self):
        return self._num_players

    @property
    def current_player(self):
        return self._current_player

    @property
    def current_context(self):
        return self._current_context

    @property
    def turn_num(self):
        return self._turn_num

    def next_player(self):
        self._current_player = (self._current_player % self._num_players) + 1

    def player_name(self, player_num):
        return self._player_names[player_num-1]

    def player_code(self, player_num):
        return self._player_codes[player_num-1]

    def player_by_code(self, player_code):
        player_num = 0
        i = 1
        for p in self._player_codes:
            if p == player_code and player_num == 0:
                player_num = i    
            else:
                i += 1
        return player_num

    @property
    def current_player_code(self):
        return self.player_code(self._current_player)

    @property
    def current_player_name(self):
        return self.player_name(self._current_player)

    @property
    def winner_code(self):
        if self._current_context["game over"] is None:
            return None
        elif self._current_context["game over"] == 0:
            return "Draw"
        else:
            return self.player_code(self._current_context["game over"])

    @property
    def winner_name(self):
        if self._current_context["game over"] is None:
            return None
        elif self._current_context["game over"] == 0:
            return "Draw"
        else:
            return self.player_name(self._current_context["game over"])

    def set_player_names(self, player_names):
        num = min(self._num_players, len(player_names))
        for i in range(num):
            self._player_names[i] = player_names[i]

    def set_player_codes(self, player_codes):
        num = min(self._num_players, len(player_codes))
        for i in range(num):
            self._player_codes[i] = player_codes[i]

    def start_board_game(self):
        self.clear_board()
        self._current_player = 1
        self._game_over = False
        self._turn_num = 0

    def count_player_pieces(self, player_num):
        return self.count_pieces(self.player_code(player_num))

    def valid_play(self, col, row):
        return col >= 0 and col < self.xsize and row >= 0 and row < self.ysize and not self._game_over

    def calculate_play(self, col, row):
        return (col, row)

    def execute_play(self, col, row):
        self.set_piece(col, row, self.current_player_code)
        consequences = None
        return consequences

    def manage_consequences(self, col, row, consequences):
        pass

    def calculate_changes(self, c, r, consequences):
        changes = []
        changes.append([c, r, self.get_piece(c, r), "add"])
        return changes

    def game_over(self, player_num, col, row):
        # Return: Winner's number; 0 = Draw; None = No winner
        winner = None
        return winner

    def play_piece(self, col=0, row=0, context=None):
        if row is None:
            row = col // self.xsize
            col = col % self.xsize
        self._current_context = cdkk.merge_dicts(context, {"turn":self._turn_num, "changes":None})
        
        c, r = (col, row)
        valid_move = self.valid_play(col, row)
        if valid_move:
            self._turn_num += 1
            c, r = self.calculate_play(col, row)
            consequences = self.execute_play(c,r)
            self.manage_consequences(c, r, consequences)
            self._current_context["changes"] = self.calculate_changes(c, r, consequences)
            p = self.current_player
            self.next_player()
            self._current_context["game over"] = self.game_over(p, c, r)
        else:
            p = None
            self._current_context["game over"] = None

        return self._current_context

### --------------------------------------------------

class Direction:
    def __init__(self, name, xstep, ystep, value):
        self.name = name
        self.xstep = xstep
        self.ystep = ystep
        self.value = value

class Directions:
    n  = Direction("N",  0, -1, 1)
    ne = Direction("NE", 1, -1, 2)
    e  = Direction("E",  1,  0, 4)
    se = Direction("SE", 1,  1, 8)
    s  = Direction("S",  0,  1, 16)
    sw = Direction("SW",-1,  1, 32)
    w  = Direction("W", -1,  0, 64)
    nw = Direction("NW",-1, -1, 128)

    all_dirs =  [n, ne, e, se, s, sw, w, nw]

### --------------------------------------------------

class BoardGame_Reversi(BoardGame):
    def __init__(self, xsize, ysize, names=["Black", "White"]):
        super().__init__(xsize, ysize)
        self.set_player_names(names)

    def start_board_game(self):
        super().start_board_game()
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
        for x,y in flip_list:
            self.flip_piece(x, y)

    def check_move(self, col, row):
        flip_list = []
        if not self.is_piece(col, row):
            for dir in Directions.all_dirs:
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
            if (col<0 or col>=8 or row<0 or row>=8):
                valid = False
            else:
                p = self.get_piece(col, row)
                if p == first:
                    count_first += 1
                    flip_list.append((col,row))
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
        for c,r in consequences:
            changes.append([c, r, self.get_piece(c, r), "flip"])
        return changes

    def game_over(self, player_num, col, row):
        if ( self.count_blanks() == 0 ):
            p1 = self.count_player_pieces(1)
            p2 = self.count_player_pieces(2)
            if p1 > p2:
                return 1
            elif p2 > p1:
                return 2
            else:
                return 0

### --------------------------------------------------

class BoardGame_mnkGame(BoardGame):
    def __init__(self, xsize, ysize, inarow, names=["Red", "Yellow"]):
        super().__init__(xsize, ysize)
        self._inarow = inarow
        self.set_player_names(names)

    def valid_play(self, col, row):
        return ( not self._game_over) and self.is_blank(col, 0)

    def calculate_play(self, col, row):
        # Piece drops to lowest available position
        found_play = False
        for y in range(0, len(self._pieces)):
            if not found_play:
                y2 = len(self._pieces) - y - 1
                if self.is_blank(col, y2):
                    found_play = True
        if found_play:
            return (col, y2)
        else:
            return None

    def game_over(self, player_num, col, row):
        # Return: Winner's number; 0 = Draw; None = No winner
        winner = None
        if not self._game_over:
            for y in range(0, len(self._pieces)):
                for x in range(0,len(self._pieces[0])):
                    for dir in Directions.all_dirs:
                        if winner is None:
                            winner = self.game_over_dir(x, y, dir)
            self._game_over = winner is not None
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
                    still_checking = ( self.get_piece(c, r) == player )

        if still_checking:
            winner = self.player_by_code(player)

        return winner

# --------------------------------------------------


class BoardGame_Mastermind(BoardGame):
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
                    self._code.append(random.randint(0,self._options-1))
            else:
                self._code = random.sample(range(self._options), self._holes)
        else:
            self._code = list(new_code)

    def board_to_str(self, rotate=False):
        # To Do: Rotate not supported
        board_str = ""
        ysize = len(self._pieces)
        xsize = len(self._pieces[0])
        if not rotate:
            board_str = "+" + "-"*(xsize*2+1) + "-+\n"
            for i in range(ysize):
                board_str += "|"
                for j in range(xsize):
                    board_str += " " + self._pieces[i][j]
                    if j == (xsize/2 - 1):
                        board_str += " "
                board_str += " |\n"
            board_str += "+" + "-"*(xsize*2+1) + "-+"
        return board_str

    def calculate_play(self, col, row):
        self._current_context["score"] = self.calculate_score(self.current_context["guess"], self._code)
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
        guess = "".join(str(n) for n in self.current_context["guess"])
        guess_score = guess + self.current_context["score"]
        for i in range(self._holes*2):
            self.set_piece(i, self.turn_num-1, guess_score[i])
        return None

    def game_over(self, player_num, col, row):
        # Return: Winner's number; 0 = Draw; None = No winner
        winner = None

        if self._current_context["score"] == "1111":
            winner = "1" # Code breaker
        elif self.turn_num == self._guesses:
            winner = "2" # Code maker

        self._game_over = (winner is not None)

        return winner

# --------------------------------------------------
