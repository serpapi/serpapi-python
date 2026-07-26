def prettify_json(s: str) -> str:
    try:
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name #type: ignore
        from pygments.formatters import TerminalFormatter
    except ImportError:
        return s

    return highlight(s, get_lexer_by_name("JSON"), TerminalFormatter())