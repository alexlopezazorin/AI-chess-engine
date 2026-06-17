import random

class Piece():
    def __init__(self, value):
        self.value = value

    def is_friendly(self, piece_value):
        if piece_value == 0:
            return False
        return (self.value > 0) == (piece_value > 0)

    def is_enemy(self, piece_value):
        return piece_value != 0 and not self.is_friendly(piece_value)

    def get_valid_moves(self, startpos, board, game_state=None):
        match abs(self.value):
            case 0:
                possible_moves = []
            case 1:
                possible_moves = self.pawn_valid_moves(startpos, board, game_state)
            case 2:
                possible_moves = self.knight_valid_moves(startpos, board)
            case 3:
                possible_moves = self.bishop_valid_moves(startpos, board)
            case 5:
                possible_moves = self.rook_valid_moves(startpos, board)
            case 9:
                possible_moves = self.queen_valid_moves(startpos, board)
            case 100:
                possible_moves = self.king_valid_moves(startpos, board, game_state)

        return possible_moves

    def pawn_valid_moves(self, startpos, board, game_state=None):
        startrow = startpos[0]
        startcol = startpos[1]
        moves = []

        if self.value == 1:
            directions = [(-1, 0)]
            capture_directions = [(-1, 1), (-1, -1)]
            start_row = 6
            en_passant_row = 3

        else:
            directions = [(1, 0)]
            capture_directions = [(1, 1), (1, -1)]
            start_row = 1
            en_passant_row = 4

        # Move forward
        new_row = startrow + directions[0][0]
        if 0 <= new_row < 8 and board[new_row][startcol] == 0:
            moves.append([new_row, startcol])

        # Move two squares from starting position
        new_row_two = startrow + 2 * directions[0][0]
        if (startrow == start_row and 0 <= new_row_two < 8 and
            board[new_row_two][startcol] == 0 and board[startrow + directions[0][0]][startcol] == 0):
            moves.append([new_row_two, startcol])

        #capture moves
        for dx, dy in capture_directions:
            new_x, new_y = startrow + dx, startcol + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                if self.is_enemy(board[new_x][new_y]):
                    moves.append([new_x, new_y])

        # En passant
        if game_state and startrow == en_passant_row and len(game_state.move_history) > 0:
            last_move = game_state.move_history[-1]
            if abs(last_move.piecemoved) == 1 and abs(last_move.startrow - last_move.endrow) == 2:
                enemy_pawn_col = last_move.endcol
                if abs(enemy_pawn_col - startcol) == 1 and last_move.endrow == startrow:
                    en_passant_capture_row = startrow + (-1 if self.value == 1 else 1)
                    moves.append([en_passant_capture_row, enemy_pawn_col])

        return moves

    def knight_valid_moves(self, startpos, board):
        startrow = startpos[0]
        startcol = startpos[1]
        moves = []

        knight_offsets = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]

        for dx, dy in knight_offsets:
            new_x, new_y = startrow + dx, startcol + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                if not self.is_friendly(board[new_x][new_y]):
                    moves.append([new_x, new_y])

        return moves

    def bishop_valid_moves(self, startpos, board):
        startrow = startpos[0]
        startcol = startpos[1]
        moves = []

        bishop_offsets = [
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]

        for dx, dy in bishop_offsets:
            for i in range(1, 8):
                new_x, new_y = startrow + dx * i, startcol + dy * i
                if 0 <= new_x < 8 and 0 <= new_y < 8:
                    if self.is_friendly(board[new_x][new_y]):
                        break
                    moves.append([new_x, new_y])
                    if self.is_enemy(board[new_x][new_y]):
                        break

        return moves

    def rook_valid_moves(self, startpos, board):
        startrow = startpos[0]
        startcol = startpos[1]
        moves = []

        rook_offsets = [
            (1, 0), (-1, 0), (0, 1), (0, -1)
        ]

        for dx, dy in rook_offsets:
            for i in range(1, 8):
                new_x, new_y = startrow + dx * i, startcol + dy * i
                if 0 <= new_x < 8 and 0 <= new_y < 8:
                    if self.is_friendly(board[new_x][new_y]):
                        break
                    moves.append([new_x, new_y])
                    if self.is_enemy(board[new_x][new_y]):
                        break

        return moves

    def queen_valid_moves(self, startpos, board):
        moves = []

        # Combine rook and bishop moves
        moves.extend(self.rook_valid_moves(startpos, board))
        moves.extend(self.bishop_valid_moves(startpos, board))

        return moves

    def king_valid_moves(self, startpos, board, game_state=None):
        startrow = startpos[0]
        startcol = startpos[1]
        moves = []

        king_offsets = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]

        for dx, dy in king_offsets:
            new_x, new_y = startrow + dx, startcol + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                if not self.is_friendly(board[new_x][new_y]):
                    moves.append([new_x, new_y])

        if game_state:
            if self.value == 100:
                if startpos == [7, 4] and not game_state.white_king_moved:
                    # Kingside castling
                    if (board[7][5] == 0 and board[7][6] == 0 and board[7][7] == 5 and
                        not game_state.white_rook_kingside_moved and
                        not game_state.is_square_under_attack([7, 5], True)):
                        moves.append([7, 6])
                    # Queenside castling
                    if (board[7][3] == 0 and board[7][2] == 0 and board[7][1] == 0 and board[7][0] == 5 and
                        not game_state.white_rook_queenside_moved and
                        not game_state.is_square_under_attack([7, 3], True)):
                        moves.append([7, 2])
            elif self.value == -100:
                if startpos == [0, 4] and not game_state.black_king_moved:
                    # Kingside castling
                    if (board[0][5] == 0 and board[0][6] == 0 and board[0][7] == -5 and
                        not game_state.black_rook_kingside_moved and
                        not game_state.is_square_under_attack([0, 5], False)):
                        moves.append([0, 6])
                    # Queenside castling
                    if (board[0][3] == 0 and board[0][2] == 0 and board[0][1] == 0 and board[0][0] == -5 and
                        not game_state.black_rook_queenside_moved and
                        not game_state.is_square_under_attack([0, 3], False)):
                        moves.append([0, 2])

        return moves


class Move():
    def __init__(self, startpos, endpos, board, game_state=None):
        self.board = board
        self.startpos = startpos
        self.endpos = endpos
        self.startrow = startpos[0]
        self.startcol = startpos[1]
        self.endrow = endpos[0]
        self.endcol = endpos[1]
        self.piecemoved = board[startpos[0]][startpos[1]]
        self.piececaptured = board[endpos[0]][endpos[1]]
        self.game_state = game_state

    def is_valid(self):
        piece = Piece(self.piecemoved)
        possible_moves = piece.get_valid_moves(self.startpos, self.board, self.game_state)

        if self.endpos in possible_moves:
            if piece.is_friendly(self.piececaptured):
                return False
            return True
        return False

    def make_move(self, promotion_piece=None):
        self.board[self.endrow][self.endcol] = self.board[self.startrow][self.startcol]
        self.board[self.startrow][self.startcol] = 0

        # En passant capture: pawn moves diagonally but no piece is captured in normal way
        if abs(self.piecemoved) == 1 and self.piececaptured == 0 and self.startcol != self.endcol:
            captured_row = self.startrow
            self.board[captured_row][self.endcol] = 0

        # Promotion: convert pawn to chosen piece
        if promotion_piece:
            promotion_map = {
                "queen": 9,
                "rook": 5,
                "bishop": 3,
                "knight": 2
            }
            piece_value = promotion_map.get(promotion_piece, 9)
            is_white = self.piecemoved > 0
            self.board[self.endrow][self.endcol] = piece_value if is_white else -piece_value

        #castling
        if self.piecemoved == 100:
            if self.startpos==[7,4] and self.endpos==[7,6]:
                self.board[7][5] = self.board[7][7]
                self.board[7][7] = 0

            elif self.startpos==[7,4] and self.endpos==[7,2]:
                self.board[7][3] = self.board[7][0]
                self.board[7][0] = 0

        elif self.piecemoved == -100:
            if self.startpos==[0,4] and self.endpos==[0,6]:
                self.board[0][5] = self.board[0][7]
                self.board[0][7] = 0

            elif self.startpos==[0,4] and self.endpos==[0,2]:
                self.board[0][3] = self.board[0][0]
                self.board[0][0] = 0


