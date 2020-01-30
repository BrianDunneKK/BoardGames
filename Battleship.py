import cdkk

# --------------------------------------------------


class BoardGame_Battleship(cdkk.BoardGame):
    ships_cfg = {
        "Aircraft Carrier": 5,
        "Battleship": 4,
        "Cruiser": 3,
        "Submarine": 3,
        "Destroyer": 2
    }

    def __init__(self, grid_size=10):
        super().__init__(xsize=grid_size, ysize=grid_size, num_players=2)
        self._guess_board = cdkk.Board(grid_size, grid_size)
        self.ships = []

    def init_game(self):
        super().init_game()
        self.set_player_names(["Player", "Computer"])

    def start_game(self):
        super().start_game()
        self._guess_board.clear_board()
        for name, size in BoardGame_Battleship.ships_cfg.items():
            ship = self.set_random(code=name[0], num=size)
            ship["sunk"] = False
            self.ships.append(ship)

    def process_input(self, keys):
        if keys is not None:
            xcol, yrow = cdkk.Board.a1_to_xy(keys)
            self.play_piece(xcol, yrow, context=None)
        return (keys is not None)

    def valid_play(self, col=None, row=None, check_if_blank=True):
        return self.valid_cell(col, row)

    def execute_play(self, col, row, code=None):
        code = 'x' if self.is_blank(col, row) else '█'
        if code == 'x':
            super().execute_play(col, row, code)
        self._guess_board.set_piece(col, row, code)
        return None

    def manage_consequences(self, *args):
        for ship in self.ships:
            if self._guess_board.is_code(ship["xpos"], ship["ypos"], '█', xcols=ship["xcols"], yrows=ship["yrows"]):
                self._guess_board.set_piece(ship["xpos"], ship["ypos"],
                                            ship["code"], xcols=ship["xcols"], yrows=ship["yrows"])
                ship["sunk"] = True

    def check_game_over(self, player_num, col, row):
        winner = None

        if len(self.find(".")) < len(self.find("x")):
            winner = 2      # Less spaces than misses - You lost

        all_sunk = True
        for ship in self.ships:
            if not ship["sunk"]:
                all_sunk = False
        if all_sunk:
            winner = 1      # All sunk - You won

        return winner

    def draw_game(self):
        # Board.print_boards([self._guess_board, self], prefix="", inc_labels=True)
        self._guess_board.print_board(prefix="", inc_labels=True)

    def end_game(self):
        print("\nWinner = " + self.winner_name + "\n")
        super().end_game()

# --------------------------------------------------


class BoardGame_BattleshipApp(cdkk.cdkkApp):
    def __init__(self):
        app_config = {
            "exit_at_end": True,
            "read_key_and_process": {"match_pattern": "[a-jA-J][0-9]", "as_upper": True, "multi_key": True}
        }
        super().__init__(app_config)
        self.add_game_mgr(BoardGame_Battleship())


BoardGame_BattleshipApp().execute()
