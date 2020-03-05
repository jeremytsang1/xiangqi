import unittest
import XiangqiGame as xg


class XiangQiGameTest(unittest.TestCase):
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
    def test_repr(self):
        board = xg.Board()
        print(board)
