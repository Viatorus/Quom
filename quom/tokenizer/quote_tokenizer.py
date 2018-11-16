from enum import Enum

from quom.utils.iterable import Iterator
from .token import Token, TokenType


class LiteralEncoding(Enum):
    NONE = 0,
    WIDE = 1,
    UTF8 = 2,
    UTF16 = 3,
    UTF32 = 4,
    RAW = 5,
    RAW_WIDE = 6,
    RAW_UTF8 = 7,
    RAW_UTF16 = 8,
    RAW_UTF32 = 9


class QuoteType(Enum):
    SINGLE = 0
    Double = 1


class QuoteToken(Token):
    def __init__(self, start, end, type: QuoteType, encoding: LiteralEncoding = None):
        super().__init__(start, end, TokenType.QUOTE)
        self.quote_type = type
        self.encoding = encoding


def to_literal_encoding(identifier: str):
    if identifier == 'u8':
        return LiteralEncoding.UTF8
    elif identifier == 'u':
        return LiteralEncoding.UTF16
    elif identifier == 'U':
        return LiteralEncoding.UTF32
    elif identifier == 'L':
        return LiteralEncoding.WIDE
    elif identifier == 'R':
        return LiteralEncoding.RAW
    elif identifier == 'u8R':
        return LiteralEncoding.RAW_UTF8
    elif identifier == 'uR':
        return LiteralEncoding.RAW_UTF16
    elif identifier == 'UR':
        return LiteralEncoding.RAW_UTF32
    elif identifier == 'LR':
        return LiteralEncoding.RAW_WIDE
    raise Exception('Unknown literal encoding.')


def scan_for_quote_single(it: Iterator, _: Iterator):
    if it[0] != '\'':
        return None
    start = it
    it += 1

    # Parse until end of line or non escaped '.
    backslashes = 0
    while it[0] != '\n' and (it[0] != '\'' or backslashes % 2 != 0):
        if it[0] == '\\':
            backslashes += 1
        else:
            backslashes = 0
        it += 1

    # Check if end of line is reached.
    if it[0] == '\n':
        raise Exception("Character sequence not terminated!")
    it += 1

    return QuoteToken(start, it, QuoteType.SINGLE)


def scan_for_quote_double(it: Iterator, it_end: Iterator, identifier: str = None):
    if it[0] != '"':
        return None
    start = it
    it += 1

    encoding = LiteralEncoding.NONE
    if identifier:
        encoding = to_literal_encoding(identifier)

    if encoding in [LiteralEncoding.NONE, LiteralEncoding.WIDE, LiteralEncoding.UTF8, LiteralEncoding.UTF16,
                    LiteralEncoding.UTF32]:
        # Parse until end of line or non escaped ".
        backslashes = 0
        while it[0] != '\n' and (it[0] != '"' or backslashes % 2 != 0):
            if it[0] == '\\':
                backslashes += 1
            else:
                backslashes = 0
            it += 1

        # Check if end of line is reached.
        if it[0] == '\n':
            raise Exception("Character sequence not terminated!")
        it += 1
    else:
        delimiter = ""

        # Parse until end of introductory delimiter.
        while it != it_end and it[0] != '(':
            delimiter += it[0]
            it += 1

        if it == it_end:
            raise Exception('No introductory delimiter inside raw string literal found!')
        it += 1

        # Define terminating delimiter.
        delimiter = ')' + delimiter + '"'

        # Parse until delimiter occours again.
        # TODO: Please optimize me.
        string = ""
        while it != it_end:
            string += it[0]
            it += 1
            if len(string) > len(delimiter) and string.endswith(delimiter):
                break

        if it == it_end:
            raise Exception('No terminating delimiter inside raw string literal found!')

    return QuoteToken(start, it, QuoteType.Double, encoding)


def scan_for_quote(it: Iterator, it_end: Iterator):
    token = scan_for_quote_double(it, it_end)
    if not token:
        token = scan_for_quote_single(it, it_end)
    return token
