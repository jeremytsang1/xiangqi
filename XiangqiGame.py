# Author: Jeremy Tsang
# Date: 03/01/2020
# Description: Defines classes to implement a game of Xiangqi
#              ("Chinese Chess"). The game will follow the rules for
#              the 7 types of pieces: General, Advisor, Elephant,
#              Horse, Chariot, Cannon, and Soldier. In particular the
#              game begins with player "red" and uses algebraic
#              notation to specify locations on the board (a1 being
#              the lower left location and i10 being the upper
#              right). The game ends when either player has been mated
#              or a stalemate has been forced. In this implementation
#              perpetual check or chasing has not been enforced.


class XiangqiGame:
    """Class to start and control the Xiangqi by the user."""
    # Class level constants
    _UNFINISHED = 'UNFINISHED'
    _RED_WON = 'RED_WON'
    _BLACK_WON = 'BLACK_WON'

    def __init__(self):
        self._players = {color: Player(color) for color in Player.get_COLORS()}
        self.set_opponents()  # Make players track each other.
        self._board = Board(self._players.values())
        self._game_state = XiangqiGame._UNFINISHED
        self._current_player = self._players[Player.get_RED()]

    def get_game_state(self):
        """Getter. Return the game state.

        Returns a string with one of three values depending current
        state of board:
        1) 'UNFINISHED'
        2) 'RED_WON'
        3) 'BLACK_WON'
        """
        return self._game_state

    def is_in_check(self, color):
        """Checks if specified player is in check.

        Parameters
        ----------
        color: str
            Color of player inquire about.

        Returns
        -------
        bool
            True if the player is in check. Otherwise False.
        """
        return self._players[color].is_in_check()

    def make_move(self, alg_start, alg_end):
        # Prevent moves if game is already over.
        if self._game_state != XiangqiGame._UNFINISHED:
            return False

        # Validate algebraic notation.
        try:
            pos_start = AlgNot.alg_to_row_col(alg_start)
            pos_end = AlgNot.alg_to_row_col(alg_end)
        except AlgStrFormattingError:
            return False

        # Prevent illegal moves.
        try:
            self._board.make_move(pos_start, pos_end, self._current_player)
        except IllegalMoveError:
            return False

        # TODO: self.update_game_state()

        return True

    def update_game_state(self):
        pass

    def get_players(self):
        """Getter. Return dictionary of the two players.

        Dictionary has string keys Player.get_RED() and
        Player.get_BlACK() with respective players as values.
        """
        return self._players

    def get_board(self):
        """Getter. Return the object of type Board."""
        return self._board

    def set_opponents(self):
        """Helper method to call during init. Allows Players to keep track of
        the other Player. This is not done in Player.__init__() due to
        possibility the opponent has not been yet created when the
        tracking player is being created.
        """
        player_list = [player for player in self._players.values()]

        for i, player in enumerate(player_list):
            player.set_opponent(player_list[i - 1])


