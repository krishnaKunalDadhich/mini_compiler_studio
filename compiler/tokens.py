from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Keywords
    INT = auto()
    FLOAT = auto()
    CHAR = auto()

    # General values
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    COMMA = auto()

    EOF = auto()


KEYWORDS = {
    "int": TokenType.INT,
    "float": TokenType.FLOAT,
    "char": TokenType.CHAR,
}


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int

    @property
    def token_type(self) -> str:
        return self.type.name

    def __str__(self) -> str:
        return f"{self.type.name}({self.lexeme!r}) at {self.line}:{self.column}"
