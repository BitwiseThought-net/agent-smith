"""
title: Web Page Scraper
author: assistant
description: Fetches a web page and returns its cleaned plain-text content so the model can read and analyze it.
version: 0.1.0
"""

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        MAX_CHARS: int = Field(
            default=8000, description="Max characters of page text to return to the model"
        )
        TIMEOUT: int = Field(default=15, description="Request timeout in seconds")

    def __init__(self):
        self.valves = self.Valves()

    def scrape_web_page(self, url: str) -> str:
        """
        Fetch a web page and return its main text content, with scripts, styles,
        and markup stripped out.
        :param url: The full URL of the page to fetch (must start with http:// or https://).
        :return: Cleaned plain-text content of the page, truncated to a safe length.
        """
        if not url.startswith(("http://", "https://")):
            return "Error: url must start with http:// or https://"

        headers = {"User-Agent": "Mozilla/5.0 (compatible; OpenWebUI-Tool/1.0)"}
        try:
            resp = requests.get(url, headers=headers, timeout=self.valves.TIMEOUT)
            resp.raise_for_status()
        except Exception as e:
            return f"Error fetching {url}: {e}"

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
            tag.decompose()

        text = " ".join(soup.get_text(separator=" ").split())
        if len(text) > self.valves.MAX_CHARS:
            text = text[: self.valves.MAX_CHARS] + "... [truncated]"

        title = soup.title.string.strip() if soup.title and soup.title.string else url
        return f"Title: {title}\nSource: {url}\n\n{text}"