class Board:
    """Class defining the physical game board. Has 5 rows on each side of
    the river (10 rows total) and 9 columns total. Algebraic notation
    is not used in this class (only in XiangqiGame). This class uses a
    row/column index notation where (0, 0) represents the upper left
    corner and and (10, 9) the lower right corner.
    """
    _ROW_COUNT = 10
    _COL_COUNT = 9

    def __init__(self, players):
        """Create a board represenation (nested list) with all pieces at their
        starting positions. Players should be the size 2 list of
        players, though they need not be in any particular order.
        """
        self._board = [[None for j in range(Board._COL_COUNT)]
                       for i in range(Board._ROW_COUNT)]
        for piece in Player.get_all_pieces(*players):
            row, col = piece.get_pos()
            self._board[row][col] = piece
        self._castles = {player.get_color(): self.make_castle(player)
                         for player in players}

    def get_piece(self, pos):
        """Get the piece at the given position.

        Assumes whenever a piece is moved, the element where it used to
        be is now occupied by None.

        Parameters
        ----------
        pos: tuple of int
            Size 2 tuple with pos[0] being row and pos[1] being column.

        Returns
        -------
        Piece
            The piece at the specified position. If position is empty,
            returns None.
        """
        return self._board[pos[0]][pos[1]]

    def make_move(self, src_pos, dst_pos, moving_player):
        src_piece = self.get_piece(src_pos)
        dst_piece = self.get_piece(dst_pos)

        if src_piece is None:
            raise NoPieceAtStartPosError(src_pos)
        if src_piece.get_player() != moving_player:
            raise WrongPieceOwner(moving_player, src_pos)

        # TODO: get piece move set

        # TODO: "make" the move

        # TODO: check if result in check

        # TODO: "make" the move for real

    def make_castle(self, player):
        """Helper method to create record of each player's castle positions.

        Should only be run upon board creation.

        Parameters
        ----------
        player: str
            Color string for given player. Can either be
            Player.get_RED() or Player.get_BLACK().

        Returns
        -------
        Tuple of tuple of int.
            Tuple of size two tuples of ints. Each inner tupple
            represents a row and col position.
        """
        # Center row of the castle is one row twoards river from
        # player's home row.
        center_row = player.get_home_row() + player.get_fwd_dir()

        # Center column of the castle is the same column as the
        # player's general.
        general = player.get_pieces()[Player.get_GENERAL()][0]
        center_col = general.get_pos()[1]

        # Add the displacements (-1, 0, 1) go the castle's center
        # location to get all 9 positions in the castle.
        displacements = [i for i in range(-1, 2)]
        castle_positions = tuple([(center_row + i, center_col + j)
                                  for i in displacements
                                  for j in displacements])
        return castle_positions

    def get_castle(self, color):
        return self._castles[color]


    @staticmethod
    def get_ROW_COUNT():
        """Getter. Gets the total number of rows on the board."""
        return Board._ROW_COUNT

    @staticmethod
    def get_COL_COUNT():
        """Getter. Gets the total number of columns on the board."""
        return Board._COL_COUNT

    def __repr__(self):
        """Debugging method. Print a text visualization of the board. Assumes
        each piece has __repr__ implemented such that its string
        representation is 5 characters or less.
        """
        dashes = "--------"  # TODO: remove hard coded length?
        divider = "|" + dashes + "".join([f"+{dashes}" for col in range(Board._COL_COUNT)]) + "|"
        row_template = "|" + "|".join(["{{: ^{}}}".format(len(dashes))
                                       for i in range(Board._COL_COUNT + 1)]) + "|"
        header_row = row_template.format(*([""] + [i for i in range(Board._COL_COUNT)]))
        res = divider + "\n" + header_row
        for i, row in enumerate(self._board):
            res += ("\n" + divider + "\n"
                    + row_template.format(*([i] + ["" if elt is None
                                                   else str(elt) for elt in row])))
        res += "\n" + divider
        return res


class Piece:
    """Class to represent an abstract Piece. Provides a base class to
    specific pieces. Should not be instantiated!"""

    def __init__(self, player, id_num, abbrev="", start_pos=None):
        """Creates a fully specified piece.

        Parameters
        ----------
        player: Player
            Player to whom the piece belongs to.
        id_num: int
            Unique identifier (among pieces of the same Player and
            type) for the piece. Must be non-negative and less than
            the total number of pieces of the same type that belong to
            a given player.
        abbrev: str
            Short string description of the piece. For printing only.
        pos: Tuple of int
            Size two tuple where pos[0] represents the row and pos[1]
            the column.
        """
        self._id_num = id_num
        self._player = player
        self._positions = Stack()
        self._positions.push(start_pos)

        # For printing use only. Names will have the form
        # <abbrev>-<player-first-letter>-<id_num>
        self._name = f"{abbrev}-{self._player.get_color()[0].upper()}-{id_num}"

    def get_player(self):
        """Getter. Return the Player who own's the piece."""
        return self._player

    def get_pos(self):
        """Getter. Get the position of the piece."""
        return self._positions.peek()

    def set_pos(self, pos):
        """Setter. Update the position of the piece."""
        self._positions.append(pos)

    def __repr__(self):
        """Use the name as representation."""
        return self._name

    def __str__(self):
        """Use the name as informal represenation."""
        return self._name


class General(Piece):
    """
    Class to represent the general piece. Can detect line of sight of enemy
    general.
    """
    _ABBREV = 'g'
    _INIT_COLS = (4,)

    def __init__(self, player, id_num):
        """Create an object of type General with location based on player."""
        super().__init__(player, id_num, abbrev=self._ABBREV,
                         start_pos=(player.get_HOME_ROWS()[player.get_color()],
                                    self._INIT_COLS[id_num]))

    def __repr__(self):
        """Inherit __repr__ of base class."""
        return super().__repr__()

    def __str__(self):
        """Inherit __str__ of base class."""
        return super().__str__()


class Advisor(Piece):
    _ABBREV = 'a'
    _INIT_COLS = (3, 5)  # Index with _id_num.

    def __init__(self, player, id_num):
        """Create an object of type Adivsor with location based on player and
        id_num."""
        super().__init__(player, id_num, abbrev=self._ABBREV,
                         start_pos=(player.get_HOME_ROWS()[player.get_color()],
                                    self._INIT_COLS[id_num]))

    def __repr__(self):
        """Inherit __repr__ of base class."""
        return super().__repr__()

    def __str__(self):
        """Inherit __str__ of base class."""
        return super().__str__()


