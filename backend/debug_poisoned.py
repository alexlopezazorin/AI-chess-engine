import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "app"))

from Chess.ChessEngine import GameState, AI

game = GameState()
game.board = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, -1, 0, 0],
    [0, 0, 0, 0, 0, -5, 0, 0],
    [-100, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 9, -1],
    [100, 0, 0, 0, 0, 0, 0, 0]
]
game.human_is_white = False

print("=" * 80)
print("BOARD ANALYSIS")
print("=" * 80)
print("\nPieces:")
print("- Queen (white) at [6, 6]")
print("- Pawn (black) at [6, 7] - FREE PAWN")
print("- Rook (black) at [4, 5] - DEFENDED BY PAWN AT [3, 5]")
print("- King (black) at [5, 0]")
print("- King (white) at [7, 0]")

print("\n" + "=" * 80)
print("VALID MOVES FROM QUEEN")
print("=" * 80)

from Chess.ChessEngine import Piece

queen = Piece(game.board[6][6])
valid_moves = queen.get_valid_moves([6, 6], game.board, game)
print(f"\nQueen at [6, 6] has {len(valid_moves)} possible moves:")
for move in sorted(valid_moves):
    target = game.board[move[0]][move[1]]
    capture = "CAPTURES" if target != 0 else "EMPTY"
    print(f"  [6, 6] -> {move}  ({capture})")

print("\n" + "=" * 80)
print("EVALUATING TOP MOVES")
print("=" * 80)

move_scores = []

for move in valid_moves:
    game.make_move([6, 6], move)
    score = AI(game).evaluation_function(True)
    move_scores.append((move, score))
    game.undo_move()

move_scores.sort(key=lambda x: x[1], reverse=True)

print("\nTop 5 moves by evaluation:")
for i, (move, score) in enumerate(move_scores[:5]):
    target = game.board[move[0]][move[1]]
    capture_str = f"captures {target}" if target != 0 else "empty square"
    print(f"{i+1}. [6, 6] -> {move}  ({capture_str}) = {score}")

# Specifically check the two important moves
print("\n" + "=" * 80)
print("SPECIFIC MOVES OF INTEREST")
print("=" * 80)

qa1_score = None
qh5_score = None

for move, score in move_scores:
    if move == [6, 7]:
        qa1_score = score
        print(f"Take free pawn [6, 6] -> [6, 7]: {score}")
    elif move == [5, 7]:
        qh5_score = score
        print(f"Move diagonal [6, 6] -> [5, 7]: {score}")

if qa1_score is not None and qh5_score is not None:
    print(f"\nDifference: {qa1_score - qh5_score}")
    if qa1_score > qh5_score:
        print("[OK] Taking the pawn should be better")
    else:
        print("[BUG] The diagonal move is rated better")

print("\n" + "=" * 80)
print("AI DECISION WITH MINIMAX")
print("=" * 80)

move = game.let_ai_make_move()
print(f"\nAI chose: [6, 6] -> {move[1]}")
print(f"Expected: [6, 6] -> [6, 7]")
