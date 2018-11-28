from typing import List

import pytest

from quom.tokenizer import tokenize, TokenizeError, Token
from quom.tokenizer import CommentToken, CppCommentToken, CCommentToken, NumberToken, PreprocessorToken, \
    PreprocessorIncludeToken, QuoteToken, SingleQuoteToken, DoubleQuoteToken, RemainingToken, WhitespaceToken, \
    WhitespaceWhitespaceToken, LinebreakWhitespaceToken


def check_tokens(tokens: List[Token], res):
    res = [Token] + res + [Token]

    for token, token_type in zip(tokens, res):
        assert isinstance(token, token_type)


def test_comments_cpp_style():
    tokens = tokenize('//abc')
    check_tokens(tokens, [CppCommentToken])
    check_tokens(tokens, [CommentToken])
    assert str(tokens[1]) == '//abc'

    tokens = tokenize(' //abc\n')
    check_tokens(tokens, [WhitespaceWhitespaceToken, CppCommentToken, LinebreakWhitespaceToken])
    assert str(tokens[2]) == '//abc'

    tokens = tokenize('//abc \\\n \\b')
    check_tokens(tokens, [CppCommentToken])


def test_comments_c_style():
    tokens = tokenize('/*ab*/')
    check_tokens(tokens, [CCommentToken])
    check_tokens(tokens, [CommentToken])
    assert str(tokens[1]) == '/*ab*/'

    tokens = tokenize(' /*ab*/ ')
    check_tokens(tokens, [WhitespaceWhitespaceToken, CCommentToken, WhitespaceWhitespaceToken])
    assert str(tokens[2]) == '/*ab*/'

    tokens = tokenize('/*ab\n*/')
    check_tokens(tokens, [CCommentToken])

    tokens = tokenize('/*ab\\\n*/')
    check_tokens(tokens, [CCommentToken])

    tokens = tokenize('/*ab\\b*/')
    check_tokens(tokens, [CCommentToken])

    with pytest.raises(TokenizeError):
        tokenize('/*a')

    with pytest.raises(TokenizeError):
        tokenize('/*a*')

    with pytest.raises(TokenizeError):
        tokenize('/*a* /')


def test_whitespace():
    tokens = tokenize(' ')
    check_tokens(tokens, [WhitespaceWhitespaceToken])
    check_tokens(tokens, [WhitespaceToken])

    tokens = tokenize(' \t')
    check_tokens(tokens, [WhitespaceWhitespaceToken])

    tokens = tokenize('\t')
    check_tokens(tokens, [WhitespaceWhitespaceToken])

    tokens = tokenize('\v')
    check_tokens(tokens, [WhitespaceWhitespaceToken])

    tokens = tokenize('\f')
    check_tokens(tokens, [WhitespaceWhitespaceToken])

    tokens = tokenize('\r')
    check_tokens(tokens, [LinebreakWhitespaceToken])
    check_tokens(tokens, [WhitespaceToken])

    tokens = tokenize('\n')
    check_tokens(tokens, [LinebreakWhitespaceToken])

    tokens = tokenize('\r\n')
    check_tokens(tokens, [LinebreakWhitespaceToken])

    tokens = tokenize('\r\n\r')
    check_tokens(tokens, [LinebreakWhitespaceToken, LinebreakWhitespaceToken])

    tokens = tokenize('\r\n\n')
    check_tokens(tokens, [LinebreakWhitespaceToken, LinebreakWhitespaceToken])

    tokens = tokenize('\r\n\r\n\n')
    check_tokens(tokens, [LinebreakWhitespaceToken, LinebreakWhitespaceToken, LinebreakWhitespaceToken])

    tokens = tokenize('\n\r\r')
    check_tokens(tokens, [LinebreakWhitespaceToken, LinebreakWhitespaceToken, LinebreakWhitespaceToken])

    tokens = tokenize(' \n ')
    check_tokens(tokens, [WhitespaceWhitespaceToken, LinebreakWhitespaceToken, WhitespaceWhitespaceToken])


