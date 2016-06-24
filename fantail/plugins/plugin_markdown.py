"""
Markdown content filter
Requires mistune: https://pypi.python.org/pypi/mistune/
"""

try:
    import mistune
except ImportError:
    import logging
    logging.warning('This plugin requires the `mistune` library. You can install it:')
    logging.warning('  $ pip install mistune')
else:
    def register_markdown_filter(content):
        # don't escape HTML
        return mistune.markdown(content, escape=False)

    register_markdown_filter.plugin_type = 'filter'
