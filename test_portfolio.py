import unittest
import XiangqiGame as xg


class XiangqiGameTest(unittest.TestCase):
    def test_init(self):
        game = xg.XiangqiGame()
        # Make sure only two players.
        self.assertEqual(2, len(game.get_players()))
        # Make sure game is not already over when created.
        self.assertEqual("UNFINISHED", game.get_game_state())
        red = game.get_players()[xg.Player.get_RED()]
        black = game.get_players()[xg.Player.get_BLACK()]
        # Check opponent tracking.
        self.assertEqual(black, red.get_opponent())
        self.assertEqual(red, black.get_opponent())

    def test_make_move_manual_00(self):
        game = xg.XiangqiGame()
        players = game.get_players()
        red = players[xg.Player.get_RED()]
        black = players[xg.Player.get_BLACK()]
        board = game.get_board()
        game.make_move('a1', 'a2', red)
        self.assertFalse(black.is_in_check(board))
        game.make_move('a2', 'd2', red)
        self.assertFalse(black.is_in_check(board))
        game.make_move('d2', 'd10', red)
        self.assertTrue(black.is_in_check(board))
        game.make_move('e10', 'd10', black)
        self.assertFalse(black.is_in_check(board))

    def test_make_move_manual_01(self):
        game = xg.XiangqiGame()
        players = game.get_players()
        red = players[xg.Player.get_RED()]
        black = players[xg.Player.get_BLACK()]
        board = game.get_board()
        sb0, sb1, sb2, sb3, sb4 = black.get_pieces()['soldier']
        eb0, eb1 = black.get_pieces()['elephant']
        game.make_move('b1', 'c3', red)  # hr0
        game.make_move('c4', 'c5', red)  # sr1
        game.make_move('c3', 'd5', red)  # hr0
        game.make_move('d5', 'e7', red)  # hr0 takes sb2
        self.assertTrue(not black.belongs_to(sb2))
        check_conditions = [
            not game.is_in_check('red'),
            not game.is_in_check('black'),
            not red.is_in_check(board),
            not black.is_in_check(board),
        ]
        self.assertTrue(all(check_conditions))
        game.make_move('e7', 'f9', red)  # hr0 blocks eb1 from left
        self.assertEqual(set([(2, 8)]), set(eb1.get_moves(board)))
        game.make_move('f9', 'g7', red)  # hr0 takes sb3
        self.assertTrue(not red.belongs_to(sb3))
        game.make_move('g7', 'h9', red)  # hr0 blocks eb1 from right
        self.assertEqual(set([(2, 4)]), set(eb1.get_moves(board)))
        game.make_move('h9', 'f8', red)  # hr0 checks black king
        # black should be in check now

    def test_make_move_invalid_alg_not(self):
        game = xg.XiangqiGame()
        test_cases = (
            ('21', 'a4'),
            ('a12', 'h1'),
            ('hello', 'world'),
            ('x2', 'd9'),
            ('g22', 'd-9'),
        )

        for pos in test_cases:
            self.assertFalse(game.make_move(*pos))


