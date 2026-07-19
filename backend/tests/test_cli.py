from backend.app import cli


def test_send_scheduled_digest_builds_and_sends(monkeypatch):
    captured = {}

    def fake_build_digest_payload(request):
        captured["request"] = request
        return {
            "plain": "Plain digest",
            "html": "<h1>Digest</h1>",
            "warnings": ["TechCrunch warning"],
        }

    def fake_send_digest_email(recipient, subject, plain_text, html_body):
        captured["email"] = {
            "recipient": recipient,
            "subject": subject,
            "plain_text": plain_text,
            "html_body": html_body,
        }

    monkeypatch.setattr(cli, "_build_digest_payload", fake_build_digest_payload)
    monkeypatch.setattr(cli, "send_digest_email", fake_send_digest_email)

    warnings = cli.send_scheduled_digest(
        recipient="reader@example.com",
        hn_limit=4,
        techcrunch_limit=5,
        arxiv_limit=6,
    )

    request = captured["request"]
    assert request.recipient == "reader@example.com"
    assert request.sources == {
        "hn": True,
        "techcrunch": True,
        "arxiv": True,
        "tip": True,
    }
    assert request.limits == {
        "hn": 4,
        "techcrunch": 5,
        "arxiv": 6,
    }
    assert captured["email"] == {
        "recipient": "reader@example.com",
        "subject": "AI Daily Digest",
        "plain_text": "Plain digest",
        "html_body": "<h1>Digest</h1>",
    }
    assert warnings == ["TechCrunch warning"]


def test_main_reports_success_and_warnings(monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "send_scheduled_digest",
        lambda **kwargs: ["arXiv warning"],
    )

    exit_code = cli.main(["--recipient", "reader@example.com"])

    output = capsys.readouterr()
    assert exit_code == 0
    assert "Digest sent successfully to reader@example.com" in output.out
    assert "Warning: arXiv warning" in output.out
    assert output.err == ""


def test_main_reports_delivery_failure(monkeypatch, capsys):
    def fail_delivery(**kwargs):
        raise RuntimeError("Email delivery is not configured")

    monkeypatch.setattr(cli, "send_scheduled_digest", fail_delivery)

    exit_code = cli.main(["--recipient", "reader@example.com"])

    output = capsys.readouterr()
    assert exit_code == 1
    assert output.out == ""
    assert "Digest delivery failed" in output.err
    assert "Email delivery is not configured" in output.err