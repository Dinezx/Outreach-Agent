from __future__ import annotations

import pytest
from leadminerai.services.html_service import HTMLService


def test_clean_html_strips_unwanted_elements():
    html = """
    <html>
      <head><title>Test Title</title></head>
      <body>
        <script>console.log("hello");</script>
        <style>body { color: red; }</style>
        <h1>Welcome</h1>
        <p>This is a test <a href="/contact">contact page</a>.</p>
        <svg><path d="M10 10"/></svg>
      </body>
    </html>
    """
    cleaned = HTMLService.clean_html(html)
    assert "Welcome" in cleaned
    assert "This is a test" in cleaned
    assert "[Link: contact page](/contact)" in cleaned
    assert "console.log" not in cleaned
    assert "color: red" not in cleaned


def test_clean_html_empty_input():
    assert HTMLService.clean_html("") == ""
    assert HTMLService.clean_html(None) == ""


def test_extract_links():
    html = """
    <div>
      <a href="/contact">Contact</a>
      <a href="https://example.com/about?ref=123">About</a>
      <a href="https://example.com/about">Duplicate About</a>
      <a href="">Empty Link</a>
    </div>
    """
    links = HTMLService.extract_links(html, "https://example.com")
    assert links == [
        "https://example.com/contact",
        "https://example.com/about",
    ]