class Elephant(Piece):
    _ABBREV = 'e'
    _INIT_COLS = (2, 6)  # Index with _id_num.

    def __init__(self, player, id_num):
        """Create an object of type Adivsor with location based on player and
        id_num."""
        super().__init__(player, id_num, abbrev=self._ABBREV,
                         start_pos=(player.get_HOME_ROWS()[player.get_color()],
                                    self._INIT_COLS[id_num]))

    def __repr__(self):
        """Inherit __repr__ of base class."""
        return super().__repr__()

    def __str__(self):
        """Inherit __str__ of base class."""
        return super().__str__()


class Horse(Piece):
    _ABBREV = 'h'
    _INIT_COLS = (1, 7)  # Index with _id_num.

    def __init__(self, player, id_num):
        """Create an object of type Adivsor with location based on player and
        id_num."""
        super().__init__(player, id_num, abbrev=self._ABBREV,
                         start_pos=(player.get_HOME_ROWS()[player.get_color()],
                                    self._INIT_COLS[id_num]))

    def __repr__(self):
        """Inherit __repr__ of base class."""
        return super().__repr__()

    def __str__(self):
        """Inherit __str__ of base class."""
        return super().__str__()


class Chariot(Piece):
    _ABBREV = 'ch'
    _INIT_COLS = (0, 8)  # Index with _id_num.

    def __init__(self, player, id_num):
        """Create an object of type Adivsor with location based on player and
        id_num."""
        super().__init__(player, id_num, abbrev=self._ABBREV,
                         start_pos=(player.get_HOME_ROWS()[player.get_color()],
                                    self._INIT_COLS[id_num]))

    def __repr__(self):
        """Inherit __repr__ of base class."""
        return super().__repr__()

    def __str__(self):
        """Inherit __str__ of base class."""
        return super().__str__()


class Cannon(Piece):
    _ABBREV = 'c'
    _INIT_ROWS = {"black": 2, "red": 7}  # TODO: remove hard coded keys?
    _INIT_COLS = (1, 7)  # Index with _id_num.

    def __init__(self, player, id_num):
        """Create an object of type Adivsor with location based on player and
        id_num."""
        super().__init__(player, id_num, abbrev=self._ABBREV,
                         start_pos=(self._INIT_ROWS[player.get_color()],
                                    self._INIT_COLS[id_num]))

    def __repr__(self):
        """Inherit __repr__ of base class."""
        return super().__repr__()

    def __str__(self):
        """Inherit __str__ of base class."""
        return super().__str__()


class Soldier(Piece):
    _ABBREV = 's'
    _INIT_ROWS = {"black": 3, "red": 6}  # TODO: remove hard coded keys?
    _INIT_COLS = (0, 2, 4, 6, 8)  # Index with _id_num.

    def __init__(self, player, id_num):
        """Create an object of type Adivsor with location based on player and
        id_num."""
        super().__init__(player, id_num, abbrev=self._ABBREV,
                         start_pos=(self._INIT_ROWS[player.get_color()],
                                    self._INIT_COLS[id_num]))

    def __repr__(self):
        """Inherit __repr__ of base class."""
        return super().__repr__()

    def __str__(self):
        """Inherit __str__ of base class."""
        return super().__str__()