class GameState():
    def __init__(self):
        self.board =[
            [-5, -2, -3, -9, -100, -3, -2, -5],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [5, 2, 3, 9, 100, 3, 2, 5]]
        self.move_history = []
        self.human_is_white = True
        self.moves_since_capture_or_pawn_move = 0
        self.position_history = []
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_queenside_moved = False
        self.white_rook_kingside_moved = False
        self.black_rook_queenside_moved = False
        self.black_rook_kingside_moved = False
        self.white_king_castled = False
        self.black_king_castled = False

    def reset_game(self):
        self.board = [
            [-5, -2, -3, -9, -100, -3, -2, -5],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [5, 2, 3, 9, 100, 3, 2, 5]]
        self.move_history = []
        self.moves_since_capture_or_pawn_move = 0
        self.position_history = []
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_queenside_moved = False
        self.white_rook_kingside_moved = False
        self.black_rook_queenside_moved = False
        self.black_rook_kingside_moved = False

    def get_board_hash(self):
        return tuple(tuple(row) for row in self.board)

    def is_valid_move(self, startpos, endpos):
        move = Move(startpos, endpos, self.board, self)
        if not move.is_valid():
            return False

        piece_color = self.board[startpos[0]][startpos[1]]
        is_white = piece_color > 0

        original_piece = self.board[endpos[0]][endpos[1]]
        self.board[endpos[0]][endpos[1]] = self.board[startpos[0]][startpos[1]]
        self.board[startpos[0]][startpos[1]] = 0

        # En passant: simular captura del peón enemigo
        captured_pawn_row = None
        if abs(self.board[endpos[0]][endpos[1]]) == 1 and original_piece == 0 and startpos[1] != endpos[1]:
            captured_pawn_row = startpos[0]
            self.board[captured_pawn_row][endpos[1]] = 0

        in_check = self.is_in_check(is_white)

        # Restaurar tablero
        if captured_pawn_row is not None:
            self.board[captured_pawn_row][endpos[1]] = -1 if is_white else 1
        self.board[startpos[0]][startpos[1]] = self.board[endpos[0]][endpos[1]]
        self.board[endpos[0]][endpos[1]] = original_piece

        return not in_check

    def make_move(self, startpos, endpos, promotion_piece=None):
        move = Move(startpos, endpos, self.board, self)
        move.make_move(promotion_piece)
        self.move_history.append(move)

        # Track king movement for castling rights
        if abs(move.piecemoved) == 100:
            if move.piecemoved == 100:
                self.white_king_moved = True
            else:
                self.black_king_moved = True

        # Track rook movement for castling rights
        if abs(move.piecemoved) == 5:
            if move.piecemoved == 5:  # White rook
                if move.startpos == [7, 0]:
                    self.white_rook_queenside_moved = True
                elif move.startpos == [7, 7]:
                    self.white_rook_kingside_moved = True
            else:  # Black rook
                if move.startpos == [0, 0]:
                    self.black_rook_queenside_moved = True
                elif move.startpos == [0, 7]:
                    self.black_rook_kingside_moved = True
        
        #track castling
        if abs(move.piecemoved) == 100:
            if (move.piecemoved == 100 and startpos==[7,4] and (endpos==[7,6] or endpos==[7,2])):
                self.white_king_castled = True
            elif (move.piecemoved == -100 and startpos==[0,4] and (endpos==[0,6] or endpos==[0,2])):
                self.black_king_castled = True

        # 50-move rule: reset counter on capture or pawn move, else increment
        if move.piececaptured != 0 or abs(move.piecemoved) == 1:
            self.moves_since_capture_or_pawn_move = 0
        else:
            self.moves_since_capture_or_pawn_move += 1

        # Save board position for repetition detection
        self.position_history.append(self.get_board_hash())

    def make_move_if_valid(self, startpos, endpos, promotion_piece=None):
        if self.is_valid_move(startpos, endpos):
            self.make_move(startpos, endpos, promotion_piece)
            return True
        return False

    def undo_move(self):
        if not self.move_history:
            return

        move = self.move_history.pop()

        # Restore board state
        self.board[move.startrow][move.startcol] = move.piecemoved
        self.board[move.endrow][move.endcol] = move.piececaptured

        # Restore en passant capture
        if abs(move.piecemoved) == 1 and move.piececaptured == 0 and move.startcol != move.endcol:
            captured_pawn_row = move.startrow
            self.board[captured_pawn_row][move.endcol] = -1 if move.piecemoved == 1 else 1

        # Restore castling (undo rook movement)
        if move.piecemoved == 100:
            if move.startpos == [7, 4] and move.endpos == [7, 6]:  # White kingside castling
                self.board[7][7] = self.board[7][5]
                self.board[7][5] = 0
            elif move.startpos == [7, 4] and move.endpos == [7, 2]:  # White queenside castling
                self.board[7][0] = self.board[7][3]
                self.board[7][3] = 0
        elif move.piecemoved == -100:
            if move.startpos == [0, 4] and move.endpos == [0, 6]:  # Black kingside castling
                self.board[0][7] = self.board[0][5]
                self.board[0][5] = 0
            elif move.startpos == [0, 4] and move.endpos == [0, 2]:  # Black queenside castling
                self.board[0][0] = self.board[0][3]
                self.board[0][3] = 0

        # Restore position history
        if self.position_history:
            self.position_history.pop()

        # Restore 50-move counter
        if move.piececaptured != 0 or abs(move.piecemoved) == 1:
            self.moves_since_capture_or_pawn_move = 0
        else:
            self.moves_since_capture_or_pawn_move -= 1

        # Restore king movement flags
        if abs(move.piecemoved) == 100:
            if move.piecemoved == 100:
                self.white_king_moved = False
            else:
                self.black_king_moved = False

        # Restore rook movement flags
        if abs(move.piecemoved) == 5:
            if move.piecemoved == 5:  # White rook
                if move.startpos == [7, 0]:
                    self.white_rook_queenside_moved = False
                elif move.startpos == [7, 7]:
                    self.white_rook_kingside_moved = False
            else:  # Black rook
                if move.startpos == [0, 0]:
                    self.black_rook_queenside_moved = False
                elif move.startpos == [0, 7]:
                    self.black_rook_kingside_moved = False

    def show_valid_end_squares(self, startpos):
        piece = Piece(self.board[startpos[0]][startpos[1]])
        possible_moves = piece.get_valid_moves(startpos, self.board, self)

        valid_end_squares = []
        has_promotion = False

        for endpos in possible_moves:
            move = Move(startpos, endpos, self.board, self)
            if not move.is_valid():
                continue

            is_white = (self.board[startpos[0]][startpos[1]] > 0 )

            original_piece = self.board[endpos[0]][endpos[1]]
            self.board[endpos[0]][endpos[1]] = self.board[startpos[0]][startpos[1]]
            self.board[startpos[0]][startpos[1]] = 0

            # En passant: simular captura del peón enemigo
            captured_pawn_row = None
            if abs(self.board[endpos[0]][endpos[1]]) == 1 and original_piece == 0 and startpos[1] != endpos[1]:
                captured_pawn_row = startpos[0]
                self.board[captured_pawn_row][endpos[1]] = 0

            in_check = self.is_in_check(is_white)

            # Restaurar tablero
            if captured_pawn_row is not None:
                self.board[captured_pawn_row][endpos[1]] = -1 if is_white else 1
            self.board[startpos[0]][startpos[1]] = self.board[endpos[0]][endpos[1]]
            self.board[endpos[0]][endpos[1]] = original_piece

            if not in_check:
                valid_end_squares.append(endpos)

                # Detectar si es casilla de promoción (peón en fila 0 o 7)
                if abs(self.board[startpos[0]][startpos[1]]) == 1:
                    if (is_white and endpos[0] == 0) or (not is_white and endpos[0] == 7):
                        has_promotion = True

        return {"validEndSquares": valid_end_squares, "promotion": has_promotion}

    def let_ai_make_move(self):
        ai = AI(self)
        move_made_by_AI = ai.ai_makes_move()
        return move_made_by_AI

    def set_human_color(self, human_is_white):
        self.human_is_white = human_is_white

    def has_legal_moves(self, is_white):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if (piece > 0 and is_white) or (piece < 0 and not is_white):
                    result = self.show_valid_end_squares([row, col])
                    if result["validEndSquares"]:
                        return True
        return False

    def is_threefold_repetition(self):
        current_position = self.get_board_hash()
        count = 0
        for position in self.position_history:
            if position == current_position:
                count += 1
        return count >= 3

    def is_insufficient_material(self):
        white_minors = 0
        black_minors = 0
        white_major = 0
        black_major = 0

        for row in self.board:
            for piece in row:
                match piece:
                    case 2:
                        white_minors += 1
                    case -2:
                        black_minors += 1
                    case 3:
                        white_minors += 1
                    case -3:
                        black_minors += 1
                    case 5 | 9:
                        white_major += 1
                    case -5 | -9:
                        black_major += 1

        match (white_minors, black_minors, white_major, black_major):
            case (0, 0, 0, 0):  # King vs King
                return True
            case (1, 0, 0, 0):  # King + 1 minor vs King
                return True
            case (0, 1, 0, 0):  # King vs King + 1 minor
                return True
            case _:
                return False

    def check_game_status(self, is_white):
        # 50-move rule: if 50 moves by each player (100 total) without capture or pawn move, it's a draw
        if self.moves_since_capture_or_pawn_move >= 100:
            return {
                'gameIsFinished': True,
                'winner': 'draw'
            }

        # Threefold repetition
        if self.is_threefold_repetition():
            return {
                'gameIsFinished': True,
                'winner': 'draw'
            }

        # Insufficient material
        if self.is_insufficient_material():
            return {
                'gameIsFinished': True,
                'winner': 'draw'
            }

        opponent_is_white = not is_white

        if not self.has_legal_moves(opponent_is_white):
            if self.is_in_check(opponent_is_white):
                return {
                    'gameIsFinished': True,
                    'winner': 'white' if is_white else 'black'
                }
            else:
                return {
                    'gameIsFinished': True,
                    'winner': 'draw'
                }

        return {
            'gameIsFinished': False,
            'winner': None
        }

    def is_square_under_attack(self, position, is_white):
        for row in range(8):
            for col in range(8):
                if ((is_white and self.board[row][col] < 0) or (not is_white and self.board[row][col] > 0)):
                    piece = Piece(self.board[row][col])
                    possible_moves = piece.get_valid_moves([row, col], self.board, None)
                    if position in possible_moves:
                        return True
        return False
    
    def get_king_position(self, is_white):
        for row in range(8):
            for col in range(8):
                if ((is_white and self.board[row][col] == 100) or (not is_white and self.board[row][col] == -100)):
                    return [row, col]

    def is_in_check(self, is_white):
        king_position = self.get_king_position(is_white)
        return self.is_square_under_attack(king_position, is_white)


