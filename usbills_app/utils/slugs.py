"""
Utility functions for generating URL-safe slugs.
"""

# imports
import re

# precompiled regex patterns
RE_SLUGIFY = re.compile(
    r"[^a-z0-9\-\s]"
)  # regex to match non-alphanumeric characters, hyphens, and spaces
RE_WS_TO_DASH = re.compile(r"\s+")  # regex to match whitespace characters
RE_DASH_COLLAPSE = re.compile(r"-+")  # regex to match multiple hyphens


def get_default_slug(
    legis_num: str, title: str, version: str, max_chars: int = 64
) -> str:
    """
    Generate a URL-safe slug from legislation number and title.

    Args:
        legis_num: Legislation number
        title: Bill title
        version: Bill version
        max_chars: Maximum number of characters in the slug

    Returns:
        URL-safe slug for the bill
    """
    # combine legislation number, title, and version into a single string
    combined_string = f"{legis_num}-{title[:max_chars]}-{version}"

    # convert to lowercase and replace periods with hyphens
    slug = combined_string.lower().replace(".", "-")

    # process the slug
    slug = RE_SLUGIFY.sub("", slug)
    slug = RE_WS_TO_DASH.sub("-", slug)
    slug = RE_DASH_COLLAPSE.sub("-", slug)
    slug = slug.strip("-")

    return slug