class AlgNotTest(unittest.TestCase):
    def test_alg_to_row_col_within_range(self):
        test_cases = {
            "a1": (9, 0),
            "b1": (9, 1),
            "c1": (9, 2),
            "d1": (9, 3),
            "e1": (9, 4),
            "f1": (9, 5),
            "g1": (9, 6),
            "h1": (9, 7),
            "i1": (9, 8),
            # -----------------------------------------------------------------
            "a2": (8, 0),
            "b2": (8, 1),
            "c2": (8, 2),
            "d2": (8, 3),
            "e2": (8, 4),
            "f2": (8, 5),
            "g2": (8, 6),
            "h2": (8, 7),
            "i2": (8, 8),
            # -----------------------------------------------------------------
            "a3": (7, 0),
            "b3": (7, 1),
            "c3": (7, 2),
            "d3": (7, 3),
            "e3": (7, 4),
            "f3": (7, 5),
            "g3": (7, 6),
            "h3": (7, 7),
            "i3": (7, 8),
            # -----------------------------------------------------------------
            "a4": (6, 0),
            "b4": (6, 1),
            "c4": (6, 2),
            "d4": (6, 3),
            "e4": (6, 4),
            "f4": (6, 5),
            "g4": (6, 6),
            "h4": (6, 7),
            "i4": (6, 8),
            # -----------------------------------------------------------------
            "a5": (5, 0),
            "b5": (5, 1),
            "c5": (5, 2),
            "d5": (5, 3),
            "e5": (5, 4),
            "f5": (5, 5),
            "g5": (5, 6),
            "h5": (5, 7),
            "i5": (5, 8),
            # -----------------------------------------------------------------
            "a6": (4, 0),
            "b6": (4, 1),
            "c6": (4, 2),
            "d6": (4, 3),
            "e6": (4, 4),
            "f6": (4, 5),
            "g6": (4, 6),
            "h6": (4, 7),
            "i6": (4, 8),
            # -----------------------------------------------------------------
            "a7": (3, 0),
            "b7": (3, 1),
            "c7": (3, 2),
            "d7": (3, 3),
            "e7": (3, 4),
            "f7": (3, 5),
            "g7": (3, 6),
            "h7": (3, 7),
            "i7": (3, 8),
            # -----------------------------------------------------------------
            "a8": (2, 0),
            "b8": (2, 1),
            "c8": (2, 2),
            "d8": (2, 3),
            "e8": (2, 4),
            "f8": (2, 5),
            "g8": (2, 6),
            "h8": (2, 7),
            "i8": (2, 8),
            # -----------------------------------------------------------------
            "a9": (1, 0),
            "b9": (1, 1),
            "c9": (1, 2),
            "d9": (1, 3),
            "e9": (1, 4),
            "f9": (1, 5),
            "g9": (1, 6),
            "h9": (1, 7),
            "i9": (1, 8),
            # -----------------------------------------------------------------
            "a10": (0, 0),
            "b10": (0, 1),
            "c10": (0, 2),
            "d10": (0, 3),
            "e10": (0, 4),
            "f10": (0, 5),
            "g10": (0, 6),
            "h10": (0, 7),
            "i10": (0, 8),
        }
        for param, expected in test_cases.items():
            actual = xg.AlgNot.alg_to_row_col(param)
            self.assertEqual(expected, actual)

    def test_alg_to_row_col_invalid_len(self):
        test_cases = (
            "",
            "f",
            "1",
            "!",
            "abb2",
            "12049",
            "sdlfksalkdj0p21940129!"
        )

        for case in test_cases:
            with self.assertRaises(xg.AlgStrLengthError):
                xg.AlgNot.alg_to_row_col(case)

    def test_alg_to_row_col_invalid_letter(self):
        test_cases = (
            "11",
            "1b",
            "!23",
            ")10",
            " 2",
            "p2",
            "A5",
        )

        for case in test_cases:
            with self.assertRaises(xg.AlgLetterError):
                xg.AlgNot.alg_to_row_col(case)

    def test_alg_to_row_col_invalid_number_format(self):
        test_cases = (
            "a!",
            "ib",
            "g ",
            "c1.",
            "d.1",
            "e  ",
            "f3p",
        )

        for case in test_cases:
            with self.assertRaises(xg.AlgNumFormatError):
                xg.AlgNot.alg_to_row_col(case)

    def test_alg_to_row_col_number_OOB(self):
        test_cases = (
            "a-2",
            "b21",
            "i0",
            "h99",
        )

        for case in test_cases:
            with self.assertRaises(xg.AlgNumOutOfBoundsError):
                xg.AlgNot.alg_to_row_col(case)


