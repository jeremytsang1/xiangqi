# Author: Jeremy Tsang
# Date: 03/01/2020
# Description: TODO


class XiangqiGame:
    # Class level constants
    _ALPHABET_DCT = {letter: i for i, letter in enumerate('abcdefghi')}
    _ROW_COUNT = 10
    _COL_COUNT = 9

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