def test_quote_single():
    tokens = tokenize('\'abc\'')
    check_tokens(tokens, [SingleQuoteToken])
    check_tokens(tokens, [QuoteToken])
    assert str(tokens[1]) == '\'abc\''

    tokens = tokenize(' \'abc\' ')
    check_tokens(tokens, [WhitespaceWhitespaceToken, SingleQuoteToken, WhitespaceWhitespaceToken])
    assert str(tokens[2]) == '\'abc\''

    tokens = tokenize('\'a\\bc\'')
    check_tokens(tokens, [SingleQuoteToken])

    tokens = tokenize('\'a\\\'bc\'')
    check_tokens(tokens, [SingleQuoteToken])

    with pytest.raises(TokenizeError):
        tokenize('\'a')

    with pytest.raises(TokenizeError):
        tokenize('\'')


def test_quote_double():
    tokens = tokenize('"abc"')
    check_tokens(tokens, [DoubleQuoteToken])
    check_tokens(tokens, [QuoteToken])
    assert str(tokens[1]) == '"abc"'

    tokens = tokenize(' "abc" ')
    check_tokens(tokens, [WhitespaceWhitespaceToken, DoubleQuoteToken, WhitespaceWhitespaceToken])
    assert str(tokens[2]) == '"abc"'

    tokens = tokenize('"abc\\""')
    check_tokens(tokens, [DoubleQuoteToken])
    assert str(tokens[1]) == '"abc\\""'

    tokens = tokenize('R"(abc)"')
    check_tokens(tokens, [RemainingToken, DoubleQuoteToken])
    assert str(tokens[2]) == '"(abc)"'

    tokens = tokenize('R"(a\b\\r\\abc)"')
    check_tokens(tokens, [RemainingToken, DoubleQuoteToken])
    assert str(tokens[2]) == '"(a\b\\r\\abc)"'

    tokens = tokenize('R"1=#(abc)1=#abc)1=#"')
    check_tokens(tokens, [RemainingToken, DoubleQuoteToken])
    assert tokens[2].is_raw_encoding

    tokens = tokenize('u8R"(abc)"')
    check_tokens(tokens, [RemainingToken, DoubleQuoteToken])
    assert tokens[2].is_raw_encoding

    tokens = tokenize('uR"(abc)"')
    check_tokens(tokens, [RemainingToken, DoubleQuoteToken])
    assert tokens[2].is_raw_encoding

    tokens = tokenize('UR"(a)bc)"')
    check_tokens(tokens, [RemainingToken, DoubleQuoteToken])
    assert tokens[2].is_raw_encoding

    tokens = tokenize('LR"=(a)bc)="')
    check_tokens(tokens, [RemainingToken, DoubleQuoteToken])
    assert tokens[2].is_raw_encoding

    tokens = tokenize('u"abc"')
    check_tokens(tokens, [RemainingToken, DoubleQuoteToken])

    tokens = tokenize('u8"abc"')
    check_tokens(tokens, [RemainingToken, DoubleQuoteToken])

    tokens = tokenize('U"abc"')
    check_tokens(tokens, [RemainingToken, DoubleQuoteToken])

    tokens = tokenize('L"abc"')
    check_tokens(tokens, [RemainingToken, DoubleQuoteToken])

    with pytest.raises(TokenizeError):
        tokenize('"a')

    with pytest.raises(TokenizeError):
        tokenize('a"a')

    with pytest.raises(TokenizeError):
        tokenize('R"a"')

    with pytest.raises(TokenizeError):
        tokenize('R"(a"')


