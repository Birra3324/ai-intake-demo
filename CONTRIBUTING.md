# Contributing

This is a portfolio demo by Birra Gemedi. If you are forking it:

1. Copy `.env.example` to `.env`. Do not commit secrets.
2. Use the SQLite default until you have Postgres.
3. Run tests before opening a PR: `.venv/bin/pytest -q`
4. Keep AI keys out of source, fixtures, and n8n exports.
5. Prefer small, readable changes over new abstraction layers.

Python 3.12+ is the Docker baseline; local development on this machine uses Homebrew Python 3.14.
