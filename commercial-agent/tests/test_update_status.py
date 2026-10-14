"""docs/status.json is public: published contacts must not leak PII."""

from __future__ import annotations

from update_status import redact_contact


def test_redact_contact_strips_email_and_phone() -> None:
    raw = {
        "id": "42",
        "properties": {
            "firstname": "Alice",
            "lastname": "Martin",
            "email": "alice@example.com",
            "phone": "+33 6 00 00 00 00",
            "company": "ACME",
        },
    }
    out = redact_contact(raw)
    assert "email" not in out and "phone" not in out
    assert out["lastname"] == "M."
    assert out["id"] == "hs_42"
    assert "alice@example.com" not in str(out)
    assert "+33" not in str(out)


def test_redact_contact_handles_missing_fields() -> None:
    out = redact_contact({"id": "1", "properties": {"lastname": None}})
    assert out["lastname"] == ""
    assert out["lifecyclestage"] == "lead"
