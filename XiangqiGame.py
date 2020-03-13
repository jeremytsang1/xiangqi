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
    """Class to start, control, and facilittate the flow of the Xiangqi game by the
    user.

    Note that although the method make_move() takes its parameters in algebraic
    notation they are immediately translated so that all other positions are
    dealt with in a standard row/col notation (similar to linear algebra
    matrices conventions) where a pair of indices (row, col) denote the
    location of an element in the Board.

    Other conventions to note is that `mover` typically denotes the current
    player (the player 'moving' a piece) and `inactive` typically denotes a
    said player's opponent (they are 'inactive' while the mover is taking their
    turn).
    """
    # Class level constants
    _UNFINISHED = 'UNFINISHED'
    _RED_WON = 'RED_WON'
    _BLACK_WON = 'BLACK_WON'
    _LOSS = {'red': _BLACK_WON, 'black': _RED_WON}

    def __init__(self):
        """Creates an instance of a Xiangqi game where the first player to
        move is player 'red'. Play alternates between valid turns
        taken by players 'red' and 'black' until one of them has no
        more valid moves at which point the other is declared the
        winner. The game does not distinguish between stalemate and
        checkmate (in both cases the mated player loses).
        """
        # Create the two players 'red' and 'black'.
        self._players = {color: Player(color) for color in Player.get_COLORS()}

        # Make players track each other. Cannot be taken care of during Player
        # object creation as the other Player does not even exist yet (i.e. the
        # second player does not exist while the first player is being
        # created).
        self.set_opponents()

        # Create the Board.
        self._board = Board(self._players.values())

        # Start off with neither player victorious.
        self._game_state = XiangqiGame._UNFINISHED

        # Let 'red' move first.
        self._mover = self._players[Player.get_RED()]
        self._inactive = self._players[Player.get_BLACK()]

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
        player = self._players[color]

        return player.get_in_check()

    def make_move(self, alg_start, alg_end, mover=None):
        """Attempts to take the current player's turn.

        A valid/legal move constitutes of the following criterion:
            - The game must not have ended.

            - The algebraic notation must be valid for both positions.

            - The alg_start must refer to a position where a piece
              belonging to the mover currently resides.

            - The alg_end must move be in accordance to how the piece
              at alg_start moves.

            - Move must not leave the mover in a checked state.

            - If currently in checked state, the move must be such
              that after it is successful the player is no longer in
              check.


        Parameters
        ----------
        alg_start: str
            Algebraic notation of the piece to move.
        alg_end: str
            Algebraic notatio of the location to move the piece to.
        mover: Player
            Player moving the piece. If set to None the piece is moved
            by the current player.

        Returns
        -------
        bool
            True if the move was valid. False if invalid.

        """
        # TODO: get rid of mover
        if mover is not None and mover is not self._mover:
            self.switch_mover(self._mover)
        # Prevent moves if game is already over.
        if self._game_state != XiangqiGame._UNFINISHED:
            return False

        # Validate algebraic notation.
        try:
            pos_start = AlgNot.alg_to_row_col(alg_start)
            pos_end = AlgNot.alg_to_row_col(alg_end)
        except AlgStrFormattingError:
            return False

        # Attempt the mover's move.
        try:
            self.move_mover(pos_start, pos_end, self._mover, self._inactive)
        except IllegalMoveError:
            return False

        # Update check status of inactive player
        self._inactive.set_in_check(self._inactive.is_in_check(self._board))

        # Check if the game is over
        self.update_game_state()

        # alternate mover
        self.switch_mover(self._mover)

        return True

    def move_mover(self, beg_pos, end_pos, mover, inactive):
        """Update the mover's Piece's location on the board.

        If the method executes successfully the mover will not be in check.

        Raises
        ------
        MoverMoveResultedInOwnCheckError:
            When attempting to move the piece in such a way that would leave
            the mover's general open to direct attack on the next turn.
        NoPieceAtStartPosError:
            When trying to move a none-existant piece at beg_pos.
        WrongPieceOwner:
            When attempting to move a piece that does not belong to mover.
        NotInMoveListError:
            When attempting to move the piece that is not in accordance to its
            moves dictated by its nature.

        Parameters
        ----------
        beg_pos: tuple of int
            Position of the mover's piece.
        end_pos: tuple of int
            Position to move the mover's piece.
        mover: Player
            Current player player making the move.
        inactive: Player
            Player that is not making the move.

        Returns
        -------
        None
        """

        # Make the move. Board is updated accordingly if there was a
        # indeed a player at the beg_pos that belonged to the player
        # whose moves allow it to traverse to the end_pos.
        taken = self._board.make_move(beg_pos, end_pos, mover)

        # Remove captured piece taken from its player (opponent of mover).
        if taken is not None:
            # --------------------------------------
            # TODO: remove assertion
            msg = f'Tried taking already dead piece {taken}'
            assert inactive.belongs_to(taken), msg
            # Assumed taken belongs to inactive
            # TODO: remove assertion
            msg = f'TRIED TO TAKE FRIENDLY PIECE: {taken}'
            assert taken.get_player() is inactive, msg
            # --------------------------------------
            inactive.remove_piece(taken)

        # Determine if the virtual move leaves the virtual mover in check.
        if mover.is_in_check(self._board):
            # If move exposes general, abort the move.
            moved = self.undo_move(taken, inactive)
            raise MoverMoveResultedInOwnCheckError(end_pos, moved, mover)

        # Guarantees that after every successful move, the mover is now out of
        # check.
        if mover.get_in_check():
            mover.set_in_check(False)

    def update_game_state(self):
        """Updates the current player's (mover player) opponent (inactive
        player) check state after. Assumed to be called after the
        mover has relocated their piece on the Board.

        Finally computes whether the game has ended by counting all
        valid moves of the inactive player. If said player has no
        valid moves then the game has been won by the mover.
        """
        pieces = self._inactive.get_all_pieces(self._inactive)
        valid_move_count = 0  # if no valid moves, then game is over.

        # Check each each of the inactives pieces to see if it has any valid
        # moves.
        for piece in pieces:
            # Piece's current position.
            beg_pos = piece.get_pos()

            # Get all possible moves for the given piece.
            end_positions = piece.get_moves(self._board)

            for end_pos in end_positions:
                try:
                    # If the move succeeds, add count it towards the total.
                    self.validate_virual_move(beg_pos, end_pos,
                                              self._inactive, self._mover)
                    valid_move_count += 1
                except IllegalMoveError:
                    # Do not count failed moves towards the total.
                    pass

        if valid_move_count == 0:
            self._game_state = self._LOSS[self._inactive.get_color()]

    def validate_virual_move(self, beg_pos, end_pos,
                             vir_mover, vir_inactive):
        """Emulates method XiangqiGame.move_mover() to check if a hypothetical
        move is valid or not.

        Makes the move but if it raises exception then it is
        determined invalid. If it completes successfully then the move
        is valid.

        Raises
        ------
        MoverMoveResultedInOwnCheckError:
            When attempting to move the piece in such a way that would leave
            the mover's general open to direct attack on the next turn.
        NoPieceAtStartPosError:
            When trying to move a none-existant piece at beg_pos.
        WrongPieceOwner:
            When attempting to move a piece that does not belong to mover.
        NotInMoveListError:
            When attempting to move the piece that is not in accordance to its
            moves dictated by its nature.

        Parameters
        ----------
        beg_pos: tuple of int
            Position of the virtual mover's piece.
        end_pos: tuple of int
            Position to move the virtual mover's piece to.
        vir_mover: Player
            Player making the virtual move.
        vir_inactive: Player
            Opponent of the virtual mover.

        Returns
        -------
        None
        """
        vir_mover_now_exposed = False  # Boolean flag variable.

        # Make the hypothetical move. Board is updated accordingly if there was
        # a indeed a player at the beg_pos that belonged to the player whose
        # moves allow it to traverse to the end_pos. Otherwise raises
        # appropriate exception.
        taken = self._board.make_move(beg_pos, end_pos, vir_mover)

        # Remove the captured from the virtual mover's opponent to subsequently
        # allow accrutate determination if the virtual mover is in check
        # afterwards.
        if taken is not None:
            vir_inactive.remove_piece(taken)

        # Determine if the virtual move leaves the virtual mover in check.
        if vir_mover.is_in_check(self._board):
            vir_mover_now_exposed = True

        # Undo the hypothetical turn regardless if it was valid or not (since
        # it is a "hypothetical" turn after all).
        moved = self.undo_move(taken, vir_inactive)

        # Raise exception if move would leave general exposed.
        if vir_mover_now_exposed:
            raise MoverMoveResultedInOwnCheckError(end_pos, moved, vir_mover)

    def undo_move(self, taken, inactive):
        """Reverse a move that has just occured.

        Puts the moved piece back where was originally.

        Puts the captured piece back where it was and adds it back to the
        Player it was taken from.

        Parameters
        ----------
        taken: Piece
            The piece that was captured by the mover of the move to be
            reversed.
        inactive: Player
            Opponent of the player `taken` was taken from (i.e. the opponent of
            the player who made the move to be reversed).

        Returns
        -------
        Piece
            The Piece that was moved in the reverted move.

        """
        # Assumes taken was originally owned by inactive.

        # Restore board position to what it was before move was made.
        moved = self._board.undo_move(taken)

        # If taken is a piece, send it back to its original owner's piece
        # dictionary.
        if taken is not None:
            # TODO: remove assertion
            assert taken.get_player() is inactive
            inactive.add_piece(taken)

        return moved

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

    def switch_mover(self, current_mover):
        """Makes the opponent of the specified mover the new current mover.

        Parameters
        ----------
        current_mover: Player
            Player to be made into the inactive player.

        Returns
        -------
        None
        """
        if current_mover.get_color() == current_mover.get_RED():
            self._mover = self._players['black']
            self._inactive = self._players['red']
        else:
            self._mover = self._players['red']
            self._inactive = self._players['black']


