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

        # TODO: alternate current player

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
    _AXES_COUNTS = (_ROW_COUNT, _COL_COUNT)
    _RIVER_DIST = 5
    # Axes constants.
    _ROW = 0
    _COL = 1

    # Directions
    _FWD = 1
    _REV = -1
    _DIRECTIONS_DIAG = ((_REV, _REV), (_REV, _FWD), (_FWD, _REV), (_FWD, _FWD))
    _DIRECTIONS_ORTHO = ((0, _REV), (0, _FWD), (_REV, 0), (_FWD, 0))
    _DIRECTIONS_HORSE = {(0, _REV): ((_FWD, _REV), (_REV, _REV)),
                         (0, _FWD): ((_FWD, _FWD), (_REV, _FWD)),
                         (_REV, 0): ((_REV, _FWD), (_REV, _REV)),
                         (_FWD, 0): ((_FWD, _FWD), (_FWD, _REV))}

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
        return self._board[pos[Board._ROW]][pos[Board._COL]]

    def place_piece(self, new_pos, piece):
        old_pos = piece.get_pos()
        self.set_board(new_pos, piece)
        self.set_board(old_pos, None)
        piece.push(new_pos)

    def set_board(self, pos, elt):
        self._board[pos[self._ROW]][pos[self._COL]] = elt

    def make_move(self, beg_pos, end_pos, moving_player):
        beg_piece = self.get_piece(beg_pos)
        end_piece = self.get_piece(end_pos)

        if beg_piece is None:
            raise NoPieceAtStartPosError(beg_pos)
        if beg_piece.get_player() != moving_player:
            raise WrongPieceOwner(moving_player, beg_pos)

        # Get piece move list.
        moves = beg_piece.get_moves(self)

        # Check if in move list.
        if end_pos not in moves:
            raise NotInMoveListError(beg_piece, moves, end_pos)

        # TODO: Check if allowed to take piece would lift mate (if currently in mate)

        # TODO: "make" the move
        self.place_piece(end_pos, beg_piece)
        return end_piece


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
        general = player.get_pieces()[Player.get_GENERAL()][Board._ROW]
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

    def is_in_castle(self, pos, player):
        return pos in self._castles[player.get_color()]

    def find_diag(self, beg_pos, dir_diag, dist=1):
        """Compute positions in a diagonal direction from the beginning position.

        Parameters
        ----------
        beg_pos: tuple of int
            Size 2 tuple representing position to check.
            beg_pos[0] must be in [0, 1, ..., Board._ROW_COUNT - 1]
            beg_pos[1] must be in [0, 1, ..., Board._COL_COUNT - 1].

        dir_diag: tuple of int
            Size 2 tuple that contains only 1 or -1.

        dist: int
            Number of diagonals away to inspect.

        Returns
        -------
        tuple of int
            Size 2 tuple representing position of diagnal. If diagonal
        would be off board, then returns None
        """
        end_pos = list(beg_pos)

        # Assumes dir_diag and end_pos have same dimensions

        # Compute the diagonal position in the specified direction.
        for i, dir_component in enumerate(dir_diag):
            end_pos[i] += dist * dir_component

        try:
            self.validate_bounds(end_pos)
        except OutOfBoundsError:
            return None

        return tuple(end_pos)

    def find_ortho_path(self, beg_pos, dir_ortho, dist_capped=None):
        """Finds an orthogonal path in the speicifed orthogonal direction from
        the position to first encountered piece or the edge of the board.

        Post Conditions
        ---------------
        If a piece is encountered, it will be located in the last
        element of the list.

        Parameters
        ----------
        beg_pos: tuple of int
            Size 2 tuple representing position to check.
            beg_pos[0] must be in [0, 1, ..., Board._ROW_COUNT - 1]
            beg_pos[1] must be in [0, 1, ..., Board._COL_COUNT - 1].

        dir_ortho: tuple of int
            Size 2 tuple who must contain exactly one 0 while the
            other element must be either -1 or 1.

        dist_capped: int
            Maxmimum number of positions to traverse in the path.

        Returns
        -------
        list of tuple
            List of positions from beginning position to next piece or edge.

        """
        if Board._FWD in dir_ortho:
            delta_axis = dir_ortho.index(Board._FWD)
        else:
            delta_axis = dir_ortho.index(Board._REV)

        direction = dir_ortho[delta_axis]  # Either _FWD or _REV.
        constant_axis = delta_axis - 1     # Axis being traveled along.

        # Edge locations along the delta axis.
        delta_axis_min = 0
        delta_axis_max = Board._AXES_COUNTS[delta_axis]

        # Create two element list. Can't explicitly initialize due to
        # end points depending on direction.
        end_pos = [0, 0]

        # Set the edge of Board to the first guess for the ending
        # position.
        end_pos[constant_axis] = beg_pos[constant_axis]
        end_pos[delta_axis] = (delta_axis_min if direction == Board._REV
                               else delta_axis_max - 1)

        # Bring guess for ending position closer to beginning position
        # if length is specified and shorter than the distance from
        # the beginning position to the edge of the board.
        if dist_capped is not None:
            dist_to_edge = abs(end_pos[delta_axis] - beg_pos[delta_axis])
            if dist_capped < dist_to_edge:
                end_pos[delta_axis] = (beg_pos[delta_axis]
                                       + (dist_capped * direction))

        current_pos = list(beg_pos)  # Starting position.
        path = list()  # List of positions to return.

        for delta_elt in range(beg_pos[delta_axis] + direction,  # Exclude beg.
                               end_pos[delta_axis] + direction,  # Include end.
                               direction):
            # Travel one position in specified direction.
            current_pos[delta_axis] = delta_elt
            # Add said position to the path. Make sure not to use
            # mutable type due or else the all path positions will
            # contain the same value.
            path.append(tuple(current_pos))
            # If find encounter a piece along the path, stop traversing.
            if self.get_piece(current_pos) is not None:
                return path
        return path

    def find_intervening_ortho(self, beg_pos, end_pos):
        """Check if there is at least one piece between two positions.

        Raises: TODO

        Parameters
        ----------
        beg_pos: tuple of int
            Size 2 tuple representing position to check.
            pos[0] must be in [0, 1, ..., Board._ROW_COUNT - 1]
            pos[1] must be in [0, 1, ..., Board._COL_COUNT - 1].

        end_pos: tuple of int
            Size 2 tuple representing position to check.
            pos[0] must be in [0, 1, ..., Board._ROW_COUNT - 1]
            pos[1] must be in [0, 1, ..., Board._COL_COUNT - 1].

        Returns
        -------
        Piece
            None if there are no pieces on a orthogonal axis between
            the two positions. Otherwise returns the first piece that
            is encountered from traversing from beginining position to
            end position.
        """
        for pos in (beg_pos, end_pos):
            Board.validate_bounds(pos)

        # Find which if the two positions are on the same row or same col.
        common_axis = Board.find_common_axis(beg_pos, end_pos)

        # No intervening Piece if two positions share neither a row or col.
        # TODO: maybe move this outside.
        if common_axis == -1:
            return None

        # The axis that the two positions do not share.
        delta_axis = common_axis - 1
        # Find the direction from the beginning element to the end element.
        direction = Board.get_dir_one_dim(beg_pos[delta_axis],
                                          end_pos[delta_axis])

        pos = list(beg_pos)  # Make copy of beginning position.

        # Traverse from beginning position to end position and if any
        # piece is found in between return it.
        for delta_elt in range(beg_pos[delta_axis] + direction,  # Exclude beg.
                               end_pos[delta_axis],              # Exclude end.
                               direction):  # Travel from beg to end.
            pos[delta_axis] = delta_elt
            intervening_piece = self.get_piece(pos)  # Check current position.
            if intervening_piece is not None:
                # Return intervening piece if there is indeed one.
                return intervening_piece

        # No intervening pieces found.
        return None

    @staticmethod
    def find_common_axis(beg_pos, end_pos):
        """Check if two positions share a row or column.

        Raises

        Parameters
        ----------
        beg_pos: tuple of int
            Size 2 tuple representing position to check.
            pos[0] must be in [0, 1, ..., Board._ROW_COUNT - 1]
            pos[1] must be in [0, 1, ..., Board._COL_COUNT - 1].

        end_pos: tuple of int
            Size 2 tuple representing position to check.
            pos[0] must be in [0, 1, ..., Board._ROW_COUNT - 1]
            pos[1] must be in [0, 1, ..., Board._COL_COUNT - 1].

        Returns
        -------
        int
            Board._ROW if both positions share the same row.
            Board._COL if both positions share the same col.
            -1 if the two positions do not have a common axis.
        """
        beg_row, beg_col = beg_pos
        end_row, end_col = end_pos

        if (beg_row, beg_col) == (end_row, end_col):
            raise SamePositionError((beg_row, beg_col))
        elif beg_row != end_row and beg_col != end_col:
            return -1
        elif beg_row == end_row:
            return Board._ROW  # Check along row.
        else:
            return Board._COL  # Check along col.

    @staticmethod
    def validate_bounds(pos):
        """Validate position to make sure lies on Board.

        Raises
        ------
        OutOfBoundsError if position lays outside of boards bounds.

        Parameters
        ----------
        pos: tuple of int
            Size 2 tuple representing position to check.

        Returns
        -------
        None
        """

        if pos[Board._ROW] not in range(Board._ROW_COUNT):
            raise OutOfBoundsError(pos, Board._ROW, Board._ROW_COUNT)
        if pos[Board._COL] not in range(Board._COL_COUNT):
            raise OutOfBoundsError(pos, Board._COL, Board._COL_COUNT)

    @staticmethod
    def get_dir_one_dim(beg, end):
        """Find the direction between two pieces.

        Raises
        ------
        SamePositionError if beg and end are equal.

        Parameters
        ----------
        beg: int
            Starting element.
        end: int
            Ending element.

        Returns
        -------
        int
            Direction is either 1 or -1. 1 if end is more than beg and
            -1 if less.
        """
        if beg == end:
            raise SamePositionError(f'ELEMENT {beg}')
        return 1 if beg < end else -1

    @staticmethod
    def is_across_river(pos, player):
        """Predicate. Checks if a position is across the river from Player's
        home row side of the board.

        Parameters
        ----------
        pos: tuple of int
            Size 2 tuple representing position to check.
            pos[0] must be in [0, 1, ..., Board._ROW_COUNT - 1]
            pos[1] must be in [0, 1, ..., Board._COL_COUNT - 1].

        Returns
        -------
        bool
            True if the position is across the river from the side of
            the Player's home row. False if on the same side.

        """
        row = pos[Board._ROW]
        home_row = player.get_home_row()
        return abs(row - home_row) >= Board._RIVER_DIST

    @staticmethod
    def get_ROW_COUNT():
        """Getter. Gets the total number of rows on the board."""
        return Board._ROW_COUNT

    @staticmethod
    def get_COL_COUNT():
        """Getter. Gets the total number of columns on the board."""
        return Board._COL_COUNT

    @staticmethod
    def get_ortho_dirs():
        return Board._DIRECTIONS_ORTHO

    @staticmethod
    def get_horse_dirs():
        return Board._DIRECTIONS_HORSE

    @staticmethod
    def get_ROW():
        return Board._ROW

    @staticmethod
    def get_COL():
        return Board._COL


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

    def __repr__(self):
        """Use the name as representation."""
        return self._name

    def __str__(self):
        """Use the name as informal represenation."""
        return self._name

    def get_player(self):
        """Getter. Return the Player who own's the piece."""
        return self._player

    def get_pos(self):
        """Getter. Get the position of the piece."""
        return self._positions.peek()

    def push(self, pos):
        """Setter. Update the position of the piece."""
        self._positions.push(pos)

    def pop(self):
        return self._positions.pop()

    def remove_friendly(self, path, board):
        """Given a path, removes any friendly piece at the end of the path.

        If no friendly piece found, path is not mutated.

        Parameters
        ----------
        path: list of tuple
            List of size 2 tuples (positions).

        Returns
        -------
        None
        """
        if len(path) < 1:
            return
        piece = board.get_piece(path[-1])
        if (piece is not None and piece.get_player() == self._player):
            path.pop()

    def remove_last_piece(self, path, board):
        """Given a path, removes any piece at the end of the path.

        If no piece found, path is not mutated.

        Parameters
        ----------
        path: list of tuple
            List of size 2 tuples (positions).

        Returns
        -------
        None
        """
        if len(path) < 1:
            return
        piece = board.get_piece(path[-1])
        if (piece is not None):
            path.pop()


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

    def get_moves(self, board):
        pos = self._positions.peek()
        horse_dirs = board.get_horse_dirs()

        # Find paths in each of the 4 ortho directions.
        moves = list()
        for ortho_dir in board.get_ortho_dirs():
            # First move orthogonally one position.
            ortho_path = board.find_ortho_path(pos, ortho_dir, 1)

            if len(ortho_path) == 0 or ortho_path[0] is not None:
                continue

            # Get the first (and only position) from orthogonal path.
            ortho_pos = ortho_path[0]

            for diag_dirs in horse_dirs[ortho_dir]:
                # TODO: Get diags
                pass

            super().remove_friendly(path, board)
            moves += path

        return moves

    def get_diag_positions(self, ortho_pos, ortho_dir, board):
        horse_dirs = board.get_horse_dirs()
        diag_positions = list()  # at most size 2
        diag_dirs = horse_dirs[ortho_dir]
        for diag_dir in diag_dirs:
            diag_pos = board.find_diag(ortho_pos, diag_dir)

            if diag_pos is not None:
                piece = board.get_piece(diag_pos)
                # If position is empty or occupied by enemy piece then
                # it is valid.
                if piece is None or piece.get_player() != self._player:
                    diag_positions.append(diag_pos)

        return diag_positions


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

    def get_moves(self, board):
        pos = self._positions.peek()

        # Find paths in each of the 4 ortho directions.
        moves = list()
        for path_dir in board.get_ortho_dirs():
            path = board.find_ortho_path(pos, path_dir)
            super().remove_friendly(path, board)
            moves += path

        return moves


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

    def get_moves(self, board):
        pos = self._positions.peek()

        # Find paths in each of the 4 ortho directions.
        moves = list()
        targets = list()
        for path_dir in board.get_ortho_dirs():
            path = board.find_ortho_path(pos, path_dir)

            # Look for cannon's firing platform if path nonempty.
            if len(path) > 0:
                platform = board.get_piece(path[-1])
                if platform is not None:
                    # Look for the target in the path in the same
                    # direction behind the platform.
                    attack_path = board.find_ortho_path(platform.get_pos(),
                                                        path_dir)
                    if len(attack_path) > 0:
                        # Target will be first enemy item behind the platform.
                        target = board.get_piece(attack_path[-1])
                        if target is not None and target.get_player() != self._player:
                            targets.append(target.get_pos())

            super().remove_last_piece(path, board)
            moves += path + targets

        return moves

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

    def get_moves(self, board):
        pos = self._positions.peek()

        # Allow column direction away from home row.
        row_directions = [self._player.get_fwd_dir()]  # [_fwd_dir]

        # Allow left and right movement if across river.
        if board.is_across_river(pos, self._player):
            row_directions.append(0)  # [_fwd_dir, 0]

        # List of size two tuple directions. [(_fwd_dir, 0), (0, -1), (0, 1)]
        path_dirs = [direc for direc in board.get_ortho_dirs()
                     if direc[board.get_ROW()] in row_directions]

        moves = list()
        for path_dir in path_dirs:
            path = board.find_ortho_path(pos, path_dir, 1)
            super().remove_friendly(path, board)
            moves += path

        return moves


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

    def __repr__(self):
        """Return the color string of the player."""
        return self._color

    def __str__(self):
        """Return the color string of the player."""
        return self._color

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
        self._pos = pos
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