class BoardTest(unittest.TestCase):
    def test_init(self):
        red = xg.Player(xg.Player.get_RED())
        black = xg.Player(xg.Player.get_BLACK())
        board = xg.Board((red, black))

        rp = red.get_pieces()
        bp = black.get_pieces()

        gen = xg.Player.get_GENERAL()
        adv = xg.Player.get_ADVISOR()
        ele = xg.Player.get_ELEPHANT()
        hor = xg.Player.get_HORSE()
        cha = xg.Player.get_CHARIOT()
        can = xg.Player.get_CANNON()
        sol = xg.Player.get_SOLDIER()

        expected = {
            (0, 0): bp[cha][0],
            (0, 1): bp[hor][0],
            (0, 2): bp[ele][0],
            (0, 3): bp[adv][0],
            (0, 4): bp[gen][0],
            (0, 5): bp[adv][1],
            (0, 6): bp[ele][1],
            (0, 7): bp[hor][1],
            (0, 8): bp[cha][1],
            (2, 1): bp[can][0],
            (2, 7): bp[can][1],
            (3, 0): bp[sol][0],
            (3, 2): bp[sol][1],
            (3, 4): bp[sol][2],
            (3, 6): bp[sol][3],
            (3, 8): bp[sol][4],
            # -----------------------------------------------------------------
            (9, 0): rp[cha][0],
            (9, 1): rp[hor][0],
            (9, 2): rp[ele][0],
            (9, 3): rp[adv][0],
            (9, 4): rp[gen][0],
            (9, 5): rp[adv][1],
            (9, 6): rp[ele][1],
            (9, 7): rp[hor][1],
            (9, 8): rp[cha][1],
            (7, 1): rp[can][0],
            (7, 7): rp[can][1],
            (6, 0): rp[sol][0],
            (6, 2): rp[sol][1],
            (6, 4): rp[sol][2],
            (6, 6): rp[sol][3],
            (6, 8): rp[sol][4],
        }

        for pos, piece in expected.items():
            self.assertEqual(piece, board.get_piece(pos))

    def test_repr(self):
        players = (xg.Player('red'), xg.Player('black'))
        board = xg.Board(players)
        print()
        print(board)

    def test_castle_creation(self):
        players = (xg.Player(xg.Player.get_RED()),
                   xg.Player(xg.Player.get_BLACK()))
        red, black = players
        board = xg.Board(players)
        expected = {
            xg.Player.get_BLACK():
            ((0, 3),
             (0, 4),
             (0, 5),
             (1, 3),
             (1, 4),
             (1, 5),
             (2, 3),
             (2, 4),
             (2, 5),),
            xg.Player.get_RED():
            ((7, 3),
             (7, 4),
             (7, 5),
             (8, 3),
             (8, 4),
             (8, 5),
             (9, 3),
             (9, 4),
             (9, 5),),
        }
        for color, castle in expected.items():
            self.assertEqual(castle, board.get_castle(color))

    def test_is_in_castle(self):
        players = (xg.Player(xg.Player.get_RED()),
                   xg.Player(xg.Player.get_BLACK()))
        board = xg.Board(players)
        for player in players:
            piece_dct = xg.Player.get_pieces(player)
            for key, piece_lst in piece_dct.items():
                for piece in piece_lst:
                    actual = board.is_in_castle(piece.get_pos(), player)
                    expected = (True if (isinstance(piece, xg.General)
                                         or isinstance(piece, xg.Advisor))
                                else False)
                    # print(f'{piece}: {expected}')
                    self.assertEqual(expected, actual)

    def test_is_across_river(self):
        players = (xg.Player(xg.Player.get_RED()),
                   xg.Player(xg.Player.get_BLACK()))
        red, black = players
        # elt 0: black, (note negation will be Red)
        board = xg.Board(players)
        for i, row in enumerate(board._board):
            for j, piece in enumerate(row):
                pos = (i, j)
                expected_black = True if pos[0] >= 5 else False
                expected_red = not expected_black
                actual_black = xg.Board.is_across_river(pos, black)
                actual_red = xg.Board.is_across_river(pos, red)
                self.assertEqual(expected_black, actual_black)
                self.assertEqual(expected_red, actual_red)

    def test_find_ortho_path(self):
        players = (xg.Player(xg.Player.get_RED()),
                   xg.Player(xg.Player.get_BLACK()))
        red, black = players
        board = xg.Board(players)
        test_cases = {
            ((3, 2), (-1, 0)): [(2, 2), (1, 2), (0, 2)],
            ((3, 2),  (1, 0)): [(4, 2), (5, 2), (6, 2)],
            ((3, 2),  (0, 1)): [(3, 3), (3, 4)],
            ((3, 2), (0, -1)): [(3, 1), (3, 0)],
            # -----------------------------------------------------------------
            ((8, 0), (-1, 0)): [(7, 0), (6, 0)],
            ((8, 0),  (1, 0)): [(9, 0)],
            ((8, 0),  (0, 1)): [(8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6),
                                (8, 7), (8, 8)],
            ((8, 0), (0, -1)): [],
            # -----------------------------------------------------------------
            ((9, 4), (-1, 0)): [(8, 4), (7, 4), (6, 4)],
            ((9, 4),  (1, 0)): [],
            ((9, 4),  (0, 1)): [(9, 5)],
            ((9, 4), (0, -1)): [(9, 3)],
            # -----------------------------------------------------------------
            # ((3, 2), (-1, 0)): [],  # UP
            # ((3, 2),  (1, 0)): [],  # DOWN
            # ((3, 2),  (0, 1)): [],  # RIGHT
            # ((3, 2), (0, -1)): [],  # LEFT
            # -----------------------------------------------------------------
        }

        for params, expected in test_cases.items():
            actual = board.find_ortho_path(*params)
            self.assertEqual(expected, actual)

    def test_make_move_undo_black_chariot(self):
        players = (xg.Player(xg.Player.get_RED()),
                   xg.Player(xg.Player.get_BLACK()))
        red, black = players
        board = xg.Board(players)
        chb0, chb1 = black.get_pieces()['chariot']
        sr0, sr1, sr2, sr3, sr4 = red.get_pieces()['soldier']

        taken = board.make_move((0, 0), (1, 0), black)
        self.assertEqual(None, taken)
        self.assertEqual(None, board.get_piece((0, 0)))
        self.assertEqual((1, 0), chb0.get_pos())

        old_pos = chb0.get_pos()
        new_pos = (1, 3)
        taken = board.make_move(old_pos, new_pos, black)
        self.assertEqual(None, taken)
        self.assertEqual(None, board.get_piece(old_pos))
        self.assertEqual(new_pos, chb0.get_pos())

        old_pos = chb0.get_pos()
        new_pos = (6, 3)
        taken = board.make_move(old_pos, new_pos, black)
        self.assertEqual(None, taken)
        self.assertEqual(None, board.get_piece(old_pos))
        self.assertEqual(new_pos, chb0.get_pos())

        old_pos = chb0.get_pos()
        new_pos = (6, 2)
        taken = board.make_move(old_pos, new_pos, black)
        self.assertEqual(sr1, taken)
        self.assertEqual(None, board.get_piece(old_pos))
        self.assertEqual(new_pos, chb0.get_pos())

        board.undo_move(taken)
        self.assertEqual(taken, board.get_piece(new_pos))
        self.assertEqual(new_pos, taken.get_pos())
        self.assertEqual(chb0, board.get_piece(old_pos))
        self.assertEqual(old_pos, chb0.get_pos())


