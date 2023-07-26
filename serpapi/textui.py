from pygments import highlight, lexers, formatters


def prettify_json(s):
    return highlight(
        s,
        lexers.JsonLexer(),
        formatters.TerminalFormatter(),
    )
