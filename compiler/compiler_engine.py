from dataclasses import dataclass
from typing import List, Optional
from .lexer import Lexer, LexerError
from .parser import Parser, ParserError
from .tokens import Token, TokenType
from .ast import ASTNode


@dataclass
class CompilationResult:
    status: str
    lexical_passed: bool
    syntax_passed: bool
    tokens: List[Token]
    ast: Optional[ASTNode] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    processed_tokens: int = 0


class CompilerEngine:
    """
    Coordinates the two consecutive compiler phases.

    Phase 1: source text -> Lexer -> Token stream
    Phase 2: Token stream -> Parser -> AST / syntax result
    """

    def analyze(self, source_code: str) -> CompilationResult:
        lexer = Lexer(source_code)

        try:
            tokens = lexer.tokenize()
        except LexerError as error:
            return CompilationResult(
                status="REJECTED",
                lexical_passed=False,
                syntax_passed=False,
                tokens=lexer.tokens,
                error_type="LEXICAL ERROR",
                error_message=error.diagnostic(),
                processed_tokens=len(lexer.tokens),
            )

        # Genuine integration point:
        # The parser receives the exact token stream returned by the lexer.
        parser = Parser(tokens)

        try:
            ast = parser.parse()
            return CompilationResult(
                status="ACCEPTED",
                lexical_passed=True,
                syntax_passed=True,
                tokens=tokens,
                ast=ast,
                processed_tokens=parser.position,
            )
        except ParserError as error:
            return CompilationResult(
                status="REJECTED",
                lexical_passed=True,
                syntax_passed=False,
                tokens=tokens,
                error_type="SYNTAX ERROR",
                error_message=error.diagnostic(),
                processed_tokens=parser.position,
            )

    @staticmethod
    def token_statistics(tokens: List[Token]) -> dict:
        real_tokens = [t for t in tokens if t.type != TokenType.EOF]
        return {
            "Total Tokens": len(real_tokens),
            "Keywords": sum(t.type in {
                TokenType.INT, TokenType.FLOAT, TokenType.CHAR
            } for t in real_tokens),
            "Identifiers": sum(t.type == TokenType.IDENTIFIER for t in real_tokens),
            "Numbers": sum(t.type == TokenType.NUMBER for t in real_tokens),
            "Operators": sum(t.type in {
                TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY,
                TokenType.DIVIDE, TokenType.MODULO, TokenType.ASSIGN,
                TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS,
                TokenType.LESS_EQUAL, TokenType.GREATER,
                TokenType.GREATER_EQUAL, TokenType.AND,
                TokenType.OR, TokenType.NOT
            } for t in real_tokens),
            "Delimiters": sum(t.type in {
                TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE,
                TokenType.RBRACE, TokenType.SEMICOLON, TokenType.COMMA
            } for t in real_tokens),
        }
