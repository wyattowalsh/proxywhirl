"""Sphinx configuration for ProxyWhirl documentation."""
from __future__ import annotations

from datetime import datetime
from importlib import metadata
import os
import sys

# -- Path setup ----------------------------------------------------------------

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

# -- Project information -------------------------------------------------------

project = "ProxyWhirl"
try:
    release = metadata.version("proxywhirl")
except metadata.PackageNotFoundError:  # Local builds without install
    release = "1.0.0"
version = release

author = "Wyatt Walsh"
copyright = f"{datetime.now():%Y}, {author}"

html_title = "ProxyWhirl Documentation"
html_baseurl = "https://www.proxywhirl.com/docs/"

# -- General configuration -----------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.duration",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinxcontrib.mermaid",
]

autosummary_generate = True
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_attr_annotations = True

myst_enable_extensions = {
    "attrs_block",
    "colon_fence",
    "deflist",
    "fieldlist",
    "linkify",
    "smartquotes",
    "attrs_inline",
}

myst_heading_anchors = 4
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

exclude_patterns: list[str] = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

templates_path = ["_templates"]

# -- Options for HTML output ---------------------------------------------------

html_theme = "shibuya"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_logo = "_static/logo.svg"
html_favicon = "_static/favicon.svg"

docsearch_app_id = os.getenv("DOCSEARCH_APP_ID")
docsearch_api_key = os.getenv("DOCSEARCH_API_KEY")
docsearch_index_name = os.getenv("DOCSEARCH_INDEX_NAME")

DOCSEARCH_ENABLED = all(
    [docsearch_app_id, docsearch_api_key, docsearch_index_name]
)

if DOCSEARCH_ENABLED:
    extensions.append("sphinx_docsearch")

html_theme_options = {
    "accent_color": "violet",
    "color_mode": "auto",
    "dark_code": True,
    "globaltoc_expand_depth": 2,
    "toctree_titles_only": False,
    "github_url": "https://github.com/wyattowalsh/proxywhirl",
    # TODO: Create og-image.png and uncomment to enable Open Graph image meta tags
    # "og_image_url": "https://proxywhirl.readthedocs.io/_static/og-image.png",
    "twitter_creator": "wyaborern",
    "twitter_site": "wyaborern",
    "light_logo": "_static/logo.svg",
    "dark_logo": "_static/logo.svg",
}

if DOCSEARCH_ENABLED:
    html_theme_options["docsearch"] = {
        "app_id": docsearch_app_id,
        "api_key": docsearch_api_key,
        "index_name": docsearch_index_name,
    }

html_show_sphinx = False
html_show_sourcelink = True

# -- Extension configuration ---------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "fastapi": ("https://fastapi.tiangolo.com", None),
    # httpx doesn't provide a Sphinx objects.inv
    # "httpx": ("https://www.python-httpx.org/", None),
    "pydantic": ("https://docs.pydantic.dev/latest", None),
}

nitpicky = True
nitpick_ignore = [
    ("py:class", "Proxy"),
    ("py:class", "ProxyRotator"),
    ("py:class", "TierType"),
    ("py:class", "Path"),
    ("py:class", "SecretStr"),
]

nitpick_ignore_regex = [
    (r"py:.*", r"proxywhirl\..*"),
    (r"py:.*", r"pydantic\..*"),
]

todo_include_todos = False

# -- Linkcheck configuration ---------------------------------------------------

linkcheck_ignore = [
    r"http://localhost.*",  # Local dev server URLs
    r"http://127\.0\.0\.1.*",  # Local dev server URLs
    r"https://proxywhirl\.com.*",  # Main site (may not be deployed yet)
    r"http://sources\.py",  # False positive: backtick-wrapped sources.py parsed as URL
]
linkcheck_anchors = False  # Don't check anchors (can be slow/flaky)

# -- Mermaid -------------------------------------------------------------------

mermaid_version = "10.9.1"
mermaid_params = ["--theme", "forest"]

# -- Autosummary / Autodoc tweaks ---------------------------------------------

autodoc_typehints = "description"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

def setup(app):  # type: ignore[override]
    """Inject project-wide substitutions and CSS."""
    app.add_config_value("project_root", PROJECT_ROOT, "env")
