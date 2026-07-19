"""Command-line entry point for scheduled AI digest delivery."""

import argparse
import sys
from typing import Sequence

from .main import _build_digest_payload
from .schemas import DigestSendRequest
from .services.email import send_digest_email


def send_scheduled_digest(
    recipient: str,
    hn_limit: int = 3,
    techcrunch_limit: int = 3,
    arxiv_limit: int = 3,
) -> list[str]:
    """Build and send one digest, returning any source warnings."""
    request = DigestSendRequest(
        recipient=recipient,
        sources={
            "hn": True,
            "techcrunch": True,
            "arxiv": True,
            "tip": True,
        },
        limits={
            "hn": hn_limit,
            "techcrunch": techcrunch_limit,
            "arxiv": arxiv_limit,
        },
    )

    payload = _build_digest_payload(request)

    send_digest_email(
        recipient=request.recipient,
        subject="AI Daily Digest",
        plain_text=payload["plain"],
        html_body=payload["html"],
    )

    return payload["warnings"] or []


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Build and send the AI Daily Digest.",
    )
    parser.add_argument(
        "--recipient",
        required=True,
        help="Email address that will receive the digest.",
    )
    parser.add_argument("--hn-limit", type=int, default=3)
    parser.add_argument("--techcrunch-limit", type=int, default=3)
    parser.add_argument("--arxiv-limit", type=int, default=3)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the scheduled digest command."""
    args = build_parser().parse_args(argv)

    try:
        warnings = send_scheduled_digest(
            recipient=args.recipient,
            hn_limit=args.hn_limit,
            techcrunch_limit=args.techcrunch_limit,
            arxiv_limit=args.arxiv_limit,
        )
    except Exception as exc:
        print(f"Digest delivery failed: {exc}", file=sys.stderr)
        return 1

    print(f"Digest sent successfully to {args.recipient}")
    for warning in warnings:
        print(f"Warning: {warning}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())