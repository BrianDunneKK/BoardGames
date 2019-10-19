import cdkk
from BoardGames import *

mm = BoardGame_Mastermind(guesses=3)
print(mm.to_str()+"\n")
# print(mm.code)
while(mm.in_progress):
    code_guess = input("Enter your 4-digit guess: ")
    (ch, go) = mm.play_piece(context={"guess": code_guess})
    print(mm.to_str()+"\n")
    if go == "1":
        print("Congrats ... You won!\n")
    elif go == "2":
        print("Hard luck ... You lost. The code was " + mm.code + ".\n")
