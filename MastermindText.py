from BoardGames import *

mm = BoardGame_Mastermind()  # holes=4, guesses=12, options=6, code=None
print(mm.to_str()+"\n")
while(mm.in_progress):
    code_guess = input("Enter your 4-digit guess: ")
    (ch, go) = mm.play_piece(context={"guess": code_guess})
    print(mm.to_str()+"\n")
    if go == "1":
        print("Congrats ... You won!\n")
    elif go == "2":
        print("Hard luck ... You lost. The code was " + mm.code + ".\n")
