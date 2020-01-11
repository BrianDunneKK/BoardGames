from BoardGames import *

mm = BoardGame_Mastermind()  # holes=4, guesses=12, options=6, code=None
print(mm.board_to_str()+"\n")
while(mm.in_progress):
    code_guess = input("Enter your 4-digit guess: ")
    code_list = [int(n) for n in list(code_guess)] 
    outcome = mm.play_piece(context={"guess": code_list})
    print(mm.board_to_str()+"\n")
    if outcome["game over"] == "1":
        print("Congrats ... You won!\n")
    elif outcome["game over"] == "2":
        print("Hard luck ... You lost. The code was " + mm.code + ".\n")