class AI():
    SEARCH_DEPTH = 5  # Configurable depth for minimax search

    # Piece values (in centipawns: 1 pawn = 100)
    PIECE_VALUES = {
        1: 100,    # Pawn
        2: 300,    # Knight
        3: 300,    # Bishop
        5: 500,    # Rook
        9: 900,    # Queen
        100: 0     # King (value is irrelevant, but needed for lookup)
    }

    # Piece-Square Tables for positional evaluation
    PAWN_TABLE = [
        [  0,   0,   0,   0,   0,   0,   0,   0],
        [ 50,  50,  50,  50,  50,  50,  50,  50],
        [ 10,  10,  20,  30,  30,  20,  10,  10],
        [  5,   5,  10,  25,  25,  10,   5,   5],
        [  0,   0,   0,  20,  20,   0,   0,   0],
        [  5,  -5, -10,   0,   0, -10,  -5,   5],
        [  5,  10,  10, -20, -20,  10,  10,   5],
        [  0,   0,   0,   0,   0,   0,   0,   0]
    ]

    KNIGHT_TABLE = [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50]
    ]

    BISHOP_TABLE = [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-20,-10,-10,-10,-10,-10,-10,-20]
    ]

    ROOK_TABLE = [
        [  0,   0,   5,  10,  10,   5,   0,   0],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [  5,  10,  10,  10,  10,  10,  10,   5],
        [  0,   0,   20,   20,   20,   20,   0,   0]
    ]

    QUEEN_TABLE = [
        [-20,-10,-10, -5, -5,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5,  5,  5,  5,  0,-10],
        [ -5,  0,  5,  5,  5,  5,  0, -5],
        [  0,  0,  5,  5,  5,  5,  0, -5],
        [-10,  5,  5,  5,  5,  5,  0,-10],
        [-10,  0,  5,  0,  0,  0,  0,-10],
        [-20,-10,-10, -5, -5,-10,-10,-20]
    ]

    DOUBLED_PAWN_PENALTY = 20

    def __init__(self, game_state):
        self.game_state = game_state
        self.transposition_table = {}  # Hash table for memoization: board_hash -> {score, depth}

    def ai_makes_move(self):
        # Clear transposition table for each new search to avoid memory bloat
        self.transposition_table.clear()

        possible_moves = self.get_valid_moves()
        move = self.select_best_move_algorithm(possible_moves)

        if move is None:
            # Fallback: if no move was selected, return the first available move
            if possible_moves:
                move = possible_moves[0]
            else:
                # No legal moves available (should not happen in normal game flow)
                return None

        # Extract promotion piece if present
        startpos = move[0]
        endpos = move[1]
        promotion_piece = move[2] if len(move) > 2 else None

        self.game_state.make_move(startpos, endpos, promotion_piece)
        return move

    def get_valid_moves(self):
        ai_is_white = not self.game_state.human_is_white
        return self.get_valid_moves_for_color(ai_is_white)

    def get_valid_moves_for_color(self, is_white):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.game_state.board[row][col]
                is_piece_of_color = (piece > 0) if is_white else (piece < 0)
                if is_piece_of_color:
                    result = self.game_state.show_valid_end_squares([row, col])
                    valid_moves = result["validEndSquares"]
                    is_promotion = result["promotion"]

                    if is_promotion:
                        # For promotion moves, create 4 variants (one for each piece)
                        promotion_pieces = ["queen", "rook", "bishop", "knight"]
                        for endpos in valid_moves:
                            for piece_type in promotion_pieces:
                                moves.append([[row, col], endpos, piece_type])
                    else:
                        for endpos in valid_moves:
                            moves.append([[row, col], endpos])

        # Sort moves by order of importance (move ordering for alpha-beta pruning)
        moves.sort(key=lambda move: self.move_score(move, is_white), reverse=True)
        return moves

    def move_score(self, move, is_white):
        """
        Assign a heuristic score to a move for move ordering.
        Higher score = explored first. Used to maximize alpha-beta pruning efficiency.

        MOVE ORDERING (by priority):
        1. Pawn Promotion (score: 800) - Peón llega a última fila
        2. Capture Queen (score: 900) - Captura la reina rival
        3. Capture Rook (score: 500) - Captura la torre
        4. Capture Bishop/Knight (score: 300) - Captura alfil o caballo
        5. Capture Pawn (score: 100) - Captura peón
        6. Giving Check (score: 50) - Movimiento que da jaque
        7. Quiet moves (score: 0) - Movimientos normales

        NOTA: Los scores se acumulan. Ejemplo: Promocionar capturando una torre
        tendría score = 800 + 500 = 1300, mejor que solo capturar reina (900).
        """
        startpos, endpos = move[0], move[1]
        piece_moved = self.game_state.board[startpos[0]][startpos[1]]
        captured_piece = self.game_state.board[endpos[0]][endpos[1]]

        score = 0

        # Priority 1: Promotion (pawn reaches last rank)
        is_promotion = abs(piece_moved) == 1 and ((is_white and endpos[0] == 0) or (not is_white and endpos[0] == 7))
        if is_promotion:
            score += 800

        # Priority 2-5: Captures scored by Most Valuable Victim (MVV) principle
        if captured_piece != 0:
            captured_value = abs(captured_piece)
            if captured_value == 9:  # Queen
                score += 900
            elif captured_value == 5:  # Rook
                score += 500
            elif captured_value == 3 or captured_value == 2:  # Bishop or Knight
                score += 300
            elif captured_value == 1:  # Pawn
                score += 100
        else:
            # Priority 6: Moves that give check (expensive to calculate, only if no capture)
            original_piece = self.game_state.board[startpos[0]][startpos[1]]
            self.game_state.board[endpos[0]][endpos[1]] = original_piece
            self.game_state.board[startpos[0]][startpos[1]] = 0

            opponent_is_white = not is_white
            in_check = self.game_state.is_in_check(opponent_is_white)

            self.game_state.board[startpos[0]][startpos[1]] = original_piece
            self.game_state.board[endpos[0]][endpos[1]] = 0

            if in_check:
                score += 50

        return score
    
    def select_best_move_algorithm(self, possible_moves):

        best_move = None
        # Iterative deepening
        for depth in range(1, self.SEARCH_DEPTH + 1):
            best_score = float('-inf')
            current_best_move = None

            if best_move: #best move of last depth search goes to first position,  so its the first move evaluated in the new depth
                idx = possible_moves.index(best_move)
                if idx != 0:
                    possible_moves[0], possible_moves[idx] = possible_moves[idx], possible_moves[0]


            for move in possible_moves:
                startpos = move[0]
                endpos = move[1]
                promotion_piece = move[2] if len(move) > 2 else None

                self.game_state.make_move(startpos, endpos, promotion_piece)
                score = self.minimax(depth - 1, is_ai_turn=False)
                self.game_state.undo_move()

                if score > best_score:
                    best_score = score
                    current_best_move = move

            if current_best_move is not None:
                best_move = current_best_move

        return best_move




    def minimax(self, depth, is_ai_turn, alpha=float('-inf'), beta=float('inf')):
        # Transposition table lookup
        board_hash = self.game_state.get_board_hash()
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:
                return entry['score']

        if depth == 0:
            last_mover_is_white = not is_ai_turn
            score = self.quiescence(alpha, beta, is_ai_turn)
            # Store in transposition table
            self.transposition_table[board_hash] = {'score': score, 'depth': depth}
            return score

        ai_is_white = not self.game_state.human_is_white

        if is_ai_turn:  # AI's turn - maximize score
            best_score = float('-inf')
            moves = self.get_valid_moves_for_color(ai_is_white)

            if not moves:  # No legal moves
                last_mover_is_white = not ai_is_white
                score = self.evaluation_function(last_mover_is_white)
                self.transposition_table[board_hash] = {'score': score, 'depth': depth}
                return score

            for move in moves:
                startpos = move[0]
                endpos = move[1]
                promotion_piece = move[2] if len(move) > 2 else None

                self.game_state.make_move(startpos, endpos, promotion_piece)
                score = self.minimax(depth - 1, is_ai_turn=False, alpha=alpha, beta=beta)
                best_score = max(best_score, score)
                self.game_state.undo_move()

                alpha = max(alpha, best_score)
                if alpha >= beta:
                    break  # Beta cutoff

            # Store in transposition table
            self.transposition_table[board_hash] = {'score': best_score, 'depth': depth}
            return best_score

        else:  # Opponent's turn - minimize score
            best_score = float('inf')
            moves = self.get_valid_moves_for_color(not ai_is_white)

            if not moves:  # No legal moves
                last_mover_is_white = ai_is_white
                score = self.evaluation_function(last_mover_is_white)
                self.transposition_table[board_hash] = {'score': score, 'depth': depth}
                return score

            for move in moves:
                startpos = move[0]
                endpos = move[1]
                promotion_piece = move[2] if len(move) > 2 else None

                self.game_state.make_move(startpos, endpos, promotion_piece)
                score = self.minimax(depth - 1, is_ai_turn=True, alpha=alpha, beta=beta)
                best_score = min(best_score, score)
                self.game_state.undo_move()

                beta = min(beta, best_score)
                if alpha >= beta:
                    break  # Alpha cutoff

            # Store in transposition table
            self.transposition_table[board_hash] = {'score': best_score, 'depth': depth}
            return best_score
    
    def quiescence(self, alpha, beta, is_ai_turn):
        """
        After having reached depth=0, we calculate direct combinations that
        include captures, promotion and checks.
        By doing that, we increment the calculations over risky positions until
        no more captures, promotion or checks are possible
        """
        last_mover_is_white = not is_ai_turn
        stand_pat = self.evaluation_function(last_mover_is_white)

        #delta prunning: in order to avoid exploring moves where evaluation wont get better
        DELTA_MARGIN = 1000
        if stand_pat + DELTA_MARGIN < alpha:
            return alpha

        # Alpha-beta pruning básico
        if is_ai_turn:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)

        # Generar SOLO movimientos de captura
        moves = self.get_capture_and_promotion_moves(is_ai_turn)

        for move in moves:
            startpos = move[0]
            endpos = move[1]
            promotion_piece = move[2] if len(move) > 2 else None

            self.game_state.make_move(startpos, endpos, promotion_piece)

            score = self.quiescence(alpha, beta, not is_ai_turn)

            self.game_state.undo_move()

            if is_ai_turn:
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
            else:
                beta = min(beta, score)
                if alpha >= beta:
                    break

        return alpha if is_ai_turn else beta
    
    def get_capture_and_promotion_moves(self, is_white):
        moves = []

        for row in range(8):
            for col in range(8):
                piece = self.game_state.board[row][col]
                if piece == 0:
                    continue

                if (piece > 0) != is_white:
                    continue

                result = self.game_state.show_valid_end_squares([row, col])
                valid_moves = result["validEndSquares"]
                is_promotion = result["promotion"]

                for endpos in valid_moves:
                    captured_piece = self.game_state.board[endpos[0]][endpos[1]]

                    #PROMOCIONES
                    if is_promotion:
                            for promo in ["queen", "rook", "bishop", "knight"]:
                                moves.append([[row, col], endpos, promo])

                    # CAPTURAS
                    if captured_piece != 0:
                            moves.append([[row, col], endpos])

        return moves


    

    def evaluation_function(self, last_mover_is_white):
        ai_is_white = not self.game_state.human_is_white

        game_status = self.game_state.check_game_status(last_mover_is_white)
        if game_status['gameIsFinished']:
            winner = game_status['winner']
            if winner == ('white' if ai_is_white else 'black'):
                return 99999  # IA wins by checkmate (use large number instead of inf for int eval)
            elif winner == ('black' if ai_is_white else 'white'):
                return -99999  # IA loses by checkmate
            else:
                return 0  # Draw

        score = 0

        # Material + Position evaluation with Piece-Square Tables
        for row in range(8):
            for col in range(8):
                piece = self.game_state.board[row][col]
                if piece == 0:
                    continue

                piece_type = abs(piece)
                is_white = piece > 0

                # Material value
                material_value = self.PIECE_VALUES.get(piece_type, 0)
                score_contribution = material_value if is_white else -material_value

                # Positional value from Piece-Square Table
                positional_value = self._get_positional_value(piece_type, row, col, is_white)
                score_contribution += positional_value if is_white else -positional_value

                score += score_contribution

        # Bonification: Castling
        if self.game_state.white_king_castled:
            score += 50  # Castling for white
        if self.game_state.black_king_castled:
            score -= 50  # Castling for white

        # Penalty: Doubled Pawns
        score -= self._count_doubled_pawns(ai_is_white) * self.DOUBLED_PAWN_PENALTY
        score += self._count_doubled_pawns(ai_is_white) * self.DOUBLED_PAWN_PENALTY

        # Invert score if human plays white (AI perspective)
        if self.game_state.human_is_white:
            score = -score

        return score

    def _get_positional_value(self, piece_type, row, col, is_white):
        """Get Piece-Square Table value for a piece at position."""
        # Flip row for black pieces (they are played from the opposite side)
        table_row = row if is_white else 7 - row

        if piece_type == 1:  # Pawn
            return self.PAWN_TABLE[table_row][col]
        elif piece_type == 2:  # Knight
            return self.KNIGHT_TABLE[table_row][col]
        elif piece_type == 3:  # Bishop
            return self.BISHOP_TABLE[table_row][col]
        elif piece_type == 5:  # Rook
            return self.ROOK_TABLE[table_row][col]
        elif piece_type == 9:  # Queen
            return self.QUEEN_TABLE[table_row][col]
        else:
            return 0

    def _count_doubled_pawns(self, ai_is_white):
        """Count doubled pawns for white (penalty)."""
        count = 0
        pawn = 1 if ai_is_white else -1

        for col in range(8):
            pawns_in_col = 0
            for row in range(8):
                if self.game_state.board[row][col] == pawn:  # White pawn
                    pawns_in_col += 1
            if pawns_in_col > 1:
                count += pawns_in_col - 1
        return count

