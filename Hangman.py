import cdkk
from hangman_txt import *
import random

class BoardGame_Hangman(cdkk.GameManagerMP):
    def __init__(self):
        super().__init__(num_players=2)

    def init_game(self):
        super().init_game()
        self.all_words = []
        self.difficulty = 4  # Options: 1..4
        filename = "BoardGames\\Words-Grade{}.txt".format(self.difficulty)
        with open(filename) as wordfile:
            for line in wordfile:
                if len(line) > (self.difficulty+3):  # Reject short words (length includes new-line)
                    self.all_words.append(line.strip())

    def start_game(self):
        super().start_game()
        self.mistakes = 0
        self.word = random.choice(self.all_words).upper()
        self.word_guess = "." * len(self.word)
        self.guesses = ""

    def process_input(self, input_key):
        if input_key not in self.guesses:
            self.guesses += input_key
            not_found = 1
            for i in range(len(self.word)):
                if input_key == self.word[i]:
                    self.word_guess = self.word_guess[:i] + input_key + self.word_guess[i+1:]
                    not_found = 0
            self.mistakes += not_found

        if self.word == self.word_guess:
            self.winner_num = 1
        elif self.mistakes == (len(hangman_txt)-1):
            self.winner_num = 2

    def draw_game(self):
        print("\n"+hangman_txt[self.mistakes])
        print("    " + self.word_guess + "    (Guesses: " + self.guesses + ")")

    def end_game(self):
        if self.winner_num == 1:
            print("\nYou won!\n")
        else:
            print("\nYou lost! The word was " + self.word + ".\n")
        super().end_game()

# --------------------------------------------------

class HangmanApp(cdkk.cdkkApp):
    def __init__(self):
        app_config = {
            "exit_at_end": True,
            "read_key_and_process": {"match_pattern": "[a-zA-Z]", "as_upper": True}
        }
        super().__init__(app_config)
        self.add_game_mgr(BoardGame_Hangman())

HangmanApp().execute()
