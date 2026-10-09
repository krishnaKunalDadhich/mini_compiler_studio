import streamlit as st
from compiler.compiler_engine import CompilerEngine
from compiler.tokens import TokenType
from ui.styles import inject_css

st.set_page_config(
    page_title="Mini Compiler Studio",
    page_icon="⌘",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

EXAMPLES = {
    "Valid Declaration": """int x = 10;""",
    "Valid Arithmetic": """int x = 10;
int y = 5;
int result = x + y * 2;""",
    "Multiple Statements": """int x = 10;
float price = 25.5;
int total = x + 20;
total = total * 2;""",
    "Parentheses & Precedence": """int result = (10 + 20) * 2;
int answer = 10 + 5 * 2;""",
    "Syntax Error": """int = 10;""",
    "Missing Semicolon": """int total = 10 + 20""",
    "Lexical Error": """int x = 10 @ 5;""",
}

DEFAULT_SOURCE = EXAMPLES["Multiple Statements"]

if "source_code" not in st.session_state:
    st.session_state.source_code = DEFAULT_SOURCE
if "analysis" not in st.session_state:
    st.session_state.analysis = None


def phase_card(number, title, desc):
    st.markdown(
        f"""
        <div class="phase-card">
            <div class="phase-number">Phase {number}</div>
            <div class="phase-title">{title}</div>
            <div class="phase-desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="hero">
        <h1>⌘ Mini Compiler Studio</h1>
        <p>An Interactive Compiler Front-End Demonstrating Integrated Lexical and Syntax Analysis</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "College-level Compiler Design Lab Project • Python 3 • Manual Scanner • Recursive Descent Parser"
)

# Pipeline
c1, a1, c2, a2, c3, a3, c4 = st.columns([1.8, .35, 1.8, .35, 1.8, .35, 1.8])
with c1:
    phase_card("Input", "Source Code", "Program text")
with a1:
    st.markdown("<div style='padding-top:2.6rem;text-align:center;font-size:1.5rem'>→</div>", unsafe_allow_html=True)
with c2:
    phase_card("1", "Lexical Analysis", "Characters → tokens")
with a2:
    st.markdown("<div style='padding-top:2.6rem;text-align:center;font-size:1.5rem'>→</div>", unsafe_allow_html=True)
with c3:
    phase_card("2", "Syntax Analysis", "Tokens → AST")
with a3:
    st.markdown("<div style='padding-top:2.6rem;text-align:center;font-size:1.5rem'>→</div>", unsafe_allow_html=True)
with c4:
    phase_card("Output", "Final Result", "Accept / reject")

st.divider()

left, right = st.columns([1.35, 1])

with left:
    st.subheader("Source Code Editor")
    st.session_state.source_code = st.text_area(
        "Mini-language source",
        value=st.session_state.source_code,
        height=330,
        label_visibility="collapsed",
        placeholder="Write a program such as:\nint x = 10;\nint result = x + 20;",
    )

with right:
    st.subheader("Examples")
    selected = st.selectbox("Load a ready-made test case", list(EXAMPLES.keys()))
    if st.button("Load Example", use_container_width=True):
        st.session_state.source_code = EXAMPLES[selected]
        st.rerun()

    st.markdown("**Supported grammar**")
    st.code(
        """program     → statement*
statement   → declaration | assignment
declaration → datatype IDENTIFIER (= expression)? ;
assignment  → IDENTIFIER = expression ;
expression  → term ((+ | -) term)*
term        → factor ((* | / | %) factor)*
factor      → NUMBER | IDENTIFIER | ( expression )""",
        language="text",
    )

    b1, b2 = st.columns(2)
    with b1:
        if st.button("Analyze Program", type="primary", use_container_width=True):
            st.session_state.analysis = CompilerEngine().analyze(
                st.session_state.source_code
            )
    with b2:
        if st.button("Clear", use_container_width=True):
            st.session_state.source_code = ""
            st.session_state.analysis = None
            st.rerun()

if st.session_state.analysis is not None:
    result = st.session_state.analysis
    st.divider()
    st.subheader("Analysis Result")

    if result.status == "ACCEPTED":
        st.markdown(
            '<div class="status-ok">✓ PROGRAM ACCEPTED — Lexical Analysis PASSED • Syntax Analysis PASSED</div>',
            unsafe_allow_html=True,
        )
    elif result.error_type == "LEXICAL ERROR":
        st.markdown(
            '<div class="status-bad">✗ PROGRAM REJECTED — Lexical Analysis FAILED • Syntax Analysis NOT STARTED</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-bad">✗ PROGRAM REJECTED — Lexical Analysis PASSED • Syntax Analysis FAILED</div>',
            unsafe_allow_html=True,
        )

    st.write("")

    m = result
    stats = CompilerEngine.token_statistics(result.tokens)
    cols = st.columns(5)
    for col, (label, value) in zip(cols, stats.items()):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{value}</div>'
                f'<div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Token Stream", "Syntax / AST", "Diagnostics", "Phase Data Flow"]
    )

    with tab1:
        st.markdown("### Lexer Output → Parser Input")
        rows = []
        for i, token in enumerate(result.tokens, start=1):
            if token.type == TokenType.EOF:
                continue
            rows.append({
                "No.": i,
                "Lexeme": token.lexeme,
                "Token Type": token.type.name,
                "Line": token.line,
                "Column": token.column,
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)

        if result.lexical_passed:
            st.success(
                f"Token stream generated successfully. {len(result.tokens) - 1} "
                "tokens are available to the parser."
            )

    with tab2:
        st.markdown("### Recursive Descent Parser Output")
        if result.syntax_passed and result.ast:
            st.success("Syntax accepted and AST generated.")
            st.code(result.ast.pretty(), language="text")
            st.markdown("**Precedence demonstration:** multiplication/division/modulus are parsed inside `term()` before addition/subtraction in `expression()`.")
        elif result.error_type == "SYNTAX ERROR":
            st.error("No final AST was produced because syntax analysis failed.")

    with tab3:
        if result.error_message:
            st.code(result.error_message, language="text")
        else:
            st.success("No errors detected.")
            st.info("All tokens were consumed according to the grammar.")

    with tab4:
        st.markdown("### Genuine compiler-phase integration")
        st.code(
            """SOURCE CODE
    │
    ▼
CompilerEngine.analyze()
    │
    ▼
Lexer.tokenize()
    │
    ├── lexical error ──► reject
    │
    ▼
List[Token]
    │
    │  SAME TOKEN OBJECTS
    ▼
Parser(tokens)
    │
    ├── syntax error ───► reject
    │
    ▼
AST / Parse Tree
    │
    ▼
PROGRAM ACCEPTED""",
            language="text",
        )
        st.info(
            "The parser does not receive source_code. It receives the exact token list "
            "returned by Lexer.tokenize(). This is the central integration point."
        )

with st.expander("Supported Tokens"):
    st.write(
        "Keywords: int, float, char • Identifiers • Numbers • String literals "
        "(lexically recognized) • + - * / % = == != < <= > >= && || ! "
        "• parentheses • braces • semicolon • comma • // and /* */ comments"
    )
    st.warning(
        "The current syntax grammar intentionally accepts declarations, assignments, "
        "and arithmetic expressions only. Some lexically valid constructs are therefore "
        "rejected by the parser."
    )
