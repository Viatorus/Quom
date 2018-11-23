from enum import Enum
from typing import List

from .comment_tokenizer import scan_for_comment
from .iterator import LineWrapIterator
from .number_tokenizer import scan_for_number
from .quote_tokenizer import scan_for_quote
from .remaining_tokenizer import scan_for_remaining
from .token import Token, TokenType
from .tokenize_error import TokenizeError
from .whitespace_tokenizer import scan_for_whitespace, WhitespaceType


class PreprocessorType(Enum):
    UNKNOWN = 0,
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
    def __init__(self, start, end, preprocessor_type: PreprocessorType, tokens: List[Token]):
        super().__init__(start, end, TokenType.PREPROCESSOR)
        self.preprocessor_type = preprocessor_type
        self.preprocessor_tokens = tokens


def scan_for_whitespaces_and_comments(tokens: List[Token], it: LineWrapIterator):
    while it.curr != '\0':
        if scan_for_comment(tokens, it):
            continue
        if scan_for_whitespace(tokens, it):
            if tokens[-1].whitespace_type == WhitespaceType.LINE_BREAK:
                return True
            continue
        break
    return it.curr == '\0'


def scan_for_line_end(tokens: List[Token], it: LineWrapIterator):
    while it.curr != '\0':
        if scan_for_whitespaces_and_comments(tokens, it):
            return
        succeeded = scan_for_quote(tokens, it)
        if not succeeded:
            succeeded = scan_for_number(tokens, it)
        if not succeeded:
            scan_for_remaining(tokens, it)


def scan_for_preprocessor_include(tokens: List[Token], it: LineWrapIterator):
    if scan_for_whitespaces_and_comments(tokens, it) or it.curr != '"' and it.curr != '<':
        raise TokenizeError("Expected \"FILENAME\" or <FILENAME> after include!", it)

    it = LineWrapIterator(it)

    if it.curr == '"':
        # Parse until non escaped ".
        backslashes = 0
        while it.next() and it.curr != '\n' and (it.curr != '"' or backslashes % 2 != 0):
            if it.curr == '\\':
                backslashes += 1
            else:
                backslashes = 0

        # Check if end of line is reached.
        if it.curr != '"':
            raise TokenizeError("Character sequence not terminated!", it)
        it.next()

    elif it.curr == '<':
        # Scan until terminating >.
        while it.next() and it.curr != '\n' and it.curr != '>':
            pass

        # Check if end of line is reached.
        if it.curr != '>':
            raise TokenizeError("Character sequence not terminated!", it)
        it.next()


def scan_for_preprocessor(tokens: List[Token], it: LineWrapIterator):
    if it.curr != '#':
        return None
    start = it.copy()
    it.next()

    preprocessor_tokens = []
    if scan_for_whitespaces_and_comments(preprocessor_tokens, it):
        tokens.append(PreprocessorToken(start, it, PreprocessorType.NULL_DIRECTIVE, preprocessor_tokens))
        return True

    scan_for_remaining(preprocessor_tokens, it)
    name = ''.join(preprocessor_tokens[-1].span)

    preprocessor_type = PreprocessorType.UNKNOWN

    if name == 'include':
        scan_for_preprocessor_include(preprocessor_tokens, it)
        preprocessor_type = PreprocessorType.INCLUDE
    scan_for_line_end(preprocessor_tokens, it)

    tokens.append(PreprocessorToken(start, it, preprocessor_type, preprocessor_tokens))
    return True
