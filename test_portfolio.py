import unittest
import XiangqiGame as xg


class XiangQiGameTest(unittest.TestCase):
    def test_alg_to_row_col_within_range(self):
        test_cases = {
            "a1": (0, 0),
            "b1": (0, 1),
            "c1": (0, 2),
            "d1": (0, 3),
            "e1": (0, 4),
            "f1": (0, 5),
            "g1": (0, 6),
            "h1": (0, 7),
            "i1": (0, 8),
            # -----------------------------------------------------------------
            "a2": (1, 0),
            "b2": (1, 1),
            "c2": (1, 2),
            "d2": (1, 3),
            "e2": (1, 4),
            "f2": (1, 5),
            "g2": (1, 6),
            "h2": (1, 7),
            "i2": (1, 8),
            # -----------------------------------------------------------------
            "a3": (2, 0),
            "b3": (2, 1),
            "c3": (2, 2),
            "d3": (2, 3),
            "e3": (2, 4),
            "f3": (2, 5),
            "g3": (2, 6),
            "h3": (2, 7),
            "i3": (2, 8),
            # -----------------------------------------------------------------
            "a4": (3, 0),
            "b4": (3, 1),
            "c4": (3, 2),
            "d4": (3, 3),
            "e4": (3, 4),
            "f4": (3, 5),
            "g4": (3, 6),
            "h4": (3, 7),
            "i4": (3, 8),
            # -----------------------------------------------------------------
            "a5": (4, 0),
            "b5": (4, 1),
            "c5": (4, 2),
            "d5": (4, 3),
            "e5": (4, 4),
            "f5": (4, 5),
            "g5": (4, 6),
            "h5": (4, 7),
            "i5": (4, 8),
            # -----------------------------------------------------------------
            "a6": (5, 0),
            "b6": (5, 1),
            "c6": (5, 2),
            "d6": (5, 3),
            "e6": (5, 4),
            "f6": (5, 5),
            "g6": (5, 6),
            "h6": (5, 7),
            "i6": (5, 8),
            # -----------------------------------------------------------------
            "a7": (6, 0),
            "b7": (6, 1),
            "c7": (6, 2),
            "d7": (6, 3),
            "e7": (6, 4),
            "f7": (6, 5),
            "g7": (6, 6),
            "h7": (6, 7),
            "i7": (6, 8),
            # -----------------------------------------------------------------
            "a8": (7, 0),
            "b8": (7, 1),
            "c8": (7, 2),
            "d8": (7, 3),
            "e8": (7, 4),
            "f8": (7, 5),
            "g8": (7, 6),
            "h8": (7, 7),
            "i8": (7, 8),
            # -----------------------------------------------------------------
            "a9": (8, 0),
            "b9": (8, 1),
            "c9": (8, 2),
            "d9": (8, 3),
            "e9": (8, 4),
            "f9": (8, 5),
            "g9": (8, 6),
            "h9": (8, 7),
            "i9": (8, 8),
            # -----------------------------------------------------------------
            "a10": (9, 0),
            "b10": (9, 1),
            "c10": (9, 2),
            "d10": (9, 3),
            "e10": (9, 4),
            "f10": (9, 5),
            "g10": (9, 6),
            "h10": (9, 7),
            "i10": (9, 8),
        }
        for param, expected in test_cases.items():
            actual = xg.AlgebraicNotation.alg_to_row_col(param)
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
                xg.AlgebraicNotation.alg_to_row_col(case)

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
                xg.AlgebraicNotation.alg_to_row_col(case)

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
                xg.AlgebraicNotation.alg_to_row_col(case)

    def test_alg_to_row_col_number_OOB(self):
        test_cases = (
            "a-2",
            "b21",
            "i0",
            "h99",
        )

        for case in test_cases:
            with self.assertRaises(xg.AlgNumOutOfBoundsError):
                xg.AlgebraicNotation.alg_to_row_col(case)
