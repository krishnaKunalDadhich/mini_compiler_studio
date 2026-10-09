from typing import List
from .tokens import Token, TokenType
from .ast import ASTNode


class ParserError(Exception):
    def __init__(self, message: str, token: Token, expected: str = ""):
        self.message = message
        self.token = token
        self.expected = expected
        super().__init__(message)

    def diagnostic(self) -> str:
        found = self.token.type.name
        detail = (
            f"Expected: {self.expected}\n"
            f"Found: {found} ({self.token.lexeme!r})"
            if self.expected else
            f"Found: {found} ({self.token.lexeme!r})"
        )
        return (
            f"SYNTAX ERROR\n"
            f"Line: {self.token.line}, Column: {self.token.column}\n"
            f"{self.message}\n{detail}"
        )


class Parser:
    """
    Recursive descent parser.
    IMPORTANT: it consumes only the Token objects produced by Lexer.
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.position]

    def _advance(self) -> Token:
        token = self.current
        if self.position < len(self.tokens) - 1:
            self.position += 1
        return token

    def _check(self, token_type: TokenType) -> bool:
        return self.current.type == token_type

    def _match(self, *token_types: TokenType) -> bool:
        if self.current.type in token_types:
            self._advance()
            return True
        return False

    def _expect(self, token_type: TokenType, expected: str = "") -> Token:
        if not self._check(token_type):
            name = expected or token_type.name
            raise ParserError(
                f"Unexpected token while parsing. Expected {name}.",
                self.current,
                name
            )
        return self._advance()

    def parse(self) -> ASTNode:
        root = self.parse_program()
        if not self._check(TokenType.EOF):
            raise ParserError(
                "Unexpected tokens after the end of the program.",
                self.current,
                "EOF"
            )
        return root

    # program -> statement*
    def parse_program(self) -> ASTNode:
        root = ASTNode("PROGRAM")
        while not self._check(TokenType.EOF):
            root.add(self.parse_statement())
        return root

    # statement -> declaration | assignment
    def parse_statement(self) -> ASTNode:
        if self._check(TokenType.INT) or self._check(TokenType.FLOAT) or self._check(TokenType.CHAR):
            return self.parse_declaration()
        if self._check(TokenType.IDENTIFIER):
            return self.parse_assignment()
        raise ParserError(
            "A statement must begin with a data type or identifier.",
            self.current,
            "INT | FLOAT | CHAR | IDENTIFIER"
        )

    # declaration -> datatype IDENTIFIER optional_initialization SEMICOLON
    def parse_declaration(self) -> ASTNode:
        datatype = self.parse_datatype()
        identifier = self._expect(TokenType.IDENTIFIER, "IDENTIFIER")
        node = ASTNode("DECLARATION")
        node.add(ASTNode("TYPE", datatype.lexeme))
        node.add(ASTNode("IDENTIFIER", identifier.lexeme))

        if self._match(TokenType.ASSIGN):
            expr = self.parse_expression()
            node.add(ASTNode("EXPRESSION", children=[expr]))

        self._expect(TokenType.SEMICOLON, "SEMICOLON ';'")
        return node

    # assignment -> IDENTIFIER ASSIGN expression SEMICOLON
    def parse_assignment(self) -> ASTNode:
        identifier = self._expect(TokenType.IDENTIFIER, "IDENTIFIER")
        self._expect(TokenType.ASSIGN, "ASSIGN '='")
        expr = self.parse_expression()
        self._expect(TokenType.SEMICOLON, "SEMICOLON ';'")

        node = ASTNode("ASSIGNMENT")
        node.add(ASTNode("IDENTIFIER", identifier.lexeme))
        node.add(ASTNode("EXPRESSION", children=[expr]))
        return node

    # datatype -> INT | FLOAT | CHAR
    def parse_datatype(self) -> Token:
        if self.current.type in (TokenType.INT, TokenType.FLOAT, TokenType.CHAR):
            return self._advance()
        raise ParserError(
            "Invalid data type.",
            self.current,
            "INT | FLOAT | CHAR"
        )

    # expression -> term ((PLUS | MINUS) term)*
    def parse_expression(self) -> ASTNode:
        node = self.parse_term()
        while self._check(TokenType.PLUS) or self._check(TokenType.MINUS):
            operator = self._advance()
            right = self.parse_term()
            node = ASTNode(
                "BINARY OPERATION",
                operator.lexeme,
                [node, right]
            )
        return node

    # term -> factor ((MULTIPLY | DIVIDE | MODULO) factor)*
    def parse_term(self) -> ASTNode:
        node = self.parse_factor()
        while self.current.type in (
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
            TokenType.MODULO
        ):
            operator = self._advance()
            right = self.parse_factor()
            node = ASTNode(
                "BINARY OPERATION",
                operator.lexeme,
                [node, right]
            )
        return node

    # factor -> NUMBER | IDENTIFIER | LPAREN expression RPAREN
    def parse_factor(self) -> ASTNode:
        if self._check(TokenType.NUMBER):
            return ASTNode("NUMBER", self._advance().lexeme)

        if self._check(TokenType.IDENTIFIER):
            return ASTNode("IDENTIFIER", self._advance().lexeme)

        if self._match(TokenType.LPAREN):
            expression = self.parse_expression()
            self._expect(TokenType.RPAREN, "RPAREN ')'")
            return ASTNode("PARENTHESIZED EXPRESSION", children=[expression])

        if self._check(TokenType.STRING):
            raise ParserError(
                "String literals are lexically recognized but are not part of the expression grammar.",
                self.current,
                "NUMBER | IDENTIFIER | '(' expression ')'"
            )

        raise ParserError(
            "Expected an expression factor.",
            self.current,
            "NUMBER | IDENTIFIER | '(' expression ')'"
        )
