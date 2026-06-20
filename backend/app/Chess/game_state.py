import random

class GameState:
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

        return board
    
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

        else:
            # Move forward - one square
            forward_square = square - 8
            forward_square2 = square - 16
            if forward_square > 0 and not self._is_square_occupied(forward_square):
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
        if captured_piece is not None:
            self._remove_piece_bit(end_square, captured_piece)

        # Place piece at end_square
        if promotion_piece:
            promotion_map = {'queen': 9, 'rook': 5, 'bishop': 3, 'knight': 2}
            promoted_type = promotion_map.get(promotion_piece.lower(), abs(piece))
            piece_selected_for_promotion = promoted_type if (piece > 0) else -promoted_type
            self._add_piece_bit(end_square, piece_selected_for_promotion)
        else:
            self._add_piece_bit(end_square, piece)


    def check_game_status(self, last_player_is_white=None):
        """Check if the game is over - called after a move, checks if the opponent has legal moves"""
        # After a move is made, it's the opponent's turn
        # If last_player_is_white is None, assume it's the human
        if last_player_is_white is None:
            last_player_is_white = self.human_is_white

        current_player_is_white = not last_player_is_white

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
    
    def let_ai_make_move(self):
        """AI makes a move - discovers all legal moves and picks the best one"""
        ai_is_white = not self.human_is_white

        # Reset transposition table and killer moves for fresh search
        self.transposition_table = {}
        self.killer_moves = [set() for _ in range(5)]

        legal_moves = self.get_legal_moves(ai_is_white)

        if not legal_moves:
            return None

        best_move = self.select_best_move(legal_moves)

        if best_move is None:
            best_move = legal_moves[0]

        start_square, end_square, promotion = best_move

        startpos = [7 - (start_square // 8), start_square % 8]
        endpos = [7 - (end_square // 8), end_square % 8]

        self.make_move(start_square, end_square, promotion)

        return (startpos, endpos)
    

    def select_best_move(self, all_possible_moves):
        """Iterative deepening: search at depth 1, 2, 3, 4..."""
        ai_is_white = not self.human_is_white
        best_move = None

        for current_depth in range(1, self.depth + 1):
            self.current_search_depth = current_depth
            best_move_at_depth = self._select_best_move_at_depth(all_possible_moves, ai_is_white)

            if best_move_at_depth:
                best_move = best_move_at_depth

        return best_move

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

        return best_move

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
        """Evaluates the current board position by counting material"""
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

        ai_is_white = not self.human_is_white
        return (white_material - black_material) if ai_is_white else (black_material - white_material)

    def minimax(self, depth, is_maximizing, alpha=float('-inf'), beta=float('inf')):
        if depth == 0:
            return self.evaluate_board()

        # Check transposition table
        board_hash = self._get_board_hash()
        if board_hash in self.transposition_table:
            cached_depth, cached_eval = self.transposition_table[board_hash]
            if cached_depth >= depth:
                return cached_eval

        ai_is_white = not self.human_is_white
        is_white = ai_is_white if is_maximizing else not ai_is_white

        legal_moves = self.get_legal_moves(is_white)
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

    def _save_board_state(self):
        """Saves the current board state"""
        return [
            self.white_pawns, self.white_knights, self.white_bishops,
            self.white_rooks, self.white_queen, self.white_king,
            self.black_pawns, self.black_knights, self.black_bishops,
            self.black_rooks, self.black_queen, self.black_king
        ]

    def _restore_board_state(self, board_state):
        """Restores the board to a previous state"""
        (self.white_pawns, self.white_knights, self.white_bishops,
         self.white_rooks, self.white_queen, self.white_king,
         self.black_pawns, self.black_knights, self.black_bishops,
         self.black_rooks, self.black_queen, self.black_king) = board_state
    