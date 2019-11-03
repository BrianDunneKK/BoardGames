import random
import cdkk
from hangman_txt import *


class HangmanApp(cdkk.cdkkApp):
    def init(self):
        super().init()
        self.all_words = []
        self.difficulty = 4  # Options: 1..4
        filename = "Words-Grade{}.txt".format(self.difficulty)
        with open(filename) as wordfile:
            for line in wordfile:
                if len(line) > (self.difficulty+3):  # Reject short words (length includes new-line)
                    self.all_words.append(line.strip())

    def start_game(self):
        super().start_game()
        self.mistakes = 0
        self.word = random.choice(self.all_words).upper()
        self.word_list = list(self.word)
        self.word_guess = ["."] * len(self.word)
        self.guesses = ""
        self.draw()

    def manage_events(self):
        self.next_guess = cdkk.getch()

    def update(self):
        self.guesses += self.next_guess
        found = False
        for i in range(len(self.word)):
            if self.next_guess == self.word_list[i]:
                self.word_guess[i] = self.next_guess
                found = True
        if not found:
            self.mistakes += 1

    def draw(self, flip=True):
        print("\n"+hangman_txt[self.mistakes])
        print("    "+"".join(self.word_guess)+"    (Guesses:"+self.guesses+")")

    def manage_loop(self):
        if self.word_list == self.word_guess:
            print("\nYou won!\n")
            self.end_game()
        elif (self.mistakes+1) == len(hangman_txt):
            print("\nYou lost! The word was " + self.word + ".\n")
            self.end_game()

    def end_game(self):
        self.exit_app()

# --------------------------------------------------


HangmanApp().execute()