class SoldierTest(unittest.TestCase):
    def test_get_moves_initial(self):
        players = (xg.Player(xg.Player.get_RED()),
                   xg.Player(xg.Player.get_BLACK()))
        red, black = players
        b0, b1, b2, b3, b4 = black.get_pieces()['soldier']
        r0, r1, r2, r3, r4 = red.get_pieces()['soldier']
        board = xg.Board(players)
        test_cases = (
            (b0, [(4, 0)]),
            (b1, [(4, 2)]),
            (b2, [(4, 4)]),
            (b3, [(4, 6)]),
            (b4, [(4, 8)]),
            (r0, [(5, 0)]),
            (r1, [(5, 2)]),
            (r2, [(5, 4)]),
            (r3, [(5, 6)]),
            (r4, [(5, 8)]),
        )
        for case in test_cases:
            soldier, expected = case
            actual = soldier.get_moves(board)
            self.assertEqual(expected, actual)

    def test_get_moves_manually_moved(self):
        players = (xg.Player(xg.Player.get_RED()),
                   xg.Player(xg.Player.get_BLACK()))
        red, black = players
        b0, b1, b2, b3, b4 = black.get_pieces()['soldier']
        r0, r1, r2, r3, r4 = red.get_pieces()['soldier']
        board = xg.Board(players)


class PlayerTest(unittest.TestCase):
    def test_player_identity(self):
        test_cases = {
            "red": xg.Player(xg.Player.get_RED()),
            "black": xg.Player(xg.Player.get_BLACK()),
        }
        for key, val in test_cases.items():
            expected = key
            actual = val.get_color()
            self.assertEqual(expected, actual)

    def test_piece_counts(self):
        players = {
            "red": xg.Player(xg.Player.get_RED()),
            "black": xg.Player(xg.Player.get_BLACK()),
        }
        piece_counts = {
            'general': 1,
            'advisor': 2,
            'elephant': 2,
            'horse': 2,
            'chariot': 2,
            'cannon': 2,
            'soldier': 5
        }
        for color, player in players.items():
            pieces = player.get_pieces()
            for key, count in piece_counts.items():
                expected = count
                actual = len(pieces[key])
                self.assertEqual(expected, actual)


class StackTest(unittest.TestCase):
    def test_init(self):
        stack = xg.Stack()
        self.assertEqual(0, stack.get_size())
        self.assertEqual(None, stack.peek())
        self.assertTrue(stack.is_empty())
        self.assertEqual(None, stack.pop())

    def test_peek_push_from_empty(self):
        test_cases = {
            (2,): 2,
            (2, 5): 5,
            (2, 5, 3): 3,
            (2, 2, 2, 2): 2,
        }
        for params, top in test_cases.items():
            stack = xg.Stack()
            for param in params:
                stack.push(param)
            self.assertEqual(top, stack.peek())

    def test_push_and_pop(self):
        test_cases = (
            (2, 7, 12, 78, 23),
            tuple(),
            (0, 0, 0, 0),
            (65,),
        )
        for params in test_cases:
            stack = xg.Stack()
            for param in params:
                stack.push(param)
            self.assertEqual(len(params), stack.get_size())
            for i, param in enumerate(params[::-1]):
                top = stack.pop()
                self.assertEqual(param, top)
            self.assertEqual(0, stack.get_size())
