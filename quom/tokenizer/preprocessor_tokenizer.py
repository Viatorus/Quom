from enum import Enum

from .comment_tokenizer import scan_for_comment
from .identifier_tokenizer import scan_for_name
from quom.utils.iterable import Iterator
from .quote_tokenizer import scan_for_quote
from .token import Token, TokenType
from .whitespace_tokenizer import scan_for_whitespace, WhitespaceType


class PreprocessorType(Enum):
    UNDEFINED = 0,
    NULL_DIRECTIVE = 1,
    DEFINE = 2,
    UNDEFINE = 3,
    INCLUDE = 4,
    IF = 5,
    IF_DEFINED = 6,
    IF_NOT_DEFINED = 7,
    ELSE = 8,
    ELSE_IF = 9,
    END_IF = 10,
    LINE = 11,
    ERROR = 12,
    PRAGMA = 13,
    WARNING = 14


class PreprocessorToken(Token):
    def __init__(self, start, end, type: PreprocessorType):
        super().__init__(start, end, TokenType.PREPROCESSOR)
        self.preprocessor_type = type


def skip_whitespace_and_comment(it: Iterator, it_end: Iterator):
    while True:
        comment = scan_for_comment(it, it_end)
        if comment:
            continue
        whitespace = scan_for_whitespace(it, it_end)
        if whitespace:
            if whitespace.whitespace_type == WhitespaceType.LINE_BREAK:
                return True
            continue
        break


def scan_for_line_end(it: Iterator, it_end: Iterator):
    while True:
        if skip_whitespace_and_comment(it, it_end):
            return

        # Todo literal encoding
        if not scan_for_quote(it, it_end):
            it += 1


def scan_for_preprocessor_include(it: Iterator, it_end: Iterator):
    if skip_whitespace_and_comment(it, it_end) or it[0] != '"' and it[0] != '<':
        raise Exception("Expected \"FILENAME\" or <FILENAME> after include!")

    if it[0] == '"':
        it += 1

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

    elif it[0] == '<':
        it += 1

        # Scan until terminating >.
        while it[0] != '\n' and (it[0] != '>'):
            it += 1

        # Check if end of line is reached.
        if it[0] == '\n':
            raise Exception("Character sequence not terminated!")
        it += 1


def scan_for_preprocessor(it: Iterator, it_end: Iterator):
    if it[0] != '#':
        return None
    start = it
    it += 1

    if skip_whitespace_and_comment(it, it_end):
        return PreprocessorToken(start, it, PreprocessorType.NULL_DIRECTIVE)

    # TODO: Not good
    name = scan_for_name(it, it_end)
    if not name:
        raise Exception('Illegal preprocessor instruction.')

    if name in ['if', 'ifdef', 'ifndef', 'elsif', 'pragma', 'warning', 'error', 'line', 'define', 'undef',
                'else', 'endif']:
        scan_for_line_end(it, it_end)
    elif name == 'include':
        scan_for_preprocessor_include(it, it_end)
    else:
        raise Exception('Unknown preprocessor directive.')

    return PreprocessorToken(start, it, PreprocessorType.UNDEFINE)