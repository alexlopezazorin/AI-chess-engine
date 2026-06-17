import pytest
import sys
from pathlib import Path

# Add the backend app to the path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from Chess.ChessEngine import GameState, AI

# IMPORTANTE TO KNOW: THESE TESTS WERE DONE WITH depth = 4

def test_ai_wants_to_win_material():
    """Test 1: AI prefers a free queen over a free pawn"""
    game = GameState()
    game.board = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, -1, 0],
        [-100, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, -9, 9, 0],
        [100, 0, 0, 0, 0, 0, 0, 0]
    ]
    game.human_is_white = False  # AI plays white

    print("Initial board:\n",game.board)
    move = game.let_ai_make_move()
    startpos, endpos = move[0], move[1]

    print(f"Move made: {startpos} -> {endpos}")
    assert ((startpos ==[6, 6]) and (endpos == [6, 5]))


def test_ai_avoids_poisoned_material():
    """Test 2: IA to take a free pawn over a poisoned rook"""
    game = GameState()
    game.board = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, -1, 0, 0],
        [0, 0, 0, 0, 0, 0, -5, 0],
        [-100, -1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 9, -1],
        [100, 0, 0, 0, 0, 0, 0, 0]
    ]
    game.human_is_white = False  # AI plays white

    print("Initial board:\n",game.board)
    move = game.let_ai_make_move()
    startpos, endpos = move[0], move[1]

    print(f"Move made: {startpos} -> {endpos}")
    assert ((startpos ==[6, 6]) and (endpos == [6, 7]))


def test_ai_preffers_checkmate_in_one_over_material():
    """Test 3: IA preffers checkmate over material"""
    game = GameState()
    game.board = [
        [0, 0, 0, 0, 0, 0, -100, 0],
        [0, 0, 0, 0, 0, -1, -1, -1],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, -9],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [100, 0, 5, 0, 0, 0, 0, 0]
    ]
    game.human_is_white = False  # AI plays white

    print("Initial board:\n",game.board)
    move = game.let_ai_make_move()
    startpos, endpos = move[0], move[1]

    print(f"Move made: {startpos} -> {endpos}")
    assert ((startpos == [7, 2]) and (endpos == [0, 2]))


def test_ai_preffers_checkmate_in_two_over_material():
    """Test 4: IA preffers checkmate over material >1 range"""
    game = GameState()
    game.board = [
        [0, 0, 0, 0, 0, 0, -100, 0],
        [0, 0, 0, 0, 0, -1, 0, -1],
        [0, 0, 0, 1, 0, 1, -1, 1],
        [0, 0, 0, 0, 0, 0, 1, -5],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 100, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]
    game.human_is_white = False  # AI plays white

    print("Initial board:\n",game.board)
    move = game.let_ai_make_move()
    startpos, endpos = move[0], move[1]

    print(f"Move made: {startpos} -> {endpos}")
    assert ((startpos == [2, 3]) and (endpos == [1, 3]))

def test_AI_stops_checkmate():
    """Test 5: IA stops checkmate"""
    game = GameState()
    game.board = [
        [0, 0, 0, 0, 0, 0, -100, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 2, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 1, -1, 0, 0, 0, 0, 0],
        [1, 0, 1, 0, 0, 0, -5, 0],
        [0, 100, 0, 0, 0, 0, 0, 0]
    ]
    game.human_is_white = False  # AI plays white

    print("Initial board:\n",game.board)
    move = game.let_ai_make_move()
    startpos, endpos = move[0], move[1]

    print(f"Move made: {startpos} -> {endpos}")
    assert ((startpos == [3, 2]) and (endpos == [5, 3]))


def test_ai_wants_to_win_material_black():
    """Test 6 (BLACK): AI prefers a free queen over a free pawn"""
    game = GameState()
    game.board = [
        [-100, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 9, -9, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 100, 0, 0, 0, 0]
    ]
    game.human_is_white = True  # AI plays black

    print("Initial board:\n",game.board)
    move = game.let_ai_make_move()
    startpos, endpos = move[0], move[1]

    print(f"Move made: {startpos} -> {endpos}")
    assert ((startpos == [1, 6]) and (endpos == [1, 5]))


def test_AI_stops_checkmate_black():
    """Test 8: AI stops checkmate as black"""
    game = GameState()
    game.board = [
        [0, 0, 0, 0, 0, 0, -100, 0],
        [0, 0, 0, 0, 0, -1, 0, -1],
        [0, 5, 0, 0, 0, 1, -1, 1],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, -2, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 100, 0, 0, 0, 0, 0, 0]
    ]
    game.human_is_white = True  # AI plays black

    print("Initial board:\n",game.board)
    move = game.let_ai_make_move()
    startpos, endpos = move[0], move[1]

    print(f"Move made: {startpos} -> {endpos}")
    assert ((startpos == [4, 5]) and (endpos == [2, 4]))
