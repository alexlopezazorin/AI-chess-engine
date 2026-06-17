from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from ..Chess import ChessMain
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000"
]

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
    ChessMain.game.set_human_color(human_is_white)
    return {"board": ChessMain.game.board}



class MoveRequest(BaseModel):
    startpos: list
    endpos: list
    promotion_piece: Optional[str] = None

@app.post("/make-move-if-valid")
async def make_move_if_valid(move_request: MoveRequest):
    success = ChessMain.game.make_move_if_valid(move_request.startpos, move_request.endpos, move_request.promotion_piece)
    game_status = ChessMain.game.check_game_status(ChessMain.game.human_is_white) if success else None
    return {"board": ChessMain.game.board, "success": success, "gameStatus": game_status}


class ValidEndSquaresRequest(BaseModel):
    startpos: list

@app.post("/valid-end-squares")
async def valid_end_squares(valid_end_squares_request: ValidEndSquaresRequest):
    result = ChessMain.game.show_valid_end_squares(valid_end_squares_request.startpos)
    return result


class AIMovRequest(BaseModel):
    human_is_white: bool

@app.post("/let-ai-move")
async def let_ai_move(request: AIMovRequest):
    ChessMain.game.set_human_color(request.human_is_white)
    move_made_by_AI = ChessMain.game.let_ai_make_move()

    ai_is_white = not ChessMain.game.human_is_white
    game_status = ChessMain.game.check_game_status(ai_is_white)


    return {
        "startpos": move_made_by_AI[0],
        "endpos": move_made_by_AI[1],
        "board": ChessMain.game.board,
        "gameStatus": game_status
    }