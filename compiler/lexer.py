from typing import List
from .tokens import Token, TokenType, KEYWORDS


class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int, lexeme: str = ""):
        self.message = message
        self.line = line
        self.column = column
        self.lexeme = lexeme
        super().__init__(message)

    def diagnostic(self) -> str:
        return (
            f"LEXICAL ERROR\n"
            f"Line: {self.line}, Column: {self.column}\n"
            f"{self.message}"
        )


class Lexer:
    """Manually written character-by-character scanner."""

    SINGLE_CHAR_TOKENS = {
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.MULTIPLY,
        "/": TokenType.DIVIDE,
        "%": TokenType.MODULO,
        "=": TokenType.ASSIGN,
        "(": TokenType.LPAREN,
        ")": TokenType.RPAREN,
        "{": TokenType.LBRACE,
        "}": TokenType.RBRACE,
        ";": TokenType.SEMICOLON,
        ",": TokenType.COMMA,
        "<": TokenType.LESS,
        ">": TokenType.GREATER,
        "!": TokenType.NOT,
    }

    TWO_CHAR_TOKENS = {
        "==": TokenType.EQUAL,
        "!=": TokenType.NOT_EQUAL,
        "<=": TokenType.LESS_EQUAL,
        ">=": TokenType.GREATER_EQUAL,
        "&&": TokenType.AND,
        "||": TokenType.OR,
    }

    def __init__(self, source: str):
        self.source = source
        self.length = len(source)
        self.index = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def _peek(self, offset: int = 0) -> str:
        pos = self.index + offset
        return self.source[pos] if pos < self.length else "\0"

    def _advance(self) -> str:
        ch = self._peek()
        if ch == "\0":
            return ch
        self.index += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _add(self, token_type: TokenType, lexeme: str, line: int, column: int) -> None:
        self.tokens.append(Token(token_type, lexeme, line, column))

    def tokenize(self) -> List[Token]:
        while self._peek() != "\0":
            ch = self._peek()

            if ch.isspace():
                self._advance()
                continue

            # Single-line comment
            if ch == "/" and self._peek(1) == "/":
                while self._peek() not in ("\n", "\0"):
                    self._advance()
                continue

            # Block comment
            if ch == "/" and self._peek(1) == "*":
                start_line, start_col = self.line, self.column
                self._advance()
                self._advance()
                while not (self._peek() == "*" and self._peek(1) == "/"):
                    if self._peek() == "\0":
                        raise LexerError(
                            "Unterminated block comment.",
                            start_line,
                            start_col,
                            "/*"
                        )
                    self._advance()
                self._advance()
                self._advance()
                continue

            start_line, start_col = self.line, self.column

            if ch.isalpha() or ch == "_":
                self._scan_identifier(start_line, start_col)
            elif ch.isdigit():
                self._scan_number(start_line, start_col)
            elif ch == '"':
                self._scan_string(start_line, start_col)
            else:
                pair = ch + self._peek(1)
                if pair in self.TWO_CHAR_TOKENS:
                    self._advance()
                    self._advance()
                    self._add(self.TWO_CHAR_TOKENS[pair], pair, start_line, start_col)
                elif ch in self.SINGLE_CHAR_TOKENS:
                    self._advance()
                    self._add(self.SINGLE_CHAR_TOKENS[ch], ch, start_line, start_col)
                else:
                    raise LexerError(
                        f"Unexpected character {ch!r}.",
                        start_line,
                        start_col,
                        ch
                    )

        self._add(TokenType.EOF, "", self.line, self.column)
        return self.tokens

    def _scan_identifier(self, line: int, column: int) -> None:
        start = self.index
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        lexeme = self.source[start:self.index]
        token_type = KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
        self._add(token_type, lexeme, line, column)

    def _scan_number(self, line: int, column: int) -> None:
        start = self.index
        while self._peek().isdigit():
            self._advance()

        if self._peek() == ".":
            if self._peek(1).isdigit():
                self._advance()
                while self._peek().isdigit():
                    self._advance()
            else:
                raise LexerError(
                    "Malformed floating-point number; digits are required after '.'.",
                    self.line,
                    self.column,
                    self._peek()
                )

        # Reject a numeric identifier such as 123abc.
        if self._peek().isalpha() or self._peek() == "_":
            bad_start = self.index
            while self._peek().isalnum() or self._peek() == "_":
                self._advance()
            bad = self.source[start:self.index]
            raise LexerError(
                f"Invalid numeric lexeme {bad!r}.",
                line,
                column,
                self.source[bad_start:self.index]
            )

        self._add(TokenType.NUMBER, self.source[start:self.index], line, column)

    def _scan_string(self, line: int, column: int) -> None:
        self._advance()  # opening quote
        chars = []
        while self._peek() not in ('"', "\0", "\n"):
            ch = self._advance()
            if ch == "\\":
                nxt = self._peek()
                if nxt == "\0":
                    break
                chars.append(ch)
                chars.append(self._advance())
            else:
                chars.append(ch)

        if self._peek() != '"':
            raise LexerError(
                "Unterminated string literal.",
                line,
                column,
                '"' + "".join(chars)
            )

        self._advance()  # closing quote
        self._add(TokenType.STRING, '"' + "".join(chars) + '"', line, column)
