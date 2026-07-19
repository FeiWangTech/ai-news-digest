import os
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient
from smtplib import SMTPAuthenticationError, SMTPException

from backend.app.main import app

client = TestClient(app)


def _env_smtp():
    return {
        "GMAIL_SENDER": "sender@example.com",
        "GMAIL_APP_PW": "abcdefghijklmnop",
    }


def test_send_success():
    mock_hn_items = [
        {
            "source": "Hacker News",
            "title": "HN Story 1",
            "url": "https://example.com/1",
            "score": 100,
        },
    ]
    with patch.dict(os.environ, _env_smtp()), patch(
        "backend.app.services.email.smtplib.SMTP"
    ) as mock_smtp_cls, patch(
        "backend.app.main.fetch_hackernews_ai", return_value=(mock_hn_items, None)
    ):
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        response = client.post(
            "/api/digest/send",
            json={
                "sources": {"hn": True, "techcrunch": False, "arxiv": False},
                "limits": {"hn": 1},
                "recipient": "user@example.com",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["sent"] is True
    assert "Email sent successfully" in data["message"]
    mock_server.sendmail.assert_called_once()
    mock_server.login.assert_called_once_with("sender@example.com", "abcdefghijklmnop")


def test_send_invalid_recipient_blank():
    response = client.post(
        "/api/digest/send",
        json={
            "sources": {"hn": False},
            "recipient": "   ",
        },
    )
    assert response.status_code == 422


def test_send_invalid_recipient_no_at():
    response = client.post(
        "/api/digest/send",
        json={
            "sources": {"hn": False},
            "recipient": "userexample.com",
        },
    )
    assert response.status_code == 422


def test_send_invalid_recipient_no_local():
    response = client.post(
        "/api/digest/send",
        json={
            "sources": {"hn": False},
            "recipient": "@example.com",
        },
    )
    assert response.status_code == 422


def test_send_invalid_recipient_no_domain_dot():
    response = client.post(
        "/api/digest/send",
        json={
            "sources": {"hn": False},
            "recipient": "user@example",
        },
    )
    assert response.status_code == 422


def test_send_invalid_recipient_embedded_whitespace():
    for bad in ["user @example.com", "user@ example.com", "user\t@example.com", "user\r\n@example.com"]:
        response = client.post(
            "/api/digest/send",
            json={
                "sources": {"hn": False},
                "recipient": bad,
            },
        )
        assert response.status_code == 422


def test_send_smtp_not_configured():
    with patch.dict(os.environ, {}, clear=True):
        response = client.post(
            "/api/digest/send",
            json={
                "sources": {"hn": False},
                "recipient": "user@example.com",
            },
        )
    assert response.status_code == 503
    assert response.json()["detail"] == "Email delivery is not configured"
    assert "GMAIL" not in response.text


def test_send_smtp_auth_failure():
    with patch.dict(os.environ, _env_smtp()), patch(
        "backend.app.services.email.smtplib.SMTP"
    ) as mock_smtp_cls:
        mock_server = MagicMock()
        mock_server.login.side_effect = SMTPAuthenticationError(535, b"auth failed")
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        response = client.post(
            "/api/digest/send",
            json={
                "sources": {"hn": False},
                "recipient": "user@example.com",
            },
        )

    assert response.status_code == 502
    assert response.json()["detail"] == "Email delivery failed"
    assert "abcdefghijklmnop" not in response.text


def test_send_smtp_connection_refused():
    with patch.dict(os.environ, _env_smtp()), patch(
        "backend.app.services.email.smtplib.SMTP",
        side_effect=ConnectionRefusedError("connection refused"),
    ):
        response = client.post(
            "/api/digest/send",
            json={
                "sources": {"hn": False},
                "recipient": "user@example.com",
            },
        )

    assert response.status_code == 502
    assert response.json()["detail"] == "Email delivery failed"
    assert "abcdefghijklmnop" not in response.text


def test_send_no_password_in_logs_or_response():
    captured = []
    with patch.dict(os.environ, _env_smtp()), patch(
        "backend.app.services.email.smtplib.SMTP"
    ), patch("builtins.print", side_effect=lambda *args, **kwargs: captured.append(" ".join(str(a) for a in args))):
        response = client.post(
            "/api/digest/send",
            json={
                "sources": {"hn": False},
                "recipient": "user@example.com",
            },
        )

    assert response.status_code == 200
    for blob in [response.text] + captured:
        assert "abcdefghijklmnop" not in blob
        assert "GMAIL_APP_PW" not in blob


def test_send_one_source_fails_others_succeed():
    mock_hn_items = [
        {
            "source": "Hacker News",
            "title": "HN Story",
            "url": "https://example.com/hn",
            "score": 10,
        },
    ]
    with patch.dict(os.environ, _env_smtp()), patch(
        "backend.app.services.email.smtplib.SMTP"
    ) as mock_smtp_cls:
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_server
        with patch(
            "backend.app.main.fetch_hackernews_ai",
            return_value=(mock_hn_items, None),
        ), patch(
            "backend.app.main.fetch_techcrunch_ai",
            side_effect=RuntimeError("TechCrunch boom"),
        ), patch(
            "backend.app.main.fetch_arxiv_ai",
            return_value=([], None),
        ):
            response = client.post(
                "/api/digest/send",
                json={
                    "sources": {
                        "hn": True,
                        "techcrunch": True,
                        "arxiv": True,
                    },
                    "recipient": "user@example.com",
                },
            )

    assert response.status_code == 200
    data = response.json()
    assert data["sent"] is True
    assert data["warnings"] is not None
    assert any("TechCrunch fetch failed" in w for w in data["warnings"])
    mock_server.sendmail.assert_called_once()
