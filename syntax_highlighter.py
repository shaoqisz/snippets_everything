
import re

from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat, QFont
from PyQt5.QtCore import Qt


def format(color, style=''):
    _color = QColor()
    if type(color) is not str:
        _color.setRgb(color[0], color[1], color[2])
    else:
        _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


STYLES = {
    'keyword': format([200, 120, 50], 'bold'),
    'operator': format([150, 150, 150]),
    'brace': format('darkGray'),
    'defclass': format([128, 0, 128], 'bold'),
    'string': format([20, 110, 100]),
    'comment': format([70, 70, 70], 'italic'),
    'self': format([150, 85, 140], 'italic'),
    'numbers': format([100, 150, 190]),
    'placeholder': format([255, 0, 255], 'bold') # magenta
}



class PythonHighlighter(QSyntaxHighlighter):
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]

    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<', 
        # other
        '#'
    ]

    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        rules = []

        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in PythonHighlighter.braces]

        rules += [
            (r'\bself\b', 0, STYLES['self']),
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),
            (r'#[^\n]*', 0, STYLES['comment']),
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
            (r'\$\w+', 0, STYLES['placeholder'])
        ]

        rules += [
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),
        ]

        self.rules = [(re.compile(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        for expression, nth, format in self.rules:
            index = expression.search(text)
            while index:
                length = index.end(nth) - index.start(nth)
                self.setFormat(index.start(nth), length, format)
                index = expression.search(text, index.end(nth))
        self.setCurrentBlockState(0)




class CppHighlighter(QSyntaxHighlighter):
    keywords = [
        'alignas', 'alignof', 'and', 'and_eq', 'asm', 'atomic_cancel',
        'atomic_commit', 'atomic_noexcept', 'auto', 'bitand', 'bitor',
        'bool', 'break', 'case', 'catch', 'char', 'char8_t', 'char16_t',
        'char32_t', 'class', 'compl', 'concept', 'const', 'consteval',
        'constexpr', 'constinit', 'const_cast', 'continue', 'co_await',
        'co_return', 'co_yield', 'decltype', 'default', 'delete', 'do',
        'double', 'dynamic_cast', 'else', 'enum', 'explicit', 'export',
        'extern', 'false', 'float', 'for', 'friend', 'goto', 'if',
        'inline', 'int', 'long', 'mutable', 'namespace', 'new', 'noexcept',
        'not', 'not_eq', 'nullptr', 'operator', 'or', 'or_eq', 'private',
        'protected', 'public', 'reflexpr', 'register', 'reinterpret_cast',
        'requires', 'return', 'short', 'signed', 'sizeof', 'static',
        'static_assert', 'static_cast', 'struct', 'switch', 'synchronized',
        'template', 'this', 'thread_local', 'throw', 'true', 'try', 'typedef',
        'typeid', 'typename', 'union', 'unsigned', 'using', 'virtual', 'void',
        'volatile', 'wchar_t', 'while', 'xor', 'xor_eq', 'include'
    ]

    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        rules = []

        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in CppHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in CppHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in CppHighlighter.braces]

        rules += [
            (r'//[^\n]*', 0, STYLES['comment']),
            (r'/\*.*?\*/', 0, STYLES['comment']),
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
            (r'\$\w+', 0, STYLES['placeholder'])
        ]

        self.rules = [(re.compile(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        for expression, nth, format in self.rules:
            index = expression.search(text)
            while index:
                length = index.end(nth) - index.start(nth)
                self.setFormat(index.start(nth), length, format)
                index = expression.search(text, index.end(nth))
        self.setCurrentBlockState(0)


class PlainTextHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)
        self.rules = [(re.compile(r'\$\w+'), 0, STYLES['placeholder'])]

    def highlightBlock(self, text):
        for expression, nth, format in self.rules:
            index = expression.search(text)
            while index:
                length = index.end(nth) - index.start(nth)
                self.setFormat(index.start(nth), length, format)
                index = expression.search(text, index.end(nth))
        self.setCurrentBlockState(0)