def test_number():
    tokens = tokenize('0')
    check_tokens(tokens, [NumberToken])
    assert str(tokens[1]) == '0'

    tokens = tokenize('123')
    check_tokens(tokens, [NumberToken])
    assert str(tokens[1]) == '123'

    tokens = tokenize('1\'23')
    check_tokens(tokens, [NumberToken])
    assert str(tokens[1]) == '1\'23'

    tokens = tokenize(' 1234567890 ')
    check_tokens(tokens, [WhitespaceWhitespaceToken, NumberToken, WhitespaceWhitespaceToken])
    assert str(tokens[2]) == "1234567890"

    tokens = tokenize("001.1")
    check_tokens(tokens, [NumberToken])

    tokens = tokenize("001e1")
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0x')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('1xx13b')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize(".1")
    check_tokens(tokens, [NumberToken])
    assert str(tokens[1]) == ".1"

    tokens = tokenize('.123')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('123.345')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('123.345e3')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('123e+4')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('123e-4')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('12\'3.345')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('01e1')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('01.1')
    check_tokens(tokens, [NumberToken])

    with pytest.raises(TokenizeError):
        tokenize('12\'')

    tokens = tokenize('0x1')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0xFp1')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0x02\'3')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0x023p+1')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0xABCDEFabcdef')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0x0.123p-1')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0x0.e2\'3p-1\'0')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0x0.p1')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0xa.Ap1')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0xA.ap1')
    check_tokens(tokens, [NumberToken])

    with pytest.raises(TokenizeError):
        tokenize('0x12\'')

    tokens = tokenize('0x0.123')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0x0.123p-A')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0b1')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0b01')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0b010101')
    check_tokens(tokens, [NumberToken])

    with pytest.raises(TokenizeError):
        tokenize('0b01\'')

    tokens = tokenize('01')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0\'1')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0012345\'67')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('01x')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('0012345\'68')
    check_tokens(tokens, [NumberToken])

    tokens = tokenize('12\'d.z\'.x1.\'1')
    check_tokens(tokens, [NumberToken])


def test_preprocessor():
    tokens = tokenize("#")
    check_tokens(tokens, [PreprocessorToken])

    tokens = tokenize("#\n ")
    check_tokens(tokens, [PreprocessorToken, WhitespaceWhitespaceToken])

    tokens = tokenize("# /**/\n")
    check_tokens(tokens, [PreprocessorToken])

    tokens = tokenize("#pragma")
    check_tokens(tokens, [PreprocessorToken])

    tokens = tokenize(" #pragma")
    check_tokens(tokens, [WhitespaceWhitespaceToken, PreprocessorToken])

    tokens = tokenize('#define')
    check_tokens(tokens, [PreprocessorToken])

    tokens = tokenize('#include "abc" ')
    check_tokens(tokens, [PreprocessorToken])
    check_tokens(tokens, [PreprocessorIncludeToken])

    tokens = tokenize('#include "abc\\"" ')
    check_tokens(tokens, [PreprocessorToken])

    tokens = tokenize('#include /*123*/ <abc> ')
    check_tokens(tokens, [PreprocessorToken])

    tokens = tokenize('#define a(x) auto a##x = #x')
    check_tokens(tokens, [PreprocessorToken])

    tokens = tokenize('#define eprintf(format, ...) fprintf (stderr, format, __VA_ARGS__)')
    check_tokens(tokens, [PreprocessorToken])

    tokens = tokenize('# /* abc */ define  /* test */')
    check_tokens(tokens, [PreprocessorToken])

    with pytest.raises(TokenizeError):
        tokenize('#include "abc\\" ')

    with pytest.raises(TokenizeError):
        tokenize('#include <abc')

    with pytest.raises(TokenizeError):
        tokenize('#include ')


def test_remaining():
    tokens = tokenize('abc')
    check_tokens(tokens, [RemainingToken])
    assert str(tokens[1]) == 'abc'

    tokens = tokenize('abc ')
    check_tokens(tokens, [RemainingToken, WhitespaceWhitespaceToken])
    assert str(tokens[1]) == 'abc'

    tokens = tokenize(' abc ')
    check_tokens(tokens, [WhitespaceWhitespaceToken, RemainingToken, WhitespaceWhitespaceToken])
    assert str(tokens[2]) == 'abc'

    tokens = tokenize('_ab_c')
    check_tokens(tokens, [RemainingToken])
    assert str(tokens[1]) == '_ab_c'

    for symbol in "+-*/%<>&!=?.,[]{}():|;~^":
        tokens = tokenize(symbol)
        check_tokens(tokens, [RemainingToken])

    tokens = tokenize('kwqjj8a8gja98gj9\b\1\¹23')
    check_tokens(tokens, [RemainingToken])