class Board:
    """Class defining the physical game board. Has 5 rows on each side of the river
    (10 rows total) and 9 columns total.

    *****ALGEBRAIC NOTATION IS NOT USED IN THIS CLASS!*****
    (only minimally used in class XiangqiGame)

    This class uses row/column index notation where (0, 0) (translates to 'a10'
    in algebraic notation) represents the upper left corner and (10, 9)
    (translates to 'i1' in algebraic notation) the lower right corner.

    Row 0 represents the top of the board ('black' home row).

    Row 9 represents the bottom of the board ('red' home row).

    "Orthogonal" in this class refers to the vertical or horizontal directions
    (even though geometrically speaking the diagonals are technically
    orthogonal as they intersect at right angles).

    Axes respond to the two directions row direction and column direction.
        - Axis 0 corresponds to rows
        - Axis 1 corresponds to columns (at times abbreviated as 'cols').

    Positions (abbreviated pos) are represented size 2 tuples of int where
        - index 0 represents row value
        - index 1 represents col value

    Note due to fact that positions are ***size 2*** (one for element
    row and one element for column) the complement of one can computed
    by subtracting 1 either index 0 or 1 will yield the index of the
    other element because for a given position. For example
        position[0] == pos[1 - 1]
        position[1] == pos[0 - 1] = pos[-1]

    Directions are represented by size 2 tuples of int and contain values
    either of _FWD, _REV, or 0. Directions can be scaled by multiplying their
    components by a scale factor.

    """

    # Constants
    _ROW_COUNT = 10
    _COL_COUNT = 9
    _AXES_COUNTS = (_ROW_COUNT, _COL_COUNT)
    _RIVER_DIST = 5

    # Axes constants
    _ROW = 0
    _COL = 1

    # Direction constants
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
        # Represent the board as a 2D nested list where the sublists represent
        # the rows of the board..
        self._board = [[None for j in range(Board._COL_COUNT)]
                       for i in range(Board._ROW_COUNT)]

        # Place all the Pieces belonging to the players on the Board.
        for piece in Player.get_all_pieces(*players):
            row, col = piece.get_pos()
            self._board[row][col] = piece

        # Designate castle regions by player color strings Player._RED and
        # Player._BLACK.
        self._castles = {player.get_color(): self.make_castle(player)
                         for player in players}

        # Store the move history in a stack for allowing easier history
        # rollback.
        self._last_pos = Stack()

    def __repr__(self):
        """Debugging method. Print a text visualization of the board. Assumes
        each piece has __repr__ implemented such that its string
        representation is 5 characters or less.
        """
        # Cell ceiling and floor.
        dashes = "--------"  # TODO: remove hard coded length?

        # Uses '|' as cell walls. and '+' for cell corner where wall meets
        # floor or celing. `divider` will be the entire floor/ceiling for a
        # given row.
        divider = (
            # Leftmost wall.
            "|"
            # Extra column to display row numbers.
            + dashes
            # Make the celings for all 9 columns.
            + "".join([f"+{dashes}" for col in range(Board._COL_COUNT)])
            # Rightmost wall.
            + "|"
        )

        # Row template. Prepare a string for use with str.format() to
        # substitute each Piece in between walls.
        row_temp = (
            # Leftmost wall.
            "|"
            # Format string to substitute for the Pieces string
            # representations. Add 1 to account for extra column for row
            # numbers.
            + "|".join(["{{: ^{}}}".format(len(dashes))
                        for i in range(Board._COL_COUNT + 1)])
            # Rightmost wall.
            + "|"
        )

        # Top most row of above all pieces.
        header_row = row_temp.format(*([""]  # Header above row nums empty.
                                       # Fill in the row column nums.
                                       + [i for i in range(Board._COL_COUNT)]))

        # Start concatenating to a single result string.
        res = divider + "\n" + header_row

        # Concantenate each row.
        for i, row in enumerate(self._board):
            res += ("\n" + divider + "\n"                     # Celing.
                    + row_temp.format(*([i]                   # Row num.
                                        + ["" if elt is None  # Unoccupied.
                                           else str(elt)      # Occupied.
                                           for elt in row])))
        # Finally add the the bottom floor.
        res += "\n" + divider

        return res

    def get_piece(self, pos):
        """Get the piece at the given position.

        Assumes whenever a piece is moved, the element where it used to
        be is now occupied by None.

        Parameters
        ----------
        pos: tuple of int
            Position of where to look.

        Returns
        -------
        Piece
            The piece at the specified position. If position is unoccupied
            returns None.
        """
        return self._board[pos[Board._ROW]][pos[Board._COL]]

    def place_piece(self, new_pos, piece):
        """Places the piece at the new position and updates position
        accordingly. Marks the piece's original position as
        unoccupied.

        If the new_pos is the same as the piece's current
        position (e.g. it was not on the board as it had been
        captured) then just sets the location at the board to the
        piece without updating the piece's position data or the old
        position (due to the lack thereof).

        Parameters
        ----------
        new_pos: tuple of int
            Size 2 tuple indicating position of where to move the piece.
        piece: Piece
            Piece to move. Should be not None.

        Returns
        -------
        None
        """
        old_pos = piece.get_pos()               # Piece still at old spot.
        self.set_board_list(new_pos, piece)     # Place piece at its new spot.
        if old_pos != new_pos:
            self.set_board_list(old_pos, None)  # clear the spot moved from.
            piece.push(new_pos)                 # Save the new position

    def set_board_list(self, pos, elt):
        """Directly access the board nested list.

        Mostly to skip manually indexing.

        Parameters
        ----------
        pos: tuple of int
            Position to assign the new element.
        elt: Piece
            Either existing Piece or None to assign the position.

        Returns
        -------
        None
        """
        self._board[pos[self._ROW]][pos[self._COL]] = elt

    def make_move(self, beg_pos, end_pos, moving_player):
        """Moves pieces on the board. Updates the moved piece location.

        Raises
        ------
        NoPieceAtStartPosError:
            When the position beg_pos refers to an unoccupied position.
        WrongPieceOwner:
            When the Piece at beg_pos does not belong to moving_player.
        NotInMoveListError:
            When the end_pos is not in the move list fo the Piece.

        Parameters
        ----------
        beg_pos: tuple of int
            Position of the piece to move.
        end_pos: tuple of int
            Position of where to move the piece.
        moving_player: Player
            Player making the move.

        Returns
        -------
        Piece
            Piece that was captured if end_pos was occupied. Otherwise None.
        """
        beg_piece = self.get_piece(beg_pos)
        end_piece = self.get_piece(end_pos)

        # Validate that there is a piece at the begining position that belongs
        # to the mover.
        if beg_piece is None:
            raise NoPieceAtStartPosError(beg_pos)
        if beg_piece.get_player() != moving_player:
            raise WrongPieceOwner(moving_player, beg_pos)

        # Get piece move list.
        moves = beg_piece.get_moves(self)

        # Check if in move list.
        if end_pos not in moves:
            raise NotInMoveListError(beg_piece, moves, end_pos)

        self.place_piece(end_pos, beg_piece)  # Move the piece.
        self._last_pos.push(end_pos)          # Save the location.
        return end_piece

    def undo_move(self, taken_piece):
        """Reverses changes to the Board in the previous move. If taken_piece
        was captured in the previous move it is placed back on the board
        to where it was.

        Assumed not called on the first turn.

        Parameters
        ----------
        taken_piece: Piece
            The Piece captured in the last move. Can be None.

        Returns
        -------
        Piece
            The piece that was moved.
        """
        # The move's original "end position"
        action_pos = self._last_pos.pop()

        # The move's original moved piece.
        moved_piece = self.get_piece(action_pos)

        # Clear the piece's current location to get where it came from.
        moved_piece.pop()

        # Move the original moved piece back to where it originally was.
        self.set_board_list(moved_piece.get_pos(), moved_piece)

        # Determine what to put back at the original move's end position.
        if taken_piece is not None:  # End position was unoccupied.
            self.set_board_list(taken_piece.get_pos(), taken_piece)
        else:                        # End position was occupied.
            self.set_board_list(action_pos, taken_piece)

        return moved_piece

    def make_castle(self, player):
        """Helper method to create record of each player's castle positions.

        Should only be called upon board creation.

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
        center_col = general.get_pos()[self._COL]

        # Add the displacements (-1, 0, 1) go the castle's center
        # location to get all 9 positions in the castle.
        displacements = (-1, 0, 1)

        # Find castle positions.
        castle_positions = tuple([(center_row + i, center_col + j)
                                  for i in displacements
                                  for j in displacements])
        return castle_positions

    def get_castle(self, color):
        """Getter.

        Get the castle positions for the given player (specified by the
        player's color).

        Parameters
        ----------
        color: str
            Color associated with player. Either Player._RED or Player._BLACK.

        Returns
        -------
        Tuple of tuple of int
            Tuple of size 2 tuples (position tuples).

        """
        return self._castles[color]

    def is_in_castle(self, pos, player):
        """Predicate.

        Parameters
        ----------
        pos: tuple of int
            Position to check if in castle.
        player: Player
            Player whose castle to check.

        Returns
        -------
        bool
            True if pos is located in player's castle. Otherwise False.
        """
        return pos in self._castles[player.get_color()]

    def find_diag(self, beg_pos, dir_diag, dist=1):
        """Compute positions in a diagonal direction from the beginning position.

        Parameters
        ----------
        beg_pos: tuple of int
            Starting position to traverse from.
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

        # Discard the new diagonal if it does lie on the Board.
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
            Starting position to traverse from.
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

        # Takes advantage of ***size 2*** tuple (see class Board docstring).
        direction = dir_ortho[delta_axis]  # Either _FWD or _REV.
        constant_axis = delta_axis - 1     # Axis being traveled along.

        # Edge locations along the delta axis.
        delta_axis_min = 0
        delta_axis_max = Board._AXES_COUNTS[delta_axis]

        # Create two element list. Can't explicitly initialize due to
        # end points depending on direction.
        end_pos = [0, 0]

        # Set the edge of Board to the first guess for the ending position.
        # Takes advantage of ***size 2*** tuple (see class Board docstring).
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
        path = list()                # List of positions to return.

        for delta_elt in range(beg_pos[delta_axis] + direction,  # Exclude beg.
                               end_pos[delta_axis] + direction,  # Include end.
                               direction):
            # Travel one position in specified direction.
            current_pos[delta_axis] = delta_elt
            # Add said position to the path. Make sure not to use mutable type
            # or else the all path positions will contain the same value.
            path.append(tuple(current_pos))
            # If find encounter a piece along the path, stop traversing.
            if self.get_piece(current_pos) is not None:
                return path
        return path

    def find_intervening_ortho(self, beg_pos, end_pos):
        """Check if there is at least one piece between two positions.

        Raises
        ------
        SamePositionError:
            When both positions refer the same location.

        Parameters
        ----------
        beg_pos: tuple of int
            Starting position.

        end_pos: tuple of int
            Ending position

        Returns
        -------
        Piece
            None if there are no pieces on a orthogonal axis between the two
            positions. Otherwise returns the first piece that is encountered
            from traversing from beginining position to end position.
        """
        # Find which if the two positions are on the same row or same col.
        common_axis = Board.find_common_axis(beg_pos, end_pos)

        # No intervening Piece if two positions share neither a row or col.
        # TODO: maybe move this outside.
        if common_axis == -1:
            return None

        # The axis that the two positions do not share.
        # Takes advantage of ***size 2*** tuple (see class Board docstring).
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

        Raises:
        SamePositionError:
            When the two positions are identical.

        Parameters
        ----------
        beg_pos: tuple of int
            First position to compare to.
        end_pos: tuple of int
            Second position to compare with.

        Returns
        -------
        int
            Board._ROW if both positions share the same row.
            Board._COL if both positions share the same col.
            -1 if the two positions do not have a common axis.
        """
        beg_row, beg_col = beg_pos
        end_row, end_col = end_pos

        if (beg_row, beg_col) == (end_row, end_col):  # Refer to same pos.
            raise SamePositionError((beg_row, beg_col))
        elif beg_row != end_row and beg_col != end_col:  # Do not share.
            return -1
        elif beg_row == end_row:
            return Board._ROW  # Share row.
        else:
            return Board._COL  # Share col.

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
        """Find the one-dimensional direction between two pieces.

        Raises
        ------
        SamePositionError:
            When the positions both refer to the same position.

        Parameters
        ----------
        beg: int
            Starting element.
        end: int
            Ending element.

        Returns
        -------
        int
            One-dimensional direction is either 1 or -1. 1 if end is more than
            beginning and -1 if less.
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
            Position to check.

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
    def get_diag_dirs():
        """Getter. Returns all diagonal directions."""
        return Board._DIRECTIONS_DIAG

    @staticmethod
    def get_ortho_dirs():
        """Getter. Returns all orthogonal directions"""
        return Board._DIRECTIONS_ORTHO

    @staticmethod
    def get_horse_dirs():
        """Getter. Returns all directions used by Horses as a dictionary with the
        initial orthogonal directions as keys and resulting jump diagonals as
        values.
        """
        return Board._DIRECTIONS_HORSE

    @staticmethod
    def get_ROW():
        """Getter. Return row axis index."""
        return Board._ROW

    @staticmethod
    def get_COL():
        """Getter. Return col axis index."""
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
        """Clear the most recent position from the piece's history."""
        return self._positions.pop()

    def is_friendly(self, piece):
        """Predicate. True if piece belongs to same player as calling Piece.
        Otherwise False.

        Note: not necessarily the negation of is_hostile() due to the
        possibility Piece may be None (unoccupied) position.
        """
        return piece is not None and piece.get_player() is self._player

    def is_hostile(self, piece):
        """Predicate. True if piece does not belongs to same player as calling
        Piece.  Otherwise False.

        Note: not necessarily the negation of is_friendly() due to the
        possibility Piece may be None (unoccupied) position.

        """
        return piece is not None and piece.get_player() is not self._player

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
        # Stop if path is empty.
        if len(path) < 1:
            return
        piece = board.get_piece(path[-1])  # Examine pos at end of path.

        # Shorten the path by one position if there is a friendly piece
        # at the end.
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
        # Stop if path is empty.
        if len(path) < 1:
            return
        piece = board.get_piece(path[-1])  # Examine pos at end of path.

        # Shorten the path by one position if there is any piece
        # at the end.
        if (piece is not None):
            path.pop()


class General(Piece):
    """
    Class to represent the general piece. Can detect line of sight of enemy
    general.
    """
    _ABBREV = 'g'
    _INIT_COLS = (4,)
    _ORTHO_DIST = 1

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

    def get_moves(self, board):
        """Get all the moves where a the general can move to. Moves are
        restricted to Castle and do not include positions that can be
        attacked by enemy pieces (including the enemy general).

        Parameters
        ----------
        board: Board
            Board the general is placed on.

        Returns
        -------
        list of tuple of int
            List of positions.
        """
        pos = self._positions.peek()

        moves = list()

        # Grab all non-friendly orthogonal positions _ORTHO_DIST
        # positions away.
        for path_dir in board.get_ortho_dirs():
            path = board.find_ortho_path(pos, path_dir, self._ORTHO_DIST)
            super().remove_friendly(path, board)
            # Restrict to castle
            path = [tmp_pos for tmp_pos in path
                    if board.is_in_castle(tmp_pos, self._player)]
            moves += path

        # Get enemy threat.
        opponent = self._player.get_opponent()
        threat = opponent.get_threat(board)

        # Prevent general from moving in to enemy threat area.
        return list(set(moves) - threat.keys())

    def get_enemy_castle_sight(self, board):
        """Find all positions in the enemy's castle directly visible by the calling
        General with no intervening pieces.

        Parameters
        ----------
        board: Board
            Board that the calling General is located on.

        Returns
        -------
        list of tuple of int
            List of positions.
        """
        opponent = self._player.get_opponent()
        enemy_gen = opponent.get_pieces()[Player.get_GENERAL()][0]
        castle = board.get_castle(self._player.get_opponent().get_color())
        castle_sight = []  # List of positions the calling general threatens
        current_pos = self._positions.peek()
        col = current_pos[board.get_COL()]

        # Traverse enemy castle column from outter most row to enemy home rome.
        for pos in [castle_pos
                    for castle_pos in castle[::self._player.get_fwd_dir()]
                    if castle_pos[board.get_COL()] == col]:

            piece = board.get_piece(pos)
            intervening = None

            if piece is None or piece is enemy_gen:
                # Note that find_intervening_ortho() will not raise
                # SamePositionError as the General's will never visit the enemy
                # castle.
                intervening = board.find_intervening_ortho(current_pos, pos)
                if intervening is None or intervening is enemy_gen:
                    # Inetervening is enemy general allows calling general to
                    # threaten empty columns behind enemy general (because if
                    # enemy general moved vertically they would still be in
                    # line of sight of calling gneral.
                    castle_sight.append(pos)
                else:
                    # Encountered General
                    break
            else:
                # Encountered non-general Piece in castle. All columns behind
                # it are not visible to calling general.
                break

        return castle_sight


class Advisor(Piece):
    _ABBREV = 'a'
    _INIT_COLS = (3, 5)  # Index with _id_num.
    _DIAG_DIST = 1

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
        """Get all the moves where a the advisor can move to. Moves are
        restricted to Castle and can only be diagonal.

        Parameters
        ----------
        board: Board
            Board the general is placed on.

        Returns
        -------
        list of tuple of int
            List of positions.
        """
        current_pos = self._positions.peek()

        moves = list()

        # Inspect each of the diagonal directions.
        for diag_dir in board.get_diag_dirs():
            pos = board.find_diag(current_pos, diag_dir, self._DIAG_DIST)

            # Restrict to castle.
            if board.is_in_castle(pos, self._player):
                piece = board.get_piece(pos)
                if not self.is_friendly(piece):
                    moves.append(pos)
        return moves


class Elephant(Piece):
    _ABBREV = 'e'
    _INIT_COLS = (2, 6)  # Index with _id_num.
    _ATTAC_DIST = 2
    _BLOCK_DIST = 1

    def __init__(self, player, id_num):
        """Create an object of type Elephant with location based on player and
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
        """Get all the moves where a the elephant can move to. Moves are
        restricted to player's side of the river only be two diagonals
        away. Note that if a piece is 1 diagonal away, it will block the
        position two diagonals away.

        Parameters
        ----------
        board: Board
            Board the general is placed on.

        Returns
        -------
        list of tuple of int
            List of positions.
        """
        current_pos = self._positions.peek()

        moves = list()

        # Inspect each diagonal direction.
        for diag_dir in board.get_diag_dirs():

            adj_pos = board.find_diag(current_pos, diag_dir, dist=self._BLOCK_DIST)
            pos = board.find_diag(current_pos, diag_dir, dist=self._ATTAC_DIST)
            in_bounds = pos is not None

            # If pos is in bounds, then adj is definitely in bounds as well so
            # don't need to check adj OOB

            # Make sure not jumping off board.
            if in_bounds:
                is_unblocked = board.get_piece(adj_pos) is None

                # Only valid if not blocked nor across river.
                if is_unblocked and not board.is_across_river(pos, self._player):
                    piece = board.get_piece(pos)
                    if not self.is_friendly(piece):
                        moves.append(pos)
        return moves


class Horse(Piece):
    _ABBREV = 'h'
    _INIT_COLS = (1, 7)  # Index with _id_num.
    _ORTHO_DIST = 1
    _DIAG_DIST = 1

    def __init__(self, player, id_num):
        """Create an object of type Horse with location based on player and
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
        """Get all the moves where a the horse can move to. Moves are computed
        in two parts. First go one orthogonal with a distance of
        1. Then go diagonal with diagonal distance of 1. If horizontal
        direction is blocked this blocks off both of that directions
        diagonal positions.

        Parameters
        ----------
        board: Board
            Board the general is placed on.

        Returns
        -------
        list of tuple of int
            List of positions.

        """
        pos = self._positions.peek()

        # Find paths in each of the 4 ortho directions.
        moves = list()
        for ortho_dir in board.get_ortho_dirs():
            # First move orthogonally one position.
            ortho_path = board.find_ortho_path(pos, ortho_dir, self._ORTHO_DIST)

            # Validate the ortho move.
            empty = len(ortho_path) == 0
            ortho_blocked = (board.get_piece(ortho_path[0])
                             is not None if not empty else False)

            # Choose next ortho direction if invalid.
            if empty or ortho_blocked:
                continue

            # Get the first (and only position) from orthogonal path.
            ortho_pos = ortho_path[0]

            # Compute the diagonals (up to two valid ones) for the
            # ortho position.
            diag_positions = self.get_diag_positions(ortho_pos, ortho_dir,
                                                     board)

            # Add the valid diagonals to the move list.
            moves += diag_positions

        return moves

    def get_diag_positions(self, ortho_pos, ortho_dir, board):
        """Compute valid diagonal positions after computing the orthogonal
        position.

        Parameters
        ----------
        ortho_pos: tuple of int
            Position to jump from.
        ortho_dir: tuple of int
            Orthogonal direction from horse.
        board: Board
            Board the Horse is located on.

        Returns
        -------
        list of tuple of int
            List of diagonal positions.
        """
        horse_dirs = board.get_horse_dirs()
        diag_positions = list()  # at most size 2
        diag_dirs = horse_dirs[ortho_dir]

        # Look in the two horse diagonal directions.
        for diag_dir in diag_dirs:
            diag_pos = board.find_diag(ortho_pos, diag_dir, self._DIAG_DIST)

            if diag_pos is not None:               # Make sure not jumping off board.
                piece = board.get_piece(diag_pos)  # Get diagonal.
                if not self.is_friendly(piece):    # Don't kill friendlies.
                    diag_positions.append(diag_pos)

        return diag_positions


class Chariot(Piece):
    _ABBREV = 'ch'
    _INIT_COLS = (0, 8)  # Index with _id_num.

    def __init__(self, player, id_num):
        """Create an object of type Chariot with location based on player and
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
        """Create an object of type Cannon with location based on player and
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
        moves = list()

        # Find paths and targets in each of the 4 ortho directions.
        for path_dir in board.get_ortho_dirs():
            path = board.find_ortho_path(pos, path_dir)
            targets = self.get_targets_from_path(path, path_dir, board)
            super().remove_last_piece(path, board)  # Can't attack directly.
            moves += path + targets

        return moves

    def get_targets(self, board):
        pos = self._positions.peek()

        # Look for targets in each of the 4 ortho directions.
        moves = list()
        for path_dir in board.get_ortho_dirs():
            path = board.find_ortho_path(pos, path_dir)
            targets = self.get_targets_from_path(path, path_dir, board)
            moves += targets

        return moves

    def get_targets_from_path(self, path, path_dir, board):
        targets = []
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
                    if self.is_hostile(target):
                        targets.append(target.get_pos())
        return targets


class Soldier(Piece):
    _ABBREV = 's'
    _INIT_ROWS = {"black": 3, "red": 6}  # TODO: remove hard coded keys?
    _INIT_COLS = (0, 2, 4, 6, 8)  # Index with _id_num.

    def __init__(self, player, id_num):
        """Create an object of type Soldier with location based on player and
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
        self._in_check = False

    def __repr__(self):
        """Return the color string of the player."""
        return self._color

    def __str__(self):
        """Return the color string of the player."""
        return self._color

    def get_in_check(self):
        return self._in_check

    def set_in_check(self, in_check):
        self._in_check = in_check

    def is_in_check(self, board):
        """Determine if the calling Player is in check.

        Returns
        -------
        bool
            True if calling Player is in check. Otherwise False.
        """
        # Both player's can't be in check at the same time.
        opponent = self._opponent

        if opponent.get_in_check():
            return False

        threat = opponent.get_threat(board)
        general = self._pieces[self.get_GENERAL()][0]

        if general.get_pos() in threat:
            return True

        return False

    def get_threat(self, board):
        """Get all the positions under attack by the player's pieces.

        Parameters
        ----------
        board: Board
            Current play board.

        Returns
        -------
        dict
            Keys are positions under attack. Values are sets of pieces
            who can attack the position.
        """
        threat = {}
        Player.get_all_pieces(self)

        for piece in Player.get_all_pieces(self):
            # Determine method of gathering threat positions based on subtype
            # of Piece.
            if isinstance(piece, General):
                threat_method = piece.get_enemy_castle_sight
            elif isinstance(piece, Cannon):
                threat_method = piece.get_targets
            else:
                threat_method = piece.get_moves

            # Get all the positions threatened by the current piece.
            for move in threat_method(board):
                if move not in threat:
                    threat[move] = set()
                threat[move].add(piece)

        return threat

    def find_key(self, piece):
        """Lookup the string key for the given Piece.

        Parameters
        ----------
        piece: Piece
            Piece to check. Assumed not None.

        Returns
        -------
        str
            Dictionary key for the piece.
        """
        for dct in self._PIECE_DCTS:
            if isinstance(piece, dct['class']):
                return dct['key']

    def belongs_to(self, piece):
        key = self.find_key(piece)
        return piece in self._pieces[key]

    def remove_piece(self, piece):
        key = self.find_key(piece)
        # TODO: check if piece is already removed?
        self._pieces[key].remove(piece)

    def add_piece(self, piece):
        key = self.find_key(piece)

        # Avoid re-adding Pieces that already belong to the player.
        if piece in self._pieces[key]:
            raise AlreadyInPieceList(piece, self)

        self._pieces[key].append(piece)

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


class MoverMoveResultedInOwnCheckError(IllegalMoveError):
    """Exception class for when a player attempts to make an illegal move where
    they leave their general exposed to direct threat.
    """
    def __init__(self, pos, piece, player):
        self._pos = pos
        self._player = player
        self._msg = (f'Player ({player}) tried moving piece ({piece}) '
                     + f'to pos ({pos}) but is now in check')
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


class PlayerError(Error):
    """Base exception class for Player errors"""
    pass


class AlreadyInPieceList(PlayerError):
    """Exception class for when attempting to add a Piece to a player that
    already owns it."""
    def __init__(self, piece, player):
        self._piece = piece
        self._player = player
        self._msg = f'{self._piece} already belongs to {self._player}'
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
    gb0 = black.get_pieces()['general'][0]
    gr0 = red.get_pieces()['general'][0]
