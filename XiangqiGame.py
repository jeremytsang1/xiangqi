# Author: Jeremy Tsang
# Date: 03/01/2020
# Description: TODO


class XiangqiGame:
    # Class level constants
    _ROW_COUNT = 10
    _COL_COUNT = 9
    _ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
    _ALPHABET_DCT = {letter: i for i, letter in
                     enumerate(_ALPHABET[:_ROW_COUNT])}

    @staticmethod
    def alg_to_row_col(alg_str):
        """Converts an Algebraic notation for a board position to a standard
        row and column indices tuple.

        Row and column indices correspond as follows:
          |-----------+-------------|
          | algebraic | row/col     |
          |-----------+-------------|
          | a         | col index 0 |
          | i         | col index 8 |
          | 1         | row index 0 |
          | 10        | row index 9 |
          |-----------+-------------|

        Parameters
        ----------
        alg_str: str

            Location on board in valid "algebraic notation" with
            columns labeled a-i and rows labeled 1-10. Row 1 being red
            side and row 10 being black side.

        Returns
        -------
        tuple of int
            Size 2 tuple of integers indicating row and column indices.

        """
        # Validate algebraic string's length.
        if not (2  # Min 2 chars (1 for col 1 for row).
                <= len(alg_str)
                <= 1 + len(str(XiangqiGame._ROW_COUNT))):  # Max row num digits
            raise AlgStrLengthError

        alg_letter = alg_str[0]  # Grab the column letter.

        # Validate the algebraic string's column letter.
        if alg_letter not in XiangqiGame._ALPHABET_DCT:
            raise AlgLetterError

        # Try to convert all characters after the column letter into
        # an integer.
        try:
            alg_num = int(alg_str[1:])
        except ValueError:
            raise AlgNumFormatError

        # Validate the row number to make sure falls within permissible range.
        if not (1 <= alg_num <= XiangqiGame._ROW_COUNT):
            raise AlgNumOutOfBoundsError

        # Return the row and column indices.
        return (alg_num - 1, XiangqiGame._ALPHABET_DCT[alg_letter])

    @staticmethod
    def get_ALPHABET():
        return XiangqiGame._ALPHABET

    @staticmethod
    def get_ROW_COUNT():
        return XiangqiGame._ROW_COUNT

    @staticmethod
    def get_COL_COUNT():
        return XiangqiGame._COL_COUNT

    @staticmethod
    def get_ALPHABET_DCT():
        return XiangqiGame._ALPHABET_DCT


class Error(Exception):
    """Base class for all exceptions."""
    def __init__(self, message):
        Exception.__init__(self, message)


class AlgStrFormattingError(Error):
    """Base exception class for all expcetions relating to the Algebraic
    notation errors."""
    pass


class AlgStrLengthError(AlgStrFormattingError):
    """Exception class for when Algebraic notation string has invalid
    length."""
    def __init__(self):
        max_row_digits = len(str(XiangqiGame._ROW_COUNT))
        super().__init__('Algebraic string must be between 2 to '
                         + f'{1 + max_row_digits} '
                         + 'characters long (inclusive).')


class AlgLetterError(AlgStrFormattingError):
    """Exception class for when Algebraic notation string's column letter is
    invalid."""
    def __init__(self):
        letters = XiangqiGame.get_ALPHABET()[:XiangqiGame.get_COL_COUNT()]
        super().__init__(f'Algebraic column letter must be in "{letters}".')


class AlgNumFormatError(AlgStrFormattingError):
    """Exception class for when Algebraic notation string's row number is not a
    proper integer."""
    def __init__(self):
        super().__init__('Algebraic row number must be a valid integer.')


class AlgNumOutOfBoundsError(AlgStrFormattingError):
    """Exception class for when Algebraic notation string's row number is not
    within bounds."""
    def __init__(self):
        super().__init__('Algebraic row number must fall between 1 and '
                         + f'{XiangqiGame.get_ROW_COUNT()} '
                         + 'inclusive.')
