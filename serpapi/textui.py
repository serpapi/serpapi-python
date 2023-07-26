try:
    import pygments
    from pygments import highlight, lexers, formatters
except ImportError:
    pygments = None


def prettify_json(s):
    if pygments:
        return highlight(
            s,
            lexers.JsonLexer(),
            formatters.TerminalFormatter(),
        )
    else:
        return s
