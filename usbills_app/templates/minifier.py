"""
Template minifier for HTML and CSS content.
"""

# packages
import minify

# set default configuration
minify.config(
    {
        "css-precision": 0,
        "html-keep-comments": False,
        "html-keep-conditional-comments": False,
        "html-keep-default-attr-vals": False,
        "html-keep-document-tags": False,
        "html-keep-end-tags": False,
        "html-keep-whitespace": False,
        "html-keep-quotes": False,
        "js-precision": 0,
        "js-keep-var-names": False,
        "js-version": 0,
        "json-precision": 0,
        "json-keep-numbers": False,
        "svg-keep-comments": False,
        "svg-precision": 0,
        "xml-keep-whitespace": False,
    }
)


def minify_html(html: str) -> str:
    """
    Minify HTML content.

    Args:
        html (str): The HTML content to minify.

    Returns:
        str: The minified HTML content.
    """
    return minify.string("text/html", html)


def minify_css(css: str) -> str:
    """
    Minify CSS content.

    Args:
        css (str): The CSS content to minify.

    Returns:
        str: The minified CSS content.
    """
    return minify.string("text/css", css)
