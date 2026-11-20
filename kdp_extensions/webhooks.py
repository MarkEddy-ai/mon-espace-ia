"""
Bus de Webhooks SaaS — MarkEddy KDP Studio (Sur-Ensemble Zéro-Casse)
Émission d'événements signés HMAC-SHA256 vers n8n / Hermes / CRM avec retries et journalisation JSONL.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore

BASE_DIR = Path(__file__).resolve().parent.parent
WEBHOOK_LOG_FILE = BASE_DIR / "logs" / "webhooks_audit.jsonl"

SUPPORTED_EVENTS = (
    "market.trends.ready",
    "competitor.gap.ready",
    "book.manuscript.ready",
    "book.design.ready",
    "book.published.pack_ready",
    "job.failed",
)


def sign_payload(body_bytes: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def _append_audit_log(entry: Dict[str, Any]) -> None:
    WEBHOOK_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with WEBHOOK_LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def emit_webhook(
    event: str,
    payload: Dict[str, Any],
    url: Optional[str] = None,
    secret: Optional[str] = None,
    max_retries: int = 3,
    timeout: float = 8.0,
) -> Dict[str, Any]:
    target_url = (url or os.getenv("KDP_WEBHOOK_URL", "")).strip()
    signing_secret = (secret or os.getenv("KDP_WEBHOOK_SECRET", "markeddy_dev_secret")).strip()

    envelope = {
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "markeddy-kdp-studio",
        "data": payload,
    }
    body_bytes = json.dumps(envelope, ensure_ascii=False).encode("utf-8")
    signature = sign_payload(body_bytes, signing_secret)

    result: Dict[str, Any] = {
        "event": event,
        "url": target_url or None,
        "delivered": False,
        "status_code": None,
        "attempts": 0,
        "error": None,
    }

    if not target_url:
        result["mode"] = "local_audit_only"
        _append_audit_log({**envelope, "_delivery": result})
        return result

    if httpx is None:
        result["error"] = "httpx non installé"
        _append_audit_log({**envelope, "_delivery": result})
        return result

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "MarkEddy-KDP-Studio/1.0",
        "X-KDP-Event": event,
        "X-KDP-Signature": signature,
    }

    for attempt in range(1, max_retries + 1):
        result["attempts"] = attempt
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(target_url, content=body_bytes, headers=headers)
            result["status_code"] = resp.status_code
            if 200 <= resp.status_code < 300:
                result["delivered"] = True
                result["error"] = None
                break
            result["error"] = f"HTTP {resp.status_code}"
        except Exception as exc:
            result["error"] = str(exc)
        if attempt < max_retries:
            time.sleep(0.5 * attempt)

    _append_audit_log({**envelope, "_delivery": result})
    return result
