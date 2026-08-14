"""
Installs (or updates) the web scraper and GitHub repo reader Tools into Open
WebUI over its REST API, so no manual copy/paste into the UI is needed.

Reads every .py file in /tools, pulls a title/description out of its leading
docstring frontmatter, and POSTs it to Open WebUI's tools API. If a tool with
that id already exists, it is left alone and skipped, this script never
overwrites an existing tool. To push a source change to a tool that's
already installed, delete it in Open WebUI first (or give it a new id),
then re-run.

Configured entirely through environment variables (see docker-compose.yml):
  OPEN_WEBUI_URL   base URL of Open WebUI, e.g. http://open-webui:8080
  ADMIN_EMAIL      email for the account that will own these tools
  ADMIN_PASSWORD   password for that account
  ADMIN_NAME       display name, only used if the account doesn't exist yet
  TOOLS_DIR        directory containing the .py tool files (default /tools)
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

OPEN_WEBUI_URL = os.environ.get("OPEN_WEBUI_URL", "http://open-webui:8080").rstrip("/")
ADMIN_EMAIL = os.environ["ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
ADMIN_NAME = os.environ.get("ADMIN_NAME", "Admin")
TOOLS_DIR = os.environ.get("TOOLS_DIR", "/tools")

MAX_RETRIES = 30
RETRY_DELAY_SECONDS = 3


def request(method, path, token=None, payload=None):
    url = f"{OPEN_WEBUI_URL}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, (json.loads(body) if body else {})
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"detail": body}


def wait_for_server():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            status, _ = request("GET", "/health")
            if status == 200:
                return
        except Exception:
            pass
        print(f"Waiting for Open WebUI to be reachable... ({attempt}/{MAX_RETRIES})")
        time.sleep(RETRY_DELAY_SECONDS)
    print("Open WebUI never became reachable, giving up.")
    sys.exit(1)


def get_admin_token():
    # First run: this creates the account (and it becomes admin, since it's
    # the first user). Later runs: signup fails because the account already
    # exists, so fall back to signing in with the same credentials.
    status, body = request(
        "POST", "/api/v1/auths/signup",
        payload={"name": ADMIN_NAME, "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    if status == 200 and "token" in body:
        print(f"Created admin account {ADMIN_EMAIL}.")
        return body["token"]

    status, body = request(
        "POST", "/api/v1/auths/signin",
        payload={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    if status == 200 and "token" in body:
        print(f"Signed in as {ADMIN_EMAIL}.")
        return body["token"]

    print(f"Could not authenticate as {ADMIN_EMAIL}: {body}")
    sys.exit(1)


def parse_frontmatter(content):
    """Pull title/description out of the module's leading docstring, if present."""
    match = re.match(r'\s*"""(.*?)"""', content, re.DOTALL)
    title, description = None, None
    if match:
        block = match.group(1)
        t = re.search(r"^title:\s*(.+)$", block, re.MULTILINE)
        d = re.search(r"^description:\s*(.+)$", block, re.MULTILINE)
        if t:
            title = t.group(1).strip()
        if d:
            description = d.group(1).strip()
    return title, description


def tool_exists(token, tool_id):
    status, _ = request("GET", f"/api/v1/tools/id/{tool_id}", token=token)
    return status == 200


def install_tool(token, filepath):
    filename = os.path.basename(filepath)
    tool_id = re.sub(r"[^a-z0-9_]", "_", filename[:-3].lower())

    if tool_exists(token, tool_id):
        print(f"Tool '{tool_id}' already exists, skipping (not overwriting).")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    title, description = parse_frontmatter(content)
    name = title or tool_id
    payload = {
        "id": tool_id,
        "name": name,
        "content": content,
        "meta": {"description": description or ""},
    }

    status, body = request("POST", "/api/v1/tools/create", token=token, payload=payload)
    if status == 200:
        print(f"Installed tool '{name}' (id={tool_id}).")
        return

    if status == 400 and "taken" in json.dumps(body).lower():
        # Lost a race with something else that created it between our check
        # and this request. Treat it the same as "already exists": skip.
        print(f"Tool '{tool_id}' already exists (created concurrently), skipping.")
        return

    print(f"Failed to install tool '{name}' (id={tool_id}): status={status} body={body}")
    sys.exit(1)


def main():
    wait_for_server()
    token = get_admin_token()

    tool_files = sorted(
        os.path.join(TOOLS_DIR, f) for f in os.listdir(TOOLS_DIR) if f.endswith(".py")
    )
    if not tool_files:
        print(f"No .py tool files found in {TOOLS_DIR}.")
        return

    for filepath in tool_files:
        install_tool(token, filepath)

    print("Done.")


if __name__ == "__main__":
    main()