class Player:
    """Class representing a player with their own set of pieces. Responsible
    for piece creation."""

    # CONSTANTS
    _RED = 'red'
    _BLACK = 'black'
    _COLORS = (_RED, _BLACK)

    # Piece specific dictionary keys
    _GENERAL = 'general'
    _ADVISOR = 'advisor'
    _ELEPHANT = 'elephant'
    _HORSE = 'horse'
    _CHARIOT = 'chariot'
    _CANNON = 'cannon'
    _SOLDIER = 'soldier'

    # Dictionary for helping creating pieces. For 'class' value iterate
    # across different derived classes __init__ methods to create the
    # specific pieces for the player.
    _PIECE_DCTS = [
        {'key': _GENERAL, 'class': General, 'count': 1},
        {'key': _ADVISOR, 'class': Advisor, 'count': 2},
        {'key': _ELEPHANT, 'class': Elephant, 'count': 2},
        {'key': _HORSE, 'class': Horse, 'count': 2},
        {'key': _CHARIOT, 'class': Chariot, 'count': 2},
        {'key': _CANNON, 'class': Cannon, 'count': 2},
        {'key': _SOLDIER, 'class': Soldier, 'count': 5},
    ]

    # Player specific locations.
    _HOME_ROWS = {_BLACK: 0, _RED: 9}
    _FWD_DIRS = {_BLACK: 1, _RED: -1}

    def __init__(self, color):
        """Create a player based on one of two colors 'red' or 'black'. Create
        all pieces belonging to the player for a new game.

        Parameters
        ----------
        color: str
            color may take the value of either PLAYER._RED or PLAYER._BLACK
        """
        self._color = color

        # CREATE ALL THE PLAYER'S PIECES.
        # Create as a dictionary of lists indexed by the above class
        # level constant keys.
        self._pieces = {dct['key']:
                        [dct['class'](self, i) for i in range(dct['count'])]
                        for dct in Player._PIECE_DCTS}
        self._opponent = None
        self._home_row = Player._HOME_ROWS[self._color]
        self._fwd_dir = Player._FWD_DIRS[self._color]

    def is_in_check(self):
        """Determine if the calling Player is in check.

        Returns
        -------
        bool
            True if calling Player is in check. Otherwise False.
        """
        pass

    def set_opponent(self, opponent):
        """Setter. `opponent` must be object of type Player."""
        self._opponent = opponent

    def get_opponent(self):
        """Getter. Return the calling player's opponent. Returns object of
        type Player"""
        return self._opponent

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

    def get_home_row(self):
        """Getter. Get the home row (initial row where general starts) of the
        player."""
        return self._home_row

    def get_fwd_dir(self):
        """Getter. Get the direction pieces move away from the player's home
        row."""
        return self._fwd_dir

    @staticmethod
    def get_all_pieces(*args):
        """Get pieces from specified players.

        Parameters
        ----------
        args: Player
            Players to get Pieces from.

        Returns
        -------
        list of Piece
            List of all the pieces of the specified players.

        """
        pieces = []  # List to add player pieces to.

        # For each player, add their remaining pieces to the list.
        for player in args:
            piece_dct = player.get_pieces()

            for class_key, piece_sublist in piece_dct.items():
                pieces += piece_sublist

        return pieces

    def __repr__(self):
        """Return the color string of the player."""
        return self._color

    def __str__(self):
        """Return the color string of the player."""
        return self._color

    @staticmethod
    def get_RED():
        """Getter. Get the constant for red color string."""
        return Player._RED

    @staticmethod
    def get_BLACK():
        """Getter. Get the constant for black color string."""
        return Player._BLACK

    @staticmethod
    def get_COLORS():
        """Getter. Return tuple of all color strings."""
        return Player._COLORS

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
    def get_HOME_ROWS():
        """Getter. Get _HOME_ROW dictionary."""
        return Player._HOME_ROWS


class Stack:
    """
    An implementation of the Stack ADT that uses Python's built-in lists.

    Taken from CS 162, "Exploration: Linked lists, stacks, queues".
    """
    def __init__(self):
        self._list = []

    def get_size(self):
        return len(self._list)

    def peek(self):
        if self.get_size() == 0:
            return None
        return self._list[-1]

    def is_empty(self):
        return len(self._list) == 0

    def push(self, data):
        self._list.append(data)

    def pop(self):
        if self.is_empty():
            return None

        val = self._list[-1]
        del self._list[-1]
        return val


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

        Raises
        ------
        AlgStrLengthError:
            When algebraic notation string is not length 2 or 3.
        AlgLetterError:
            When algebraic notation string has invalid character in its
            first position (it should be a letter from a-i).
        AlgNumFormatError:
            When the character(s) after the first do not represent a
            valid integer.
        AlgNumOutOfBoundsError:
            When the integer is not within the valid 1-10 range.

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


class IllegalMoveError(Error):
    """Base class for performing invalid moves."""
    pass


class NoPieceAtStartPosError(IllegalMoveError):
    """Exception class for when attempting to move a piece at a position
    where no piece currently resides."""
    def __init__(self, pos):
        self._pos
        super().__init__('Attempting to move non-existent piece at '
                         + f'{self._pos}')


class WrongPieceOwner(IllegalMoveError):
    """Exception class for when attempting to move a piece that does not
    belong go the player making the move."""
    def __init__(self, moving_player, pos):
        self._moving_player = moving_player
        self._pos = pos
        super().__init__('Attempting to move piece at '
                         + f'{self._pos} but does not belong to '
                         + f'{moving_player}.')


if __name__ == '__main__':
    game = XiangqiGame()
    players = game.get_players()
    red, black = players[Player.get_RED()], players[Player.get_BLACK()]
    rp = red.get_pieces()
    bp = black.get_pieces()
    board = game.get_board()
