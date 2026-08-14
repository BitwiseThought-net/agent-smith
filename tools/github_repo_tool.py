"""
title: GitHub Repository Reader
author: assistant
description: Given a public GitHub repository URL, fetches its file tree and the contents of its key text files so the model can analyze the codebase.
version: 0.1.0
"""

import re
import requests
from pydantic import BaseModel, Field

SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "vendor",
    "__pycache__", ".venv", "venv", ".idea", ".vscode",
}
SKIP_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", ".bmp",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".mp4", ".mp3", ".mov", ".avi", ".zip", ".tar", ".gz", ".7z",
    ".pdf", ".lock", ".min.js", ".min.css",
    ".pyc", ".so", ".dll", ".exe", ".bin",
}


class Tools:
    class Valves(BaseModel):
        GITHUB_TOKEN: str = Field(
            default="",
            description="Optional GitHub personal access token, raises the API rate limit "
            "from 60/hr to 5000/hr and allows access to private repos you own.",
        )
        MAX_FILES: int = Field(default=40, description="Max number of files to include")
        MAX_FILE_CHARS: int = Field(default=4000, description="Max characters read per file")
        MAX_TOTAL_CHARS: int = Field(default=30000, description="Max total characters returned")

    def __init__(self):
        self.valves = self.Valves()

    def _headers(self):
        h = {"Accept": "application/vnd.github+json", "User-Agent": "OpenWebUI-Tool"}
        if self.valves.GITHUB_TOKEN:
            h["Authorization"] = f"Bearer {self.valves.GITHUB_TOKEN}"
        return h

    def _parse_repo_url(self, url: str):
        m = re.search(r"github\.com/([^/]+)/([^/#?]+)", url)
        if not m:
            return None, None, None
        owner, repo = m.group(1), m.group(2).replace(".git", "")
        branch_match = re.search(r"github\.com/[^/]+/[^/]+/tree/([^/]+)", url)
        branch = branch_match.group(1) if branch_match else None
        return owner, repo, branch

    def read_github_repository(self, repo_url: str) -> str:
        """
        Fetch a public GitHub repository's file tree and the contents of its
        source files so they can be analyzed and summarized.
        :param repo_url: The full GitHub repository URL, e.g. https://github.com/owner/repo
        :return: A text digest with the filtered file tree plus the contents of key files, truncated to a safe length.
        """
        owner, repo, branch = self._parse_repo_url(repo_url)
        if not owner or not repo:
            return f"Could not parse a GitHub owner/repo from: {repo_url}"

        try:
            if not branch:
                r = requests.get(
                    f"https://api.github.com/repos/{owner}/{repo}",
                    headers=self._headers(), timeout=15,
                )
                if r.status_code != 200:
                    return f"Error fetching repo metadata ({r.status_code}): {r.text[:300]}"
                branch = r.json().get("default_branch", "main")

            tree_resp = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
                headers=self._headers(), timeout=20,
            )
            if tree_resp.status_code != 200:
                return f"Error fetching repo tree ({tree_resp.status_code}): {tree_resp.text[:300]}"

            tree = tree_resp.json().get("tree", [])
        except Exception as e:
            return f"Error contacting GitHub API: {e}"

        files = []
        for item in tree:
            if item.get("type") != "blob":
                continue
            path = item["path"]
            if any(f"/{d}/" in f"/{path}/" for d in SKIP_DIRS):
                continue
            if any(path.lower().endswith(ext) for ext in SKIP_EXTS):
                continue
            if item.get("size", 0) > 200_000:
                continue
            files.append(path)

        file_tree_text = "\n".join(sorted(files)[:300])
        digest = [
            f"Repository: {owner}/{repo} (branch: {branch})",
            "",
            "File tree (filtered):",
            file_tree_text,
            "",
        ]

        total_chars = sum(len(s) for s in digest)
        included = 0
        for path in sorted(files):
            if included >= self.valves.MAX_FILES or total_chars >= self.valves.MAX_TOTAL_CHARS:
                break
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
            try:
                fr = requests.get(raw_url, timeout=10)
                if fr.status_code != 200:
                    continue
                content = fr.text
            except Exception:
                continue

            if len(content) > self.valves.MAX_FILE_CHARS:
                content = content[: self.valves.MAX_FILE_CHARS] + "\n... [truncated]"

            section = f"\n--- FILE: {path} ---\n{content}\n"
            if total_chars + len(section) > self.valves.MAX_TOTAL_CHARS:
                break
            digest.append(section)
            total_chars += len(section)
            included += 1

        digest.append(f"\n[Included {included} of {len(files)} candidate files]")
        return "\n".join(digest)

