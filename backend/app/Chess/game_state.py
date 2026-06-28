import random

class GameState:
    # Knight position table (prefers central squares)
    KNIGHT_TABLE = [
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10,   0,   5,   5,   5,   5,   0, -10,
        -10,   5,  10,  10,  10,  10,   5, -10,
        -10,   5,  10,  15,  15,  10,   5, -10,
        -10,   5,  10,  15,  15,  10,   5, -10,
        -10,   5,  10,  10,  10,  10,   5, -10,
        -10,   0,   5,   5,   5,   5,   0, -10,
        -20, -10, -10, -10, -10, -10, -10, -20,
    ]

    # Bishop position table (prefers long diagonals)
    BISHOP_TABLE = [
        -10, -10, -10, -10, -10, -10, -10, -10,
        -10,   5,   5,   5,   5,   5,   5, -10,
        -10,   5,  10,  10,  10,  10,   5, -10,
        -10,   5,  10,  15,  15,  10,   5, -10,
        -10,   5,  10,  15,  15,  10,   5, -10,
        -10,   5,  10,  10,  10,  10,   5, -10,
        -10,   5,   5,   5,   5,   5,   5, -10,
        -10, -10, -10, -10, -10, -10, -10, -10,
    ]

    # Pawn position table (encourages advance and center control)
    PAWN_TABLE = [
        0,   0,   0,   0,   0,   0,   0,   0,
        5,   5,   5,  10,  10,   5,   5,   5,
        10,  10,  10,  20,  20,  10,  10,  10,
        20,  20,  20,  30,  30,  20,  20,  20,
        30,  30,  30,  40,  40,  30,  30,  30,
        40,  40,  40,  50,  50,  40,  40,  40,
        50,  50,  50,  60,  60,  50,  50,  50,
        0,   0,   0,   0,   0,   0,   0,   0,
    ]

    def __init__(self):
        self.depth = 3
        self.current_search_depth = self.depth
        self.reset_game()
        self.transposition_table = {}
        self.killer_moves = [set() for _ in range(self.depth + 1)]

    def reset_game(self):
        # white pieces
        self.white_rooks    = 0b0000000000000000000000000000000000000000000000000000000010000001
        self.white_knights  = 0b0000000000000000000000000000000000000000000000000000000001000010
        self.white_bishops  = 0b0000000000000000000000000000000000000000000000000000000000100100
        self.white_queen    = 0b0000000000000000000000000000000000000000000000000000000000001000
        self.white_king     = 0b0000000000000000000000000000000000000000000000000000000000010000
        self.white_pawns    = 0b0000000000000000000000000000000000000000000000001111111100000000
        # black pieces
        self.black_rooks    = 0b1000000100000000000000000000000000000000000000000000000000000000
        self.black_knights  = 0b0100001000000000000000000000000000000000000000000000000000000000
        self.black_bishops  = 0b0010010000000000000000000000000000000000000000000000000000000000
        self.black_queen    = 0b0000100000000000000000000000000000000000000000000000000000000000
        self.black_king     = 0b0001000000000000000000000000000000000000000000000000000000000000
        self.black_pawns    = 0b0000000011111111000000000000000000000000000000000000000000000000

        self.human_is_white = True
        self.last_move = None
        self.moves_history = []
        self.board_history = []

        # Castling rights tracking
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_a_moved = False  # queenside rook
        self.white_rook_h_moved = False  # kingside rook
        self.black_rook_a_moved = False  # queenside rook
        self.black_rook_h_moved = False  # kingside rook

        # Castling history (to distinguish from king moving to g1/c1 later)
        self.white_kingside_castled = False
        self.white_queenside_castled = False
        self.black_kingside_castled = False
        self.black_queenside_castled = False

        # 50-move rule counter (reset on pawn move or capture)
        self.halfmove_clock = 0

        # Position history for threefold repetition
        self.position_history = {}

        # Accumulated position bonuses (updated in make_move for O(1) evaluate_board)
        self.white_position_bonus = 0
        self.black_position_bonus = 0

    def _sort_moves_by_priority(self, moves, is_white, depth=0):
        """Sort moves: captures (MVV/LVA), killer moves, then quiet moves"""
        captures = []
        killer_moves = []
        quiet_moves = []

        for start_square, end_square, promotion in moves:
            piece_at_dest = self._get_piece(end_square)
            move_tuple = (start_square, end_square, promotion)

            if piece_at_dest and ((piece_at_dest < 0) == is_white):
                # Capture: MVV/LVA = victim_value - attacker_value
                attacker = self._get_piece(start_square)
                victim_value = abs(piece_at_dest)
                attacker_value = abs(attacker) if attacker else 0
                mvv_lva = victim_value - attacker_value
                captures.append((start_square, end_square, promotion, mvv_lva))
            elif move_tuple in self.killer_moves[depth]:
                # Killer move
                killer_moves.append(move_tuple)
            else:
                # Quiet move
                quiet_moves.append(move_tuple)

        # Sort captures by MVV/LVA descending
        captures.sort(key=lambda x: x[3], reverse=True)
        sorted_moves = [(s, e, p) for s, e, p, _ in captures] + killer_moves + quiet_moves
        return sorted_moves

    def get_all_possible_moves(self, is_white):
        """Get all possible moves for the specified side - includes pawn promotions"""
        all_possible_moves = []

        if is_white:
            pieces = [
                (self.white_pawns, 1),
                (self.white_knights, 2),
                (self.white_bishops, 3),
                (self.white_rooks, 5),
                (self.white_queen, 9),
                (self.white_king, 100)
            ]
        else:
            pieces = [
                (self.black_pawns, -1),
                (self.black_knights, -2),
                (self.black_bishops, -3),
                (self.black_rooks, -5),
                (self.black_queen, -9),
                (self.black_king, -100)
            ]

        for bitboard, piece_type in pieces:
            temp_board = bitboard
            while temp_board:
                square = (temp_board & -temp_board).bit_length() - 1

                if abs(piece_type) == 1:
                    valid_moves = self._get_pawn_moves(square, is_white)
                elif abs(piece_type) == 2:
                    valid_moves = self._get_knight_moves(square, is_white)
                elif abs(piece_type) == 3:
                    valid_moves = self._get_bishop_moves(square, is_white)
                elif abs(piece_type) == 5:
                    valid_moves = self._get_rook_moves(square, is_white)
                elif abs(piece_type) == 9:
                    valid_moves = self._get_queen_moves(square, is_white)
                elif abs(piece_type) == 100:
                    valid_moves = self._get_king_moves(square, is_white)

                for end_square in valid_moves:
                    # Check if pawn reaches promotion rank
                    if abs(piece_type) == 1 and ((is_white and end_square >= 56) or (not is_white and end_square <= 7)):
                        # Generate 4 promotion moves
                        for promotion in ['queen', 'rook', 'bishop', 'knight']:
                            all_possible_moves.append((square, end_square, promotion))
                    else:
                        # Normal move
                        all_possible_moves.append((square, end_square, None))

                temp_board &= temp_board - 1

        return all_possible_moves

    def get_capture_moves(self, is_white):
        """Get only legal capture moves (for quiescence search)"""
        all_moves = self.get_all_possible_moves(is_white)
        capture_moves = []

        for start_square, end_square, promotion in all_moves:
            # Check if there's a piece to capture at end_square
            if self._get_piece(end_square) is not None:
                capture_moves.append((start_square, end_square, promotion))
            # Also include en passant captures
            elif abs(self._get_piece(start_square)) == 1:  # Pawn
                if self.last_move:
                    last_start, last_end, last_piece = self.last_move
                    if abs(last_piece) == 1 and abs(last_start - last_end) == 16:
                        # Could be en passant
                        if abs(last_end // 8 - start_square // 8) == 1 and abs(last_end % 8 - start_square % 8) == 1:
                            if abs(end_square % 8 - last_end % 8) == 0:  # Same file
                                capture_moves.append((start_square, end_square, promotion))

        # Filter for legal moves (don't leave king in check)
        legal_captures = []
        for start_square, end_square, promotion in capture_moves:
            board_state = self._save_board_state()
            self.make_move(start_square, end_square, promotion)
            if not self._is_in_check(is_white):
                legal_captures.append((start_square, end_square, promotion))
            self._restore_board_state(board_state)

        return legal_captures

    def get_tactical_moves(self, is_white):
        """Get legal capture moves and checking moves (for quiescence search)"""
        all_moves = self.get_all_possible_moves(is_white)
        tactical_moves = []
        opponent_is_white = not is_white

        for start_square, end_square, promotion in all_moves:
            # Check if move is a capture BEFORE making it
            is_capture = self._get_piece(end_square) is not None

            board_state = self._save_board_state()
            self.make_move(start_square, end_square, promotion)

            # Check if move gives check
            is_checking = self._is_in_check(opponent_is_white)

            self._restore_board_state(board_state)

            # Include if is capture OR gives check (will be filtered for legality next)
            if is_capture or is_checking:
                tactical_moves.append((start_square, end_square, promotion))

        # Filter for legal moves (don't leave king in check)
        legal_tactical = []
        for start_square, end_square, promotion in tactical_moves:
            board_state = self._save_board_state()
            self.make_move(start_square, end_square, promotion)
            if not self._is_in_check(is_white):
                legal_tactical.append((start_square, end_square, promotion))
            self._restore_board_state(board_state)

        return legal_tactical

    def get_legal_moves(self, is_white):
        """Get only legal moves (that don't leave king in check)"""
        all_moves = self.get_all_possible_moves(is_white)
        legal_moves = []

        for start_square, end_square, promotion in all_moves:
            board_state = self._save_board_state()

            self.make_move(start_square, end_square, promotion)

            if not self._is_in_check(is_white):
                legal_moves.append((start_square, end_square, promotion))

            self._restore_board_state(board_state)

        return legal_moves

    def has_legal_moves(self, is_white):
        """Check if player has at least one legal move - faster than get_legal_moves"""
        all_moves = self.get_all_possible_moves(is_white)

        for start_square, end_square, promotion in all_moves:
            board_state = self._save_board_state()

            self.make_move(start_square, end_square, promotion)

            if not self._is_in_check(is_white):
                self._restore_board_state(board_state)
                return True  # Found one legal move, stop searching

            self._restore_board_state(board_state)

        return False  # No legal moves found

    def get_board_as_matrix(self):
        """Convert bitboards to 8x8 matrix for frontend"""
        board = [[0 for _ in range(8)] for _ in range(8)]

        # Piece values: pawn=1, knight=2, bishop=3, rook=5, queen=9, king=100. Black pieces as negatives values
        piece_data = [
            (self.white_pawns, 1),
            (self.white_knights, 2),
            (self.white_bishops, 3),
            (self.white_rooks, 5),
            (self.white_queen, 9),
            (self.white_king, 100),
            (self.black_pawns, -1),
            (self.black_knights, -2),
            (self.black_bishops, -3),
            (self.black_rooks, -5),
            (self.black_queen, -9),
            (self.black_king, -100)]

        for bitboard, value in piece_data:
            while bitboard:
                square = (bitboard & -bitboard).bit_length() - 1
                row = square // 8
                col = square % 8
                board[7 - row][col] = value
                bitboard &= bitboard - 1

        self.board_history.append(board)
        return self.board_history

    def _square_to_notation(self, square):
        """Convert square index (0-63) to algebraic notation (a1-h8)"""
        col = square % 8
        row = square // 8
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        return files[col] + str(row + 1)

    def _piece_to_notation(self, piece):
        """Convert piece value to algebraic notation initial"""
        piece_type = abs(piece)
        piece_map = {
            1: '',      # pawn - no initial
            2: 'N',     # knight
            3: 'B',     # bishop
            5: 'R',     # rook
            9: 'Q',     # queen
            100: 'K'    # king
        }
        return piece_map.get(piece_type, '')

    def get_move_history_in_human_notation(self):
        """Convert move history to human-readable algebraic notation"""
        notation_list = []

        for move in self.moves_history:
            start_square, end_square, piece, promotion_piece, is_capture, is_castling = move

            # Handle castling separately
            if is_castling:
                # Kingside castling: end_col > start_col
                if end_square % 8 > start_square % 8:
                    move_notation = 'o-o'
                # Queenside castling: end_col < start_col
                else:
                    move_notation = 'o-o-o'
            else:
                piece_notation = self._piece_to_notation(piece)
                end_notation = self._square_to_notation(end_square)

                # Handle pawn moves specially (peones que capturan mostran columna de origen)
                if abs(piece) == 1:  # Pawn
                    if is_capture:
                        # For captures: show origin file + 'x' + destination
                        origin_file = chr(ord('a') + (start_square % 8))
                        move_notation = origin_file + 'x' + end_notation
                    else:
                        # For non-captures: just the destination
                        move_notation = end_notation
                else:
                    # For other pieces: initial + 'x' (if capture) + destination
                    capture_notation = 'x' if is_capture else ''
                    move_notation = piece_notation + capture_notation + end_notation

                # Handle promotion
                if promotion_piece:
                    promotion_map = {'queen': 'Q', 'rook': 'R', 'bishop': 'B', 'knight': 'N'}
                    move_notation += '=' + promotion_map.get(promotion_piece, '')

            notation_list.append(move_notation)

        return notation_list

    def show_valid_end_squares(self, startpos):
        """Get all valid end squares for a piece at startpos (filtered to exclude moves leaving king in check)"""
        row, col = startpos
        square = (7 - row) * 8 + col

        has_promotion = False

        piece = self._get_piece(square)
        is_white = (piece > 0)
        valid_moves = []

        if abs(piece) == 1:
            valid_moves = self._get_pawn_moves(square, is_white)
            if is_white and square >= 48:  # Rank 7 for white pawn
                has_promotion = True
            if not is_white and square <= 16:  # Rank 2 for black pawn
                has_promotion = True

        elif abs(piece) == 2:
            valid_moves = self._get_knight_moves(square, is_white)
        elif abs(piece) == 3:
            valid_moves = self._get_bishop_moves(square, is_white)
        elif abs(piece) == 5:
            valid_moves = self._get_rook_moves(square, is_white)
        elif abs(piece) == 9:
            valid_moves = self._get_queen_moves(square, is_white)
        elif abs(piece) == 100:
            valid_moves = self._get_king_moves(square, is_white)

        # Filter out moves that leave king in check
        legal_moves = []
        for end_square in valid_moves:
            board_state = self._save_board_state()

            self.make_move(square, end_square, None)

            if not self._is_in_check(is_white):
                legal_moves.append(end_square)

            self._restore_board_state(board_state)

        # Convert squares to [row, col] format
        valid_end_squares = [[7 - (move // 8), move % 8] for move in legal_moves]

        return {"validEndSquares": valid_end_squares, "promotion": has_promotion}

    def _get_piece(self, square):
        """Returns the piece that is at square - optimized for common pieces first"""
        # Search by probability: pawns are most common (16 each), then others
        bit = 1 << square

        if self.white_pawns & bit:
            return 1
        if self.black_pawns & bit:
            return -1
        if self.white_knights & bit:
            return 2
        if self.black_knights & bit:
            return -2
        if self.white_bishops & bit:
            return 3
        if self.black_bishops & bit:
            return -3
        if self.white_rooks & bit:
            return 5
        if self.black_rooks & bit:
            return -5
        if self.white_queen & bit:
            return 9
        if self.black_queen & bit:
            return -9
        if self.white_king & bit:
            return 100
        if self.black_king & bit:
            return -100
        return None

    def _get_white_pieces(self):
        return self.white_pawns | self.white_knights | self.white_bishops | self.white_rooks | self.white_queen | self.white_king

    def _get_black_pieces(self):
        return self.black_pawns | self.black_knights | self.black_bishops | self.black_rooks | self.black_queen | self.black_king

    def _is_square_occupied_by_enemy_piece(self, square, is_white):
        """Check if square is occupied by enemy piece"""
        enemy_pieces = self._get_black_pieces() if is_white else self._get_white_pieces()
        return (enemy_pieces >> square) & 1

    def _is_square_occupied_by_friendly_piece(self, square, is_white):
        """Check if square is occupied by friendly piece"""
        ally_pieces = self._get_white_pieces() if is_white else self._get_black_pieces()
        return (ally_pieces >> square) & 1

    def _is_square_occupied(self, square):
        """Check if square is occupied"""
        pieces = self._get_white_pieces() | self._get_black_pieces()
        return (pieces >> square) & 1

    def _get_pawn_moves(self, square, is_white):
        """Get valid pawn moves"""
        moves = []

        if is_white:
            # Move forward - one square
            forward_square = square + 8
            forward_square2 = square + 16
            if forward_square < 64 and not self._is_square_occupied(forward_square):
                moves.append(forward_square)
                # Move forward - two squares
                if square < 16 and not self._is_square_occupied(forward_square2):
                    moves.append(forward_square2)

            # Capture diagonals
            if square % 8 > 0:  # Not on a-file
                capture_square = square + 7
                if capture_square < 64 and self._is_square_occupied_by_enemy_piece(capture_square, is_white):
                    moves.append(capture_square)
            if square % 8 < 7:  # Not on h-file
                capture_square = square + 9
                if capture_square < 64 and self._is_square_occupied_by_enemy_piece(capture_square, is_white):
                    moves.append(capture_square)

            # En passant
            if square // 8 == 4:  # White pawn on rank 5
                last_start, last_end, last_piece = self.last_move
                if last_piece == -1 and abs(last_start - last_end) == 16: # Check if last move was a black pawn moving two squares
                    if abs(square % 8 - last_end % 8) == 1:# Check if enemy pawn is on adjacent file
                        en_passant_square = last_end + 8 # En passant capture
                        moves.append(en_passant_square)

        else:
            # Move forward - one square
            forward_square = square - 8
            forward_square2 = square - 16
            if forward_square >= 0 and not self._is_square_occupied(forward_square):
                moves.append(forward_square)
                # Move forward - two squares
                if square >= 48 and not self._is_square_occupied(forward_square2):
                    moves.append(forward_square2)

            # Capture diagonals
            if square % 8 > 0:  # Not on a-file
                capture_square = square - 9
                if capture_square >= 0 and self._is_square_occupied_by_enemy_piece(capture_square, is_white):
                    moves.append(capture_square)
            if square % 8 < 7:  # Not on h-file
                capture_square = square - 7
                if capture_square >= 0 and self._is_square_occupied_by_enemy_piece(capture_square, is_white):
                    moves.append(capture_square)

            # En passant
            if self.last_move and square // 8 == 3:  # Black pawn on rank 4
                last_start, last_end, last_piece = self.last_move
                if last_piece == 1 and abs(last_start - last_end) == 16: # Check if last move was a white pawn moving two squares
                    if abs(square % 8 - last_end % 8) == 1: # Check if enemy pawn is on adjacent file
                        en_passant_square = last_end - 8 # En passant capture
                        moves.append(en_passant_square)

        return moves

    def _get_knight_moves(self, square, is_white):
        """Get valid knight moves"""
        moves = []
        knight_offsets = [6, 10, 15, 17, -6, -10, -15, -17]
        row, col = square // 8, square % 8

        for offset in knight_offsets:
            target_square = square + offset
            if 0 <= target_square < 64:
                target_row, target_col = target_square // 8, target_square % 8
                if abs(row - target_row) <= 2 and abs(col - target_col) <= 2: # Validate no wrapping -> Knights can not wrap the board
                    if not self._is_square_occupied_by_friendly_piece(target_square, is_white):
                        moves.append(target_square)

        return moves

    def _get_bishop_moves(self, square, is_white):
        """Get valid bishop moves (diagonals)"""
        moves = []
        directions = [7, 9, -7, -9]

        for direction in directions:
            target = square + direction
            while 0 <= target < 64:
                # Validate no wrapping -> bishops can not wrap the board
                if abs((target // 8) - (square // 8)) != abs((target % 8) - (square % 8)):
                    break
                if self._is_square_occupied_by_friendly_piece(target, is_white):
                    break
                moves.append(target)
                if self._is_square_occupied_by_enemy_piece(target, is_white):
                    break
                target += direction

        return moves

    def _get_rook_moves(self, square, is_white):
        """Get valid rook moves (horizontal/vertical)"""
        moves = []
        directions = [1, -1, 8, -8]

        for direction in directions:
            target = square + direction
            while 0 <= target < 64:
                # Validate no wrapping -> rooks can not wrap the board
                if direction in [1, -1] and (target // 8) != (square // 8):
                    break
                if self._is_square_occupied_by_friendly_piece(target, is_white):
                    break
                moves.append(target)
                if self._is_square_occupied_by_enemy_piece(target, is_white):
                    break
                target += direction

        return moves

    def _get_queen_moves(self, square, is_white):
        """Get valid queen moves (bishop + rook)"""
        return self._get_bishop_moves(square, is_white) + self._get_rook_moves(square, is_white)

    def _get_king_moves(self, square, is_white):
        """Get valid king moves (one square in any direction)"""
        moves = []
        directions = [1, -1, 8, -8, 7, 9, -7, -9]
        row, col = square // 8, square % 8

        for direction in directions:
            target = square + direction
            if 0 <= target < 64:
                target_row, target_col = target // 8, target % 8
                if abs(row - target_row) <= 1 and abs(col - target_col) <= 1:  # Validate no wrapping -> Kings can not wrap the board
                    if not self._is_square_occupied_by_friendly_piece(target, is_white):
                        moves.append(target)

        # Castling moves
        if is_white:
            # White castling - check king is not in check and hasn't moved
            if square == 4 and not self.white_king_moved and not self._is_square_attacked_by_enemy(4, is_white):
                # Kingside castling (e1 to g1)
                if (not self.white_rook_h_moved and
                    self._get_piece(5) is None and self._get_piece(6) is None and
                    self._get_piece(7) == 5):  # f1 and g1 empty, h1 has white rook
                    # Check if f1 is not attacked (intermediate square)
                    if not self._is_square_attacked_by_enemy(5, is_white):
                        moves.append(6)

                # Queenside castling (e1 to c1)
                if (not self.white_rook_a_moved and
                    self._get_piece(3) is None and self._get_piece(2) is None and
                    self._get_piece(1) is None and self._get_piece(0) == 5):  # d1, c1, b1 empty, a1 has white rook
                    # Check if d1 is not attacked (intermediate square)
                    if not self._is_square_attacked_by_enemy(3, is_white):
                        moves.append(2)
        else:
            # Black castling - check king is not in check and hasn't moved
            if square == 60 and not self.black_king_moved and not self._is_square_attacked_by_enemy(60, is_white):
                # Kingside castling (e8 to g8)
                if (not self.black_rook_h_moved and
                    self._get_piece(61) is None and self._get_piece(62) is None and
                    self._get_piece(63) == -5):  # f8 and g8 empty, h8 has black rook
                    # Check if f8 is not attacked (intermediate square)
                    if not self._is_square_attacked_by_enemy(61, is_white):
                        moves.append(62)

                # Queenside castling (e8 to c8)
                if (not self.black_rook_a_moved and
                    self._get_piece(59) is None and self._get_piece(58) is None and
                    self._get_piece(57) is None and self._get_piece(56) == -5):  # e8, d8, c8, b8 empty, a8 has black rook
                    # Check if d8 is not attacked (intermediate square)
                    if not self._is_square_attacked_by_enemy(59, is_white):
                        moves.append(58)

        return moves

    def _is_square_attacked_by_enemy(self, square, is_white):
        """Check if a square is attacked by any enemy piece"""
        if is_white:
            return self._check_attacks(square, self.black_pawns, self.black_knights,
                                     self.black_bishops, self.black_rooks,
                                     self.black_queen, self.black_king, is_white=True)
        else:
            return self._check_attacks(square, self.white_pawns, self.white_knights,
                                     self.white_bishops, self.white_rooks,
                                     self.white_queen, self.white_king, is_white=False)

    def _check_attacks(self, square, pawns, knights, bishops, rooks, queen, king, is_white):
        """Check if square is attacked by any enemy piece"""
        row, col = square >> 3, square & 7

        # Pawns
        if is_white:
            # Black pawns attack downward (square - 7, square - 9)
            # So we check if black pawn is above: square + 7, square + 9
            if square < 56:
                if col < 7 and ((pawns >> (square + 9)) & 1):
                    return True
                if col > 0 and ((pawns >> (square + 7)) & 1):
                    return True
        else:
            # White pawns attack upward (square + 7, square + 9)
            # So we check if white pawn is below: square - 7, square - 9
            if square >= 8:
                if col < 7 and ((pawns >> (square - 9)) & 1):
                    return True
                if col > 0 and ((pawns >> (square - 7)) & 1):
                    return True

        # Knights
        if knights:
            for offset in [6, 10, 15, 17, -6, -10, -15, -17]:
                target = square + offset
                if 0 <= target < 64:
                    target_row, target_col = target >> 3, target & 7
                    if abs(row - target_row) <= 2 and abs(col - target_col) <= 2:
                        if (knights >> target) & 1:
                            return True

        # Bishops and Queen (diagonals)
        if bishops or queen:
            for direction in [7, 9, -7, -9]:
                target = square + direction
                while 0 <= target < 64:
                    if abs((target >> 3) - row) != abs((target & 7) - col):
                        break
                    if ((bishops >> target) & 1) or ((queen >> target) & 1):
                        return True
                    if self._is_square_occupied(target):
                        break
                    target += direction

        # Rooks and Queen (straight lines)
        if rooks or queen:
            for direction in [1, -1, 8, -8]:
                target = square + direction
                while 0 <= target < 64:
                    if direction in [1, -1] and (target >> 3) != row:
                        break
                    if ((rooks >> target) & 1) or ((queen >> target) & 1):
                        return True
                    if self._is_square_occupied(target):
                        break
                    target += direction

        # King
        if king:
            for direction in [1, -1, 8, -8, 7, 9, -7, -9]:
                target = square + direction
                if 0 <= target < 64:
                    target_row, target_col = target >> 3, target & 7
                    if abs(row - target_row) <= 1 and abs(col - target_col) <= 1:
                        if (king >> target) & 1:
                            return True

        return False


    def _is_in_check(self, is_white):
        """Check if the specified side's king is in check"""
        if is_white:
            king_square = (self.white_king & -self.white_king).bit_length() - 1
        else:
            king_square = (self.black_king & -self.black_king).bit_length() - 1

        return self._is_square_attacked_by_enemy(king_square, is_white)

    def _remove_piece_bit(self, square, piece):
        """Remove a piece from the board at the given square"""
        piece_attrs = {
            1: 'white_pawns', -1: 'black_pawns',
            2: 'white_knights', -2: 'black_knights',
            3: 'white_bishops', -3: 'black_bishops',
            5: 'white_rooks', -5: 'black_rooks',
            9: 'white_queen', -9: 'black_queen',
            100: 'white_king', -100: 'black_king'
        }
        attr = getattr(self, piece_attrs[piece])
        setattr(self, piece_attrs[piece], attr & ~(1 << square))

    def _add_piece_bit(self, square, piece):
        """Add a piece to the board at the given square"""
        piece_attrs = {
            1: 'white_pawns', -1: 'black_pawns',
            2: 'white_knights', -2: 'black_knights',
            3: 'white_bishops', -3: 'black_bishops',
            5: 'white_rooks', -5: 'black_rooks',
            9: 'white_queen', -9: 'black_queen',
            100: 'white_king', -100: 'black_king'
        }
        attr = getattr(self, piece_attrs[piece])
        setattr(self, piece_attrs[piece], attr | (1 << square))

    def make_move(self, start_square, end_square, promotion_piece=None):
        """Makes a move using square indices (0-63)"""
        piece = self._get_piece(start_square)

        # Remove piece from start_square
        self._remove_piece_bit(start_square, piece)

        # Remove any piece at end_square (capture)
        captured_piece = self._get_piece(end_square)
        is_capture = captured_piece is not None
        if captured_piece is not None:
            self._remove_piece_bit(end_square, captured_piece)

        # Handle en passant capture
        elif abs(piece) == 1 and abs(start_square // 8 - end_square // 8) == 1 and abs(start_square % 8 - end_square % 8) == 1 and self.last_move:
            # Pawn moved diagonally but no piece at destination - verify it's valid en passant
            last_start, last_end, last_piece = self.last_move
            # Check if last move was enemy pawn moving two squares and is adjacent
            if abs(last_piece) == 1 and abs(last_start - last_end) == 16 and abs(end_square % 8 - last_end % 8) == 0:
                # Valid en passant - remove enemy pawn
                if piece > 0:  # White pawn
                    en_passant_capture_square = end_square - 8
                else:  # Black pawn
                    en_passant_capture_square = end_square + 8

                en_passant_victim = self._get_piece(en_passant_capture_square)
                if en_passant_victim is not None:
                    self._remove_piece_bit(en_passant_capture_square, en_passant_victim)

        # Place piece at end_square
        if promotion_piece:
            promotion_map = {'queen': 9, 'rook': 5, 'bishop': 3, 'knight': 2}
            promoted_type = promotion_map.get(promotion_piece.lower(), abs(piece))
            piece_selected_for_promotion = promoted_type if (piece > 0) else -promoted_type
            self._add_piece_bit(end_square, piece_selected_for_promotion)
        else:
            self._add_piece_bit(end_square, piece)

        # Handle castling - move the rook and mark castling history
        if abs(piece) == 100:  # King move
            if piece > 0:  # White king
                # Kingside castling (e1 to g1)
                if start_square == 4 and end_square == 6:
                    self._remove_piece_bit(7, 5)  # Remove rook from h1
                    self._add_piece_bit(5, 5)      # Add rook to f1
                    self.white_kingside_castled = True
                # Queenside castling (e1 to c1)
                elif start_square == 4 and end_square == 2:
                    self._remove_piece_bit(0, 5)   # Remove rook from a1
                    self._add_piece_bit(3, 5)      # Add rook to d1
                    self.white_queenside_castled = True
            else:  # Black king
                # Kingside castling (e8 to g8)
                if start_square == 60 and end_square == 62:
                    self._remove_piece_bit(63, -5) # Remove rook from h8
                    self._add_piece_bit(61, -5)    # Add rook to f8
                    self.black_kingside_castled = True
                # Queenside castling (e8 to c8)
                elif start_square == 60 and end_square == 58:
                    self._remove_piece_bit(56, -5) # Remove rook from a8
                    self._add_piece_bit(59, -5)    # Add rook to d8
                    self.black_queenside_castled = True

        # Track castling rights - mark king as moved
        if abs(piece) == 100:  # King moved
            if piece > 0:
                self.white_king_moved = True
            else:
                self.black_king_moved = True

        # Track castling rights - mark rook as moved
        if abs(piece) == 5:  # Rook moved
            if piece > 0:  # White rook
                if start_square == 0:
                    self.white_rook_a_moved = True
                elif start_square == 7:
                    self.white_rook_h_moved = True
            else:  # Black rook
                if start_square == 56:
                    self.black_rook_a_moved = True
                elif start_square == 63:
                    self.black_rook_h_moved = True

        # Also mark rook as moved if it's captured
        if captured_piece and abs(captured_piece) == 5:
            if captured_piece > 0:  # White rook captured
                if end_square == 0:
                    self.white_rook_a_moved = True
                elif end_square == 7:
                    self.white_rook_h_moved = True
            else:  # Black rook captured
                if end_square == 56:
                    self.black_rook_a_moved = True
                elif end_square == 63:
                    self.black_rook_h_moved = True

        # Update position bonuses (O(1) operation)
        self._update_position_bonus(piece, start_square, end_square)

        # If capturing, also remove captured piece's bonus
        if captured_piece is not None:
            self._update_position_bonus(captured_piece, end_square, end_square)

        # Update 50-move rule counter and position history
        if captured_piece is not None or abs(piece) == 1:  # Capture or pawn move
            self.halfmove_clock = 0
            self.position_history = {}  # Reset position history on capture/pawn move
        else:
            self.halfmove_clock += 1
            # Record position for threefold repetition
            pos_hash = self._get_position_hash()
            self.position_history[pos_hash] = self.position_history.get(pos_hash, 0) + 1

        # Save move for en passant detection
        self.last_move = (start_square, end_square, piece)

        # Detect castling (king move with 2-square horizontal distance)
        is_castling = abs(piece) == 100 and abs(end_square % 8 - start_square % 8) == 2

        # Save move to history (including piece, capture flag, and castling flag)
        self.moves_history.append((start_square, end_square, piece, promotion_piece, is_capture, is_castling))


    def check_game_status(self, last_player_is_white=None):
        """Check if the game is over - called after a move, checks if the opponent has legal moves"""
        # After a move is made, it's the opponent's turn
        # If last_player_is_white is None, assume it's the human
        if last_player_is_white is None:
            last_player_is_white = self.human_is_white

        current_player_is_white = not last_player_is_white

        # Check for threefold repetition (draw)
        current_pos_hash = self._get_position_hash()
        if self.position_history.get(current_pos_hash, 0) >= 3:
            return {
                'gameIsFinished': True,
                'winner': None,
            }

        # Check for 50-move rule (draw)
        if self.halfmove_clock >= 100:  # 100 halfmoves = 50 moves
            return {
                'gameIsFinished': True,
                'winner': None,
            }

        # Check for insufficient material (draw)
        if self._has_insufficient_material():
            return {
                'gameIsFinished': True,
                'winner': None,
            }

        has_moves = self.has_legal_moves(current_player_is_white)

        if not has_moves:
            # No legal moves available
            if self._is_in_check(current_player_is_white):
                # In check with no legal moves = checkmate
                winner = "black" if current_player_is_white else "white"
                return {
                    'gameIsFinished': True,
                    'winner': winner,
                }
            else:
                # No check, no legal moves = stalemate
                return {
                    'gameIsFinished': True,
                    'winner': None,
                }

        return {
            'gameIsFinished': False,
            'winner': None
        }
    
    def transform_ai_evaluation_score_into_a_human_readable_score(self, score):
        """Convert AI evaluation score to human-readable format (positive for white, negative for black)"""
        # Convert from centipawns to pawns (standard chess engine scale)
        score_in_pawns = round(score / 100, 2)

        if self.human_is_white:
            return -score_in_pawns
        return score_in_pawns

    def let_ai_make_move(self):
        """AI makes a move - discovers all legal moves and picks the best one"""
        ai_is_white = not self.human_is_white

        # Reset transposition table and killer moves for fresh search
        self.transposition_table = {}
        self.killer_moves = [set() for _ in range(5)]

        legal_moves = self.get_legal_moves(ai_is_white)

        if not legal_moves:
            return None

        # Adjust search depth based on number of legal moves
        num_moves = len(legal_moves)
        if num_moves > 15:
            self.depth = 1  # Many moves = shallower search
        elif num_moves < 5:
            self.depth = 3  # Few moves = deeper search
        else:
            self.depth = 2  # Default

        # Update killer moves array size based on new depth
        self.killer_moves = [set() for _ in range(self.depth + 1)]

        best_move, best_evaluation = self.select_best_move(legal_moves)

        if best_move is None:
            best_move = legal_moves[0]
            best_evaluation = 0

        start_square, end_square, promotion = best_move

        startpos = [7 - (start_square // 8), start_square % 8]
        endpos = [7 - (end_square // 8), end_square % 8]

        self.make_move(start_square, end_square, promotion)

        return (startpos, endpos, best_evaluation)
    

    def select_best_move(self, all_possible_moves):
        """Iterative deepening: search at depth 1, 2, 3, 4..."""
        ai_is_white = not self.human_is_white
        best_move = None
        best_evaluation = None

        for current_depth in range(1, self.depth + 1):
            self.current_search_depth = current_depth
            move_at_depth, eval_at_depth = self._select_best_move_at_depth(all_possible_moves, ai_is_white)

            if move_at_depth:
                best_move = move_at_depth
                best_evaluation = eval_at_depth

        return (best_move, best_evaluation) if best_move else (None, None)

    def _select_best_move_at_depth(self, all_possible_moves, ai_is_white):
        """Select best move at a specific depth"""
        best_move = None
        best_evaluation = float('-inf')

        all_possible_moves = self._sort_moves_by_priority(all_possible_moves, ai_is_white, depth=0)

        for start_square, end_square, promotion in all_possible_moves:
            evaluation = self.evaluate_move(start_square, end_square, promotion, depth=self.current_search_depth)
            if evaluation > best_evaluation:
                best_evaluation = evaluation
                best_move = (start_square, end_square, promotion)

        return (best_move, best_evaluation) if best_move else (None, None)

    def evaluate_move(self, start_square, end_square, promotion=None, depth=None):
        """Evaluates a move by making it, evaluating the position, and undoing it"""
        if depth is None:
            depth = self.depth

        board_state = self._save_board_state()

        self.make_move(start_square, end_square, promotion)
        evaluation = self.minimax(depth, False)

        self._restore_board_state(board_state)

        return evaluation

    def evaluate_board(self):
        """Evaluates the current board position by counting material and positional factors"""
        white_material = (self.white_pawns.bit_count() * 100 +
                         self.white_knights.bit_count() * 300 +
                         self.white_bishops.bit_count() * 300 +
                         self.white_rooks.bit_count() * 500 +
                         self.white_queen.bit_count() * 900)

        black_material = (self.black_pawns.bit_count() * 100 +
                         self.black_knights.bit_count() * 300 +
                         self.black_bishops.bit_count() * 300 +
                         self.black_rooks.bit_count() * 500 +
                         self.black_queen.bit_count() * 900)

        # Castling bonus (50 centipawns = 50 points)
        white_bonus = 0
        black_bonus = 0

        # Give bonus for castling (whether kingside or queenside)
        if self.white_kingside_castled or self.white_queenside_castled:
            white_bonus += 50

        if self.black_kingside_castled or self.black_queenside_castled:
            black_bonus += 50

        # Doubled pawns penalty/bonus (20 points per doubled pawn)
        white_doubled = self._count_doubled_pawns(self.white_pawns)
        black_doubled = self._count_doubled_pawns(self.black_pawns)

        # Penalize own doubled pawns, bonus for opponent's doubled pawns
        white_bonus -= white_doubled * 20      # Penalize white's own doubled pawns
        white_bonus += black_doubled * 20      # Bonus for black's doubled pawns
        black_bonus -= black_doubled * 20      # Penalize black's own doubled pawns
        black_bonus += white_doubled * 20      # Bonus for white's doubled pawns

        # Add position table bonuses (O(1) - precalculated in make_move)
        white_bonus += self.white_position_bonus
        black_bonus += self.black_position_bonus

        ai_is_white = not self.human_is_white
        evaluation = (white_material + white_bonus) - (black_material + black_bonus)
        return evaluation if ai_is_white else -evaluation

    def quiescence(self, is_maximizing, alpha=float('-inf'), beta=float('inf'), depth=0):
        """Quiescence search: evaluate capture sequences to avoid horizon effect"""
        # Limit depth to avoid infinite loops
        if depth > 10:
            return self.evaluate_board()

        # Stand-pat: evaluate current position without captures
        stand_pat = self.evaluate_board()

        if is_maximizing:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)

        # Get current side
        ai_is_white = not self.human_is_white
        is_white = ai_is_white if is_maximizing else not ai_is_white

        # Generate and evaluate tactical moves (captures + checks)
        tactical_moves = self.get_tactical_moves(is_white)
        if not tactical_moves:
            return stand_pat

        tactical_moves = self._sort_moves_by_priority(tactical_moves, is_white, depth=0)

        for start_square, end_square, promotion in tactical_moves:
            board_state = self._save_board_state()
            self.make_move(start_square, end_square, promotion)

            # Recursively search tactical moves by opponent
            value = self.quiescence(not is_maximizing, alpha, beta, depth + 1)

            self._restore_board_state(board_state)

            if is_maximizing:
                if value >= beta:
                    return beta
                alpha = max(alpha, value)
            else:
                if value <= alpha:
                    return alpha
                beta = min(beta, value)

        return alpha if is_maximizing else beta

    def minimax(self, depth, is_maximizing, alpha=float('-inf'), beta=float('inf')):
        if depth == 0:
            # Use quiescence search to evaluate capture sequences
            return self.quiescence(is_maximizing, alpha, beta)

        # Check transposition table
        board_hash = self._get_board_hash()
        if board_hash in self.transposition_table:
            cached_depth, cached_eval = self.transposition_table[board_hash]
            if cached_depth >= depth:
                return cached_eval

        ai_is_white = not self.human_is_white
        is_white = ai_is_white if is_maximizing else not ai_is_white

        legal_moves = self.get_legal_moves(is_white)

        # Check if current player is in checkmate or stalemate (no legal moves)
        if not legal_moves:
            if self._is_in_check(is_white):
                # Checkmate - bad for the player to move (is_white)
                best_evaluation = -1000000 if is_maximizing else 1000000
            else:
                # Stalemate - draw
                best_evaluation = self.evaluate_board()

            self.transposition_table[board_hash] = (depth, best_evaluation)
            return best_evaluation

        legal_moves = self._sort_moves_by_priority(legal_moves, is_white, depth)

        if is_maximizing:
            best_evaluation = float('-inf')
            for start_square, end_square, promotion in legal_moves:
                board_state = self._save_board_state()
                self.make_move(start_square, end_square, promotion)

                # Check if opponent is in checkmate
                opponent_is_white = not is_white
                if self._is_in_check(opponent_is_white) and not self.has_legal_moves(opponent_is_white):
                    evaluation = 1000000
                    self._restore_board_state(board_state)
                    return evaluation

                evaluation = self.minimax(depth - 1, False, alpha, beta)
                self._restore_board_state(board_state)

                best_evaluation = max(best_evaluation, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    self.killer_moves[depth].add((start_square, end_square, promotion))
                    break

            self.transposition_table[board_hash] = (depth, best_evaluation)
            return best_evaluation
        else:
            best_evaluation = float('inf')
            for start_square, end_square, promotion in legal_moves:
                board_state = self._save_board_state()
                self.make_move(start_square, end_square, promotion)

                # Check if opponent is in checkmate
                opponent_is_white = not is_white
                if self._is_in_check(opponent_is_white) and not self.has_legal_moves(opponent_is_white):
                    evaluation = -1000000
                    self._restore_board_state(board_state)
                    return evaluation

                evaluation = self.minimax(depth - 1, True, alpha, beta)
                self._restore_board_state(board_state)

                best_evaluation = min(best_evaluation, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    self.killer_moves[depth].add((start_square, end_square, promotion))
                    break

            self.transposition_table[board_hash] = (depth, best_evaluation)
            return best_evaluation

    def _get_board_hash(self):
        """Get hash of current board position for transposition table"""
        return (
            self.white_pawns, self.white_knights, self.white_bishops,
            self.white_rooks, self.white_queen, self.white_king,
            self.black_pawns, self.black_knights, self.black_bishops,
            self.black_rooks, self.black_queen, self.black_king
        )

    def _get_position_bonus_value(self, piece, square, is_white):
        """Get position bonus for a piece at a square (normalized for white's perspective)"""
        # Normalize square for white (flip if black piece)
        if not is_white:
            square = 63 - square

        if abs(piece) == 2:  # Knight
            return self.KNIGHT_TABLE[square]
        elif abs(piece) == 3:  # Bishop
            return self.BISHOP_TABLE[square]
        elif abs(piece) == 1:  # Pawn
            return self.PAWN_TABLE[square]
        return 0

    def _update_position_bonus(self, piece, start_square, end_square):
        """Update position bonuses when a piece moves"""
        is_white = piece > 0

        # Remove bonus from old position
        old_bonus = self._get_position_bonus_value(piece, start_square, is_white)
        # Add bonus for new position
        new_bonus = self._get_position_bonus_value(piece, end_square, is_white)

        if is_white:
            self.white_position_bonus -= old_bonus
            self.white_position_bonus += new_bonus
        else:
            self.black_position_bonus -= old_bonus
            self.black_position_bonus += new_bonus

    def _count_doubled_pawns(self, pawns_bitboard):
        """Count the number of doubled pawns (multiple pawns in same file)"""
        doubled_count = 0
        # Check each file (column) 0-7
        for file in range(8):
            # Extract all pawns in this file
            file_mask = 0x0101010101010101 << file
            pawns_in_file = bin(pawns_bitboard & file_mask).count('1')
            # If more than 1 pawn in file, count the extras as doubled
            if pawns_in_file > 1:
                doubled_count += pawns_in_file - 1
        return doubled_count

    def _get_position_hash(self):
        """Generate a hash of the current board position for threefold repetition detection"""
        # Include bitboards and castling rights in the hash
        position_tuple = (
            self.white_pawns, self.white_knights, self.white_bishops,
            self.white_rooks, self.white_queen, self.white_king,
            self.black_pawns, self.black_knights, self.black_bishops,
            self.black_rooks, self.black_queen, self.black_king,
            self.white_king_moved, self.black_king_moved,
            self.white_rook_a_moved, self.white_rook_h_moved,
            self.black_rook_a_moved, self.black_rook_h_moved
        )
        return hash(position_tuple)

    def _has_insufficient_material(self):
        """Check if the game is a draw due to insufficient material"""
        # Count material for each side
        white_pawns = bin(self.white_pawns).count('1')
        white_knights = bin(self.white_knights).count('1')
        white_bishops = bin(self.white_bishops).count('1')
        white_rooks = bin(self.white_rooks).count('1')
        white_queen = bin(self.white_queen).count('1')

        black_pawns = bin(self.black_pawns).count('1')
        black_knights = bin(self.black_knights).count('1')
        black_bishops = bin(self.black_bishops).count('1')
        black_rooks = bin(self.black_rooks).count('1')
        black_queen = bin(self.black_queen).count('1')

        # If either side has pawns, rooks, or queen, there's sufficient material
        if white_pawns > 0 or black_pawns > 0 or white_rooks > 0 or black_rooks > 0 or white_queen > 0 or black_queen > 0:
            return False

        # Count total pieces (excluding kings)
        white_pieces = white_knights + white_bishops
        black_pieces = black_knights + black_bishops

        # King vs King - insufficient material
        if white_pieces == 0 and black_pieces == 0:
            return True

        # King + 1 Knight vs King - insufficient material
        if white_pieces == 1 and black_pieces == 0 and white_knights == 1:
            return True
        if black_pieces == 1 and white_pieces == 0 and black_knights == 1:
            return True

        # King + 1 Bishop vs King - insufficient material
        if white_pieces == 1 and black_pieces == 0 and white_bishops == 1:
            return True
        if black_pieces == 1 and white_pieces == 0 and black_bishops == 1:
            return True

        # King + Knight vs King + Knight (same color bishop) - insufficient material
        # King + Bishop vs King + Bishop (same color bishop) - insufficient material
        # For now, we'll keep the game going if both sides have pieces
        # (implementing same-color bishop check requires more complex logic)

        return False

    def _save_board_state(self):
        """Saves the current board state"""
        return [
            self.white_pawns, self.white_knights, self.white_bishops,
            self.white_rooks, self.white_queen, self.white_king,
            self.black_pawns, self.black_knights, self.black_bishops,
            self.black_rooks, self.black_queen, self.black_king,
            self.last_move,
            self.white_king_moved, self.black_king_moved,
            self.white_rook_a_moved, self.white_rook_h_moved,
            self.black_rook_a_moved, self.black_rook_h_moved,
            self.halfmove_clock,
            dict(self.position_history),  # Copy the position history
            self.white_kingside_castled, self.white_queenside_castled,
            self.black_kingside_castled, self.black_queenside_castled,
            self.white_position_bonus, self.black_position_bonus,
            list(self.moves_history)  # Copy the moves history
        ]

    def _restore_board_state(self, board_state):
        """Restores the board to a previous state"""
        (self.white_pawns, self.white_knights, self.white_bishops,
         self.white_rooks, self.white_queen, self.white_king,
         self.black_pawns, self.black_knights, self.black_bishops,
         self.black_rooks, self.black_queen, self.black_king,
         self.last_move,
         self.white_king_moved, self.black_king_moved,
         self.white_rook_a_moved, self.white_rook_h_moved,
         self.black_rook_a_moved, self.black_rook_h_moved,
         self.halfmove_clock,
         self.position_history,
         self.white_kingside_castled, self.white_queenside_castled,
         self.black_kingside_castled, self.black_queenside_castled,
         self.white_position_bonus, self.black_position_bonus,
         self.moves_history) = board_state
    