"""Sphinx configuration for local builds and Read the Docs."""

import os

import serpapi

project = "serpapi"
copyright = "2026 SerpApi, LLC"
author = "SerpApi, LLC"
release = serpapi.__version__
version = release

extensions = ["sphinx.ext.autodoc", "myst_parser", "sphinx_design"]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
root_doc = "index"
exclude_patterns = ["_build", "build", "Thumbs.db", ".DS_Store"]
myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 3
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "imported-members": True,
    "exclude-members": "HTTPClient, from_http_response",
}

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_logo = "../assets/serpapi-logo.svg"
html_favicon = "../assets/serpapi-icon.png"
html_theme_options = {
    "logo_only": True,
    "style_nav_header_background": "#2b2145",
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 3,
    "titles_only": True,
}
html_baseurl = os.environ.get(
    "READTHEDOCS_CANONICAL_URL", "https://serpapi-python.readthedocs.io/en/latest/"
)