class NotInMoveListError(IllegalMoveError):
    """Exception class for trying to move a piece to a position not in its
    move list."""
    def __init__(self, piece, moves, end_pos):
        self._piece = piece
        self._moves = moves
        self._end_pos = end_pos
        self._msg = (f'Tried to move {self._piece} at {self._piece.get_pos()} '
                     + f'to {self._end_pos}.\n'
                     + f'move list: {self._moves}')
        super().__init__(self._msg)


class BoardError(Error):
    """Base exception class for miscellaneous Board errors"""
    pass


class SamePositionError(BoardError):
    """Exception class for when expecting two peices on different spaces."""
    def __init__(self, pos):
        self._pos = pos
        self._msg = ('Pieces expected to have different'
                     + f' position but both at {pos}')
        super().__init__(self._msg)


class OutOfBoundsError(BoardError):
    """Exception class for when expecting two peices on different spaces."""
    def __init__(self, pos, axis, axis_count):
        self._pos = pos
        self._axis = axis
        self._max_val = axis_count - 1
        self._msg = (f'Axis {self._axis} must be in [0..{self._max_val}]'
                     + f'but pos was: {self._pos}.')
        super().__init__(self._msg)


if __name__ == '__main__':
    game = XiangqiGame()
    players = game.get_players()
    red, black = players[Player.get_RED()], players[Player.get_BLACK()]
    rp = red.get_pieces()
    bp = black.get_pieces()
    board = game.get_board()
    # -------------------------------------------------------------------------
    sb0, sb1, sb2, sb3, sb4 = black.get_pieces()['soldier']
    sr0, sr1, sr2, sr3, sr4 = red.get_pieces()['soldier']
    # -------------------------------------------------------------------------
    cb0, cb1 = black.get_pieces()['cannon']
    cr0, cr1 = red.get_pieces()['cannon']
    # -------------------------------------------------------------------------
    chb0, chb1 = black.get_pieces()['chariot']
    chr0, chr1 = red.get_pieces()['chariot']
    # -------------------------------------------------------------------------
    hb0, hb1 = black.get_pieces()['horse']
    hr0, hr1 = red.get_pieces()['horse']
    # -------------------------------------------------------------------------
    eb0, eb1 = black.get_pieces()['elephant']
    er0, er1 = red.get_pieces()['elephant']
    # -------------------------------------------------------------------------
    ab0, ab1 = black.get_pieces()['advisor']
    ar0, ar1 = red.get_pieces()['advisor']
    # -------------------------------------------------------------------------
    gb0 = black.get_pieces()['general']
    gr0 = red.get_pieces()['general']
