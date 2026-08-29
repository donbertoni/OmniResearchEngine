# OmniResearchEngine

Engine to automatize the creation of Financial Reports.

Streamlit terminal with real-time Crypto/TradFi quotes, automated report
generation (B2B, YouTube, WhatsApp, Telegram) and AI/ML agents (currently
simulated — see [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md)).

## Running locally

```bash
pip install -r requirements-dev.txt   # runtime + pytest
pytest                                  # run the test suite
streamlit run app.py
```

## Documentation

- [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) — project structure, layers, and dependency rule.
- [`docs/CHANGELOG.md`](./docs/CHANGELOG.md) — change history.
- [`docs/TODO.md`](./docs/TODO.md) — known functional gaps, prioritized.
