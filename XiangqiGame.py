# Author: Jeremy Tsang
# Date: 03/01/2020
# Description: TODO


class XiangqiGame:
    # Class level constants
    pass


class Board:
    _ROW_COUNT = 10
    _COL_COUNT = 9

    def __init__(self):
        """Create a board with all pieces at starting positions."""
        self._board = [[None for j in range(Board._COL_COUNT)]
                       for i in range(Board._ROW_COUNT)]

    @staticmethod
    def get_ROW_COUNT():
        return Board._ROW_COUNT

    @staticmethod
    def get_COL_COUNT():
        return Board._COL_COUNT

    def __repr__(self):
        """Debugging method. Print a text visualization of the board. Assumes
        each piece has __repr__ implemented such that its string
        representation is 5 characters or less.
        """
        dashes = "-----"
        divider = "|" + dashes + "".join([f"+{dashes}" for col in range(Board._COL_COUNT)]) + "|"
        row_template = "|" + "|".join(["{{: ^{}}}".format(len(dashes))
                             for i in range(Board._COL_COUNT + 1)]) + "|"
        header_row = row_template.format(*([""] + [i for i in range(Board._COL_COUNT)]))
        res = divider + "\n" + header_row
        for i, row in enumerate(self._board):
            res += ("\n" + divider + "\n"
                    + row_template.format(*([i] + ["" if elt is None
                                                   else elt for elt in row])))
        res += "\n" + divider
        return res


class Piece:
    def __init__(self, pos, player):
        self._name = ""
        self._pos = pos
        self._player = player

    def __repr__(self):
        return self._name


class AlgNot:
    """Class to handle the board's Algebraic notation positional reference."""
    _ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
    _ALPHABET_DCT = {letter: i for i, letter in
                     enumerate(_ALPHABET[:Board.get_ROW_COUNT()])}

    @staticmethod
    def get_ALPHABET():
        """Getter. Returns a string of the alphabet."""
        return AlgNot._ALPHABET

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
          | 1         | row index 9 |
          | 10        | row index 0 |
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
                <= 1 + len(str(Board._ROW_COUNT))):  # Max row num digits
            raise AlgStrLengthError

        alg_letter = alg_str[0]  # Grab the column letter.

        # Validate the algebraic string's column letter.
        if alg_letter not in AlgNot._ALPHABET_DCT:
            raise AlgLetterError

        # Try to convert all characters after the column letter into
        # an integer.
        try:
            alg_num = int(alg_str[1:])
        except ValueError:
            raise AlgNumFormatError

        # Validate the row number to make sure falls within permissible range.
        if not (1 <= alg_num <= Board._ROW_COUNT):
            raise AlgNumOutOfBoundsError

        # Return the row and column indices.
        return (Board._ROW_COUNT - alg_num, AlgNot._ALPHABET_DCT[alg_letter])


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
        max_row_digits = len(str(Board._ROW_COUNT))
        super().__init__('Algebraic string must be between 2 to '
                         + f'{1 + max_row_digits} '
                         + 'characters long (inclusive).')


class AlgLetterError(AlgStrFormattingError):
    """Exception class for when Algebraic notation string's column letter is
    invalid."""
    def __init__(self):
        letters = AlgNot.get_ALPHABET()[:Board.get_COL_COUNT()]
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
                         + f'{Board.get_ROW_COUNT()} '
                         + 'inclusive.')
