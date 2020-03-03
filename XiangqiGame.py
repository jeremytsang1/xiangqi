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
        # TODO: Add exception handling for
        #   - OOB
        #   - short strings
        #   - long strings
        #   - invalid chars
        alg_letter = alg_str[0]
        alg_num = int(alg_str[1:])  # TODO: wrap in try block

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
    def __init__(self):
        max_row_digits = len(str(XiangqiGame._ROW_COUNT))
        super().__init__('Algebraic string must be between 2 to '
                         + f'{1 + max_row_digits} '
                         + 'characters long (inclusive).')


class AlgLetterError(AlgStrFormattingError):
    def __init__(self):
        letters = XiangqiGame.get_ALPHABET()[:XiangqiGame.get_COL_COUNT()]
        super().__init__(f'Algebraic column letter must be in "{letters}".')


class AlgNumFormatError(AlgStrFormattingError):
    def __init__(self):
        super().__init__('Algebraic row number must be a valid integer.')


class AlgNumOutOfBoundsError(AlgStrFormattingError):
    def __init__(self):
        super().__init__('Algebraic row number must fall between 1 and '
                         + f'{XiangqiGame.get_ROW_COUNT()} '
                         + 'inclusive.')
