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
    def __init__(self, player, id_num, abbrev="", pos=None):
        self._id_num = id_num
        self._player = player
        self._name = f"{abbrev}-{self._player.get_color()[0].upper()}-{id_num}"
        self._pos = pos

    def get_pos(self):
        return self._pos

    def set_pos(self, row, col):
        self._pos = (row, col)

    def __repr__(self):
        return self._name


class General(Piece):
    _ABBREV = 'g'
    _INIT_COL = 4

    def __init__(self, player, id_num):
        super().__init__(player, id_num, abbrev=self._ABBREV,
                         pos=(player.get_HOME_ROW()[player.get_color()],
                              self._INIT_COL))

    def __repr__(self):
        return super().__repr__()


class Advisor(Piece):
    _ABBREV = 'a'
    _INIT_COLS = (3, 5)  # Index with _id_num.

    def __init__(self, player, id_num):
        super().__init__(player, id_num, abbrev=self._ABBREV,
                         pos=(player.get_HOME_ROW()[player.get_color()],
                              self._INIT_COLS[id_num]))

    def __repr__(self):
        return super().__repr__()


class Elephant(Piece):
    _ABBREV = 'e'
    _INIT_COLS = (2, 6)  # Index with _id_num.

    def __init__(self, player, id_num):
        super().__init__(player, id_num, abbrev=self._ABBREV,
                         pos=(player.get_HOME_ROW()[player.get_color()],
                              self._INIT_COLS[id_num]))

    def __repr__(self):
        return super().__repr__()


class Horse(Piece):
    _ABBREV = 'h'
    _INIT_COLS = (1, 7)  # Index with _id_num.

    def __init__(self, player, id_num):
        super().__init__(player, id_num, abbrev=self._ABBREV,
                         pos=(player.get_HOME_ROW()[player.get_color()],
                              self._INIT_COLS[id_num]))

    def __repr__(self):
        return super().__repr__()


class Chariot(Piece):
    _ABBREV = 'ch'
    _INIT_COLS = (0, 8)  # Index with _id_num.

    def __init__(self, player, id_num):
        super().__init__(player, id_num, abbrev=self._ABBREV,
                         pos=(player.get_HOME_ROW()[player.get_color()],
                              self._INIT_COLS[id_num]))

    def __repr__(self):
        return super().__repr__()


class Cannon(Piece):
    _ABBREV = 'c'
    _INIT_ROWS = {"black": 2, "red": 7}  # TODO: remove hard coded keys?
    _INIT_COLS = (1, 7)  # Index with _id_num.

    def __init__(self, player, id_num):
        super().__init__(player, id_num, abbrev=self._ABBREV,
                         pos=(self._INIT_ROWS[player.get_color()],
                              self._INIT_COLS[id_num]))

    def __repr__(self):
        return super().__repr__()


class Soldier(Piece):
    _ABBREV = 's'
    _INIT_ROWS = {"black": 3, "red": 6}  # TODO: remove hard coded keys?
    _INIT_COLS = (0, 2, 4, 6, 8)  # Index with _id_num.

    def __init__(self, player, id_num):
        super().__init__(player, id_num, abbrev=self._ABBREV,
                         pos=(self._INIT_ROWS[player.get_color()],
                              self._INIT_COLS[id_num]))

    def __repr__(self):
        return super().__repr__()


class Player:
    _RED = 'red'
    _BLACK = 'black'
    _GENERAL = 'general'
    _ADVISOR = 'advisor'
    _ELEPHANT = 'elephant'
    _HORSE = 'horse'
    _CHARIOT = 'chariot'
    _CANNON = 'cannon'
    _SOLDIER = 'soldier'
    _PIECE_DCTS = [
        {'key': _GENERAL, 'class': General, 'count': 1},
        {'key': _ADVISOR, 'class': Advisor, 'count': 2},
        {'key': _ELEPHANT, 'class': Elephant, 'count': 2},
        {'key': _HORSE, 'class': Horse, 'count': 2},
        {'key': _CHARIOT, 'class': Chariot, 'count': 2},
        {'key': _CANNON, 'class': Cannon, 'count': 2},
        {'key': _SOLDIER, 'class': Soldier, 'count': 5},
    ]
    _HOME_ROW = {_BLACK: 0, _RED: 9}

    def __init__(self, color):
        """Create a player based on one of two colors 'red' or 'black'. Create
        all pieces belonging to the player for a new game.

        Parameters
        ----------
        color: str
            color may take the value of either PLAYER._RED or PLAYER._BLACK

        """
        self._color = color

        # CREATE ALL THE PLAYER'S PIECES
        self._pieces = {dct['key']:
                        [dct['class'](self, i) for i in range(dct['count'])]
                        for dct in Player._PIECE_DCTS}

    def get_color(self):
        """Getter. Return the color of the player."""
        return self._color

    def get_pieces(self):
        """Getter. Get the piece dictionary for the player. Dictionary keys are
        given by the constants:
            _GENERAL
            _ADVISOR
            _ELEPHANT
            _HORSE
            _CHARIOT
            _CANNON
            _SOLDIER
        Each value is a list of the Player's remaining pieces of each key's
        specified type.
        """
        return self._pieces

    @staticmethod
    def get_RED():
        """Getter. Get the constant for red color string."""
        return Player._RED

    @staticmethod
    def get_BLACK():
        """Getter. Get the constant for black color string."""
        return Player._BLACK

    @staticmethod
    def get_GENERAL():
        """Getter. Get dictionary key for General."""
        return Player._GENERAL

    @staticmethod
    def get_ADVISOR():
        """Getter. Get dictionary key for Advisor."""
        return Player._ADVISOR

    @staticmethod
    def get_ELEPHANT():
        """Getter. Get dictionary key for Elephant."""
        return Player._ELEPHANT

    @staticmethod
    def get_HORSE():
        """Getter. Get dictionary key for Horse."""
        return Player._HORSE

    @staticmethod
    def get_CHARIOT():
        """Getter. Get dictionary key for Chariot."""
        return Player._CHARIOT

    @staticmethod
    def get_CANNON():
        """Getter. Get dictionary key for Cannon."""
        return Player._CANNON

    @staticmethod
    def get_SOLDIER():
        """Getter. Get dictionary key for Soldier."""
        return Player._SOLDIER

    @staticmethod
    def get_HOME_ROW():
        """Getter. Get _HOME_ROW dictionary."""
        return Player._HOME_ROW

    def __repr__(self):
        """Return the color string of the player."""
        return self._color


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
