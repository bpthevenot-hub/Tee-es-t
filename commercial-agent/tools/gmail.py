"""Gmail tools for the commercial agent.

Credentials are looked up in this order:

1. ``GMAIL_TOKEN_JSON`` — content of an authorized-user token (CI, Railway, Render).
2. The token file written by ``python setup_gmail.py`` (``config/gmail_token.json``
   in the project, or ``$GMAIL_TOKEN_PATH``) — whatever the working directory.

Expired tokens are refreshed with their refresh token. The browser consent flow
only starts in an interactive terminal: in cron, CI or cloud runs it would wait
for a browser that never comes until the job is killed, so a missing or unusable
token is reported as a tool error instead.
"""

import os
import sys
import json
import base64
import logging
from email.mime.text import MIMEText
from pathlib import Path

from config import paths

try:
    from google.auth.exceptions import RefreshError
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

log = logging.getLogger("commercial-agent")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
]

SETUP_HINT = (
    "Run 'python setup_gmail.py' on a machine with a browser, then provide the "
    "resulting token as GMAIL_TOKEN_JSON or as the token file."
)

# Upper bound on waiting for the browser consent, in case a terminal is
# attached but nobody is there (docker -t, tmux, script).
CONSENT_TIMEOUT_SECONDS = 300

# Malformed token data surfaces as one of these, depending on what is wrong.
TOKEN_DATA_ERRORS = (ValueError, TypeError, AttributeError)

_service = None


def _is_interactive() -> bool:
    """True when someone can complete the browser consent flow in this run."""
    if os.getenv("CI", "").strip().lower() in ("1", "true", "yes"):
        return False
    try:
        return sys.stdin is not None and sys.stdin.isatty()
    except (AttributeError, ValueError):  # replaced or closed stdin
        return False


