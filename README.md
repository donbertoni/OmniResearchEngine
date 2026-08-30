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

Copy `.env.example` to `.env` and fill in what you need. Nothing is required to
run: without `DATABASE_URL` the app falls back to local JSON files for
persistence (login, triggers, automations, asset pools — shown with a visible
warning banner since it won't survive a redeploy); without the other variables,
each integration (BRAPI, WhatsApp, Telegram, SMTP) fails honestly instead of
faking success. For real persistence, point `DATABASE_URL` at a Postgres project
dedicated to this app (e.g. its own Neon project — don't reuse another
project's database), then apply the schema:

```bash
alembic upgrade head
```

The app is multi-tenant (`organizations`/`org_members` — see
`docs/ARCHITECTURE.md`); the still-Streamlit-only UI operates as a single
fixed "legacy" organization (`omni/domain/tenancy.LEGACY_ORG_ID`) until it's
replaced by the FastAPI + Next.js surface.

For the Auto-Pilot scheduler in a multi-process deployment, run
`python scheduler_worker.py` as one dedicated process and set
`OMNI_DISABLE_INLINE_SCHEDULER=1` so the Streamlit process doesn't also start
its own scheduler (which would duplicate every dispatch).

## Documentation

- [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) — project structure, layers, and dependency rule.
- [`docs/CHANGELOG.md`](./docs/CHANGELOG.md) — change history.
- [`docs/TODO.md`](./docs/TODO.md) — known functional gaps, prioritized.
