import cdkk
from BoardGames import *

# --------------------------------------------------


class BoardGame_Battleship(BoardGame):
    def __init__(self):
        super().__init__(xsize=10, ysize=10, num_players=2)

    def init_game(self):
        super().init_game()
        self.set_player_names(["Player", "Computer"])

    def draw_game(self):
        self.print_board(prefix="", inc_labels=True)

# --------------------------------------------------


class BoardGame_BattleshipApp(cdkk.cdkkApp):
    def __init__(self):
        app_config = {
            "exit_at_end": True,
            "read_key_and_process": {"match_pattern": "[a-zA-Z]", "as_upper": True}
        }
        super().__init__(app_config)
        self.add_game_mgr(BoardGame_Battleship())


BoardGame_BattleshipApp().execute()