def _write_private(path: Path, content: str) -> None:
    """Write a secret file readable by the current user only."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    os.chmod(path, 0o600)


def _creds_from_env(token_json: str):
    """Parse GMAIL_TOKEN_JSON. Returns (credentials, None) or (None, problem)."""
    try:
        info = json.loads(token_json)
    except json.JSONDecodeError:
        return None, "not valid JSON: empty, truncated or a placeholder secret"
    if not isinstance(info, dict):
        return None, "not a JSON object"
    try:
        return Credentials.from_authorized_user_info(info, SCOPES), None
    except TOKEN_DATA_ERRORS as e:
        return None, f"not an authorized-user token: {e}"


def _run_consent_flow():
    """Browser consent flow — only called from an interactive terminal."""
    credentials_path = paths.gmail_credentials_path()
    credentials_json = os.getenv("GMAIL_CREDENTIALS_JSON", "").strip()

    if credentials_path.exists():
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
    elif credentials_json:
        try:
            client_config = json.loads(credentials_json)
        except json.JSONDecodeError:
            raise RuntimeError("GMAIL_CREDENTIALS_JSON is not valid JSON.") from None
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    else:
        raise RuntimeError(
            f"Gmail not configured: no OAuth client in {credentials_path} or "
            f"GMAIL_CREDENTIALS_JSON. {SETUP_HINT}"
        )
    return flow.run_local_server(port=0, timeout_seconds=CONSENT_TIMEOUT_SECONDS)


def _get_gmail_service():
    """Authenticate and return the Gmail API service."""
    global _service
    if _service is not None:
        return _service

    if not GMAIL_AVAILABLE:
        raise RuntimeError("Gmail dependencies not installed. Run: pip install -r requirements.txt")

    token_path = paths.gmail_token_path()
    creds = None
    from_env = False
    problems = []

    # 1. Token from env var (CI, Railway, Render). The env var stays the source
    #    of truth, so it is never copied to disk.
    token_json = os.getenv("GMAIL_TOKEN_JSON", "").strip()
    if token_json:
        creds, problem = _creds_from_env(token_json)
        if problem:
            problems.append(f"GMAIL_TOKEN_JSON: {problem}")
        from_env = creds is not None

    # 2. Token file written by setup_gmail.py
    if creds is None and token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except TOKEN_DATA_ERRORS as e:  # corrupt or truncated file
            problems.append(f"{token_path.name}: unreadable token ({e})")

    # 3. Refresh if expired, keeping the token file up to date
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError as e:  # revoked, or a 7-day "Testing" OAuth app
            problems.append(f"token refresh failed ({e.args[0] if e.args else e})")
            creds = None
        else:
            if not from_env:
                try:
                    _write_private(token_path, creds.to_json())
                except OSError as e:  # read-only checkout: keep the token in memory
                    log.warning(f"Could not save the refreshed Gmail token: {e}")

    # 4. No usable token: browser consent, but never in unattended runs
    if not creds or not creds.valid:
        detail = f" ({'; '.join(problems)})" if problems else ""
        if not _is_interactive():
            raise RuntimeError(
                f"Gmail is not authorized for unattended runs: no valid token in "
                f"GMAIL_TOKEN_JSON or {token_path}{detail}. {SETUP_HINT}"
            )
        if problems:
            log.warning(f"Gmail token unusable, starting browser consent{detail}")
        creds = _run_consent_flow()
        _write_private(token_path, creds.to_json())

    _service = build("gmail", "v1", credentials=creds)
    return _service


# --- Tool Definitions ---

GMAIL_TOOLS = [
    {
        "name": "gmail_search_messages",
        "description": "Search Gmail messages. Supports Gmail search syntax: from:, to:, subject:, is:unread, has:attachment, after:YYYY/MM/DD, before:YYYY/MM/DD.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Gmail search query (e.g. 'from:client@example.com is:unread').",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum messages to return (default 10).",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "gmail_read_message",
        "description": "Read the full content of a specific Gmail message by ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "The Gmail message ID (from gmail_search_messages).",
                },
            },
            "required": ["message_id"],
        },
    },
    {
        "name": "gmail_read_thread",
        "description": "Read an entire email conversation thread.",
        "input_schema": {
            "type": "object",
            "properties": {
                "thread_id": {
                    "type": "string",
                    "description": "The Gmail thread ID.",
                },
            },
            "required": ["thread_id"],
        },
    },
    {
        "name": "gmail_create_draft",
        "description": "Create an email draft in Gmail. The draft will NOT be sent automatically — it stays in Drafts for review. Always use this instead of sending directly.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address."},
                "subject": {"type": "string", "description": "Email subject line."},
                "body": {"type": "string", "description": "Email body (plain text)."},
                "thread_id": {
                    "type": "string",
                    "description": "Thread ID to reply to (optional, for replies).",
                },
            },
            "required": ["to", "subject", "body"],
        },
    },
]


# --- Tool Execution ---

def execute_gmail_tool(name: str, input_data: dict) -> str:
    """Execute a Gmail tool and return the result as a string."""
    try:
        if name == "gmail_search_messages":
            return _search_messages(input_data)
        elif name == "gmail_read_message":
            return _read_message(input_data)
        elif name == "gmail_read_thread":
            return _read_thread(input_data)
        elif name == "gmail_create_draft":
            return _create_draft(input_data)
        else:
            return f"Error: Unknown Gmail tool '{name}'"
    except Exception as e:
        return f"Error executing {name}: {str(e)}"


def _search_messages(input_data: dict) -> str:
    service = _get_gmail_service()
    query = input_data["query"]
    max_results = input_data.get("max_results", 10)

    result = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()

    messages = []
    for msg_ref in result.get("messages", []):
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"],
        ).execute()

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        messages.append({
            "id": msg["id"],
            "thread_id": msg["threadId"],
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
        })

    return json.dumps({"total": result.get("resultSizeEstimate", 0), "messages": messages}, ensure_ascii=False)


def _read_message(input_data: dict) -> str:
    service = _get_gmail_service()
    msg = service.users().messages().get(
        userId="me", id=input_data["message_id"], format="full"
    ).execute()

    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
    body = _extract_body(msg.get("payload", {}))

    return json.dumps({
        "id": msg["id"],
        "thread_id": msg["threadId"],
        "from": headers.get("From", ""),
        "to": headers.get("To", ""),
        "subject": headers.get("Subject", ""),
        "date": headers.get("Date", ""),
        "body": body,
    }, ensure_ascii=False)


def _read_thread(input_data: dict) -> str:
    service = _get_gmail_service()
    thread = service.users().threads().get(
        userId="me", id=input_data["thread_id"], format="full"
    ).execute()

    messages = []
    for msg in thread.get("messages", []):
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        body = _extract_body(msg.get("payload", {}))
        messages.append({
            "id": msg["id"],
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "body": body[:2000],  # Limit body length per message
        })

    return json.dumps({"thread_id": input_data["thread_id"], "messages": messages}, ensure_ascii=False)


def _create_draft(input_data: dict) -> str:
    service = _get_gmail_service()
    sender = os.getenv("AGENT_OWNER_EMAIL", "me")

    message = MIMEText(input_data["body"])
    message["to"] = input_data["to"]
    message["from"] = sender
    message["subject"] = input_data["subject"]

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {"message": {"raw": raw}}

    if "thread_id" in input_data:
        body["message"]["threadId"] = input_data["thread_id"]

    draft = service.users().drafts().create(userId="me", body=body).execute()

    return json.dumps({
        "status": "draft_created",
        "draft_id": draft["id"],
        "message": f"Draft created for {input_data['to']}. Subject: {input_data['subject']}. Review in Gmail before sending.",
    }, ensure_ascii=False)


def _extract_body(payload: dict) -> str:
    """Extract plain text body from a Gmail message payload."""
    if payload.get("mimeType") == "text/plain" and "body" in payload:
        data = payload["body"].get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    for part in payload.get("parts", []):
        result = _extract_body(part)
        if result:
            return result

    return ""
