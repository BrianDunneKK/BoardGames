import cdkk

# --------------------------------------------------

class BoardGame_TicTacToe(cdkk.BoardGame):
    def __init__(self):
        super().__init__(xsize=3, ysize=3, num_players=2)

    def init_game(self):
        super().init_game()
        self.set_player_codes(["X", "O"])

    def process_input(self, selection):
        self.play_piece(selection, row=None)
        return True

    def check_game_over(self, player_num, col, row):
        # Return: Winner's number; 0 = Draw; None = No winner
        winner = None
        curr_player = self.player_code(player_num)
        if not self._game_over:
            win_lines = [[(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1), (1, 2)],
                         [(2, 0), (2, 1), (2, 2)], [(0, 0), (1, 0), (2, 0)],
                         [(0, 1), (1, 1), (2, 1)], [(0, 2), (1, 2), (2, 2)],
                         [(0, 0), (1, 1), (2, 2)], [(2, 0), (1, 1), (0, 2)]]
            for win in win_lines:
                if self.test_pieces(win, curr_player) and winner is None:
                    winner = player_num

            if winner is None and len(self.find(".")) == 0:  # Check for draw
                winner = 0
        return winner

    def draw_game(self):
        self.print_board(prefix="",
                         suffix="Turn: "+self.current_player_code if self.game_in_progress else None)

    def end_game(self):
        print("\nWinner = " + self.winner_code + "\n")
        super().end_game()

# --------------------------------------------------

class TicTacToeApp(cdkk.cdkkApp):
    def __init__(self):
        app_config = {
            "exit_at_end": True,
            "read_key_and_process": {"as_int": True, "match_pattern": "[0-8]"}
        }
        super().__init__(app_config)
        self.add_game_mgr(BoardGame_TicTacToe())

TicTacToeApp().execute()
