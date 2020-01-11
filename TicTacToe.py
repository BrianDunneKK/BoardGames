import cdkk
from BoardGames import *


class BoardGame_TicTacToe(BoardGame):
    def init_board_game(self, xsize=3, ysize=3, num_players=2):
        super().init_board_game(xsize, ysize, num_players)
        self.set_player_codes(["X", "O"])

    def valid_play(self, col, row):
        return super().valid_play(col, row) and self.is_blank(col, row)

    def game_over(self, player_num, col, row):
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

            if winner is None and len(self.find(".")) == 0:
                winner = 0
        return winner

# --------------------------------------------------


class TicTacToeApp(cdkk.cdkkApp, BoardGame_TicTacToe):
    def init(self):
        super().init()
        self.init_board_game()

    def start_game(self):
        super().start_game()
        self.start_board_game()
        self.draw()

    def manage_events(self):
        print("Turn: "+self.current_player_code)
        self.next_move = cdkk.read_key(digit_only=True, match_pattern="[0-8]")

    def update(self):
        self._outcome = self.play_piece(self.next_move, row=None)

    def manage_loop(self):
        if self._outcome["game over"] is not None:
            self.end_game()

    def draw(self, flip=True):
        print("\n")
        self.print_board()

    def end_game(self):
        print("\nWinner = " + self.winner_name + "\n")
        self.exit_app()

# --------------------------------------------------


ttt = TicTacToeApp()
ttt.execute()
