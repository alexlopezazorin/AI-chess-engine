from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from ..Chess import ChessMain
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000",
    os.getenv("FRONTEND_URL", "http://localhost:3000")
]

# Remove duplicates
origins = list(set(origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)




@app.get("/game-state")
async def root(human_is_white: bool, reset_game: bool = False):
    if reset_game:
        ChessMain.game.reset_game()
    ChessMain.game.human_is_white = human_is_white
    return {
        "board_history": ChessMain.game.get_board_as_matrix(),
        "moves_history": ChessMain.game.get_move_history_in_human_notation()
    }


class ValidEndSquaresRequest(BaseModel):
    startpos: list

@app.post("/valid-end-squares")
async def valid_end_squares(valid_end_squares_request: ValidEndSquaresRequest):
    result = ChessMain.game.show_valid_end_squares(valid_end_squares_request.startpos)
    return result



class MoveRequest(BaseModel):
    startpos: list
    endpos: list
    promotion_piece: Optional[str] = None

@app.post("/make-move")
async def make_move(move_request: MoveRequest):
    # Convert [row, col] to square index (0-63)
    start_square = (7 - move_request.startpos[0]) * 8 + move_request.startpos[1]
    end_square = (7 - move_request.endpos[0]) * 8 + move_request.endpos[1]

    ChessMain.game.make_move(start_square, end_square, move_request.promotion_piece)
    game_status = ChessMain.game.check_game_status(last_player_is_white=ChessMain.game.human_is_white)

    # Get last move capture status
    last_move = ChessMain.game.moves_history[-1] if ChessMain.game.moves_history else None
    is_capture = last_move[4] if last_move else False

    return {
        "board_history": ChessMain.game.get_board_as_matrix(),
        "gameStatus": game_status,
        "moves_history": ChessMain.game.get_move_history_in_human_notation(),
        "is_capture": is_capture
    }



@app.get("/let-ai-move")
async def let_ai_move():
    move_made_by_AI = ChessMain.game.let_ai_make_move()
    game_status = ChessMain.game.check_game_status(last_player_is_white=not ChessMain.game.human_is_white)

    # Get last move capture status
    last_move = ChessMain.game.moves_history[-1] if ChessMain.game.moves_history else None
    is_capture = last_move[4] if last_move else False

    # Transform AI score to human-readable format
    human_readable_score = ChessMain.game.transform_ai_evaluation_score_into_a_human_readable_score(move_made_by_AI[2])

    return {
        "startpos": move_made_by_AI[0],
        "endpos": move_made_by_AI[1],
        "score": human_readable_score,
        "board_history": ChessMain.game.get_board_as_matrix(),
        "gameStatus": game_status,
        "moves_history": ChessMain.game.get_move_history_in_human_notation(),
        "is_capture": is_capture
    }