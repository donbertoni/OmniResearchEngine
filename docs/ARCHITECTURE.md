# Architecture

OmniResearchEngine is a single monolith (one Streamlit app, `streamlit run app.py`),
organized internally into layers in a hexagonal (ports & adapters) style. There are
no microservices or separate processes — the point of the split is to isolate
business logic and external integrations from the UI layer, and to make the logic
testable without having to run Streamlit.

## Layers

```
app.py                  # thin entrypoint: from ui.main import run; run()
scheduler_worker.py      # standalone process for the Auto-Pilot scheduler (see below)
alembic.ini, migrations/  # versioned Postgres schema (see "Multi-tenancy" below)
omni/
├── domain/             # pure models and rules — imports nothing from the other layers
│   ├── models.py        # Quote, MarketSentiment, TierPermissions, User, Organization, OrgMember, ...
│   ├── formatting.py     # fmt_num, fmt_pct
│   ├── catalog.py        # single source of truth for categories/benchmarks (CATEGORIES_*, *_BENCHMARKS)
│   ├── tenancy.py         # LEGACY_ORG_ID — the fixed org every ui/ (Streamlit) call uses
│   ├── rbac.py             # role_capabilities(role) — in-org permission axis, orthogonal to tier
│   └── ports.py           # Protocols the application layer uses to talk to the outside world
├── application/        # testable orchestration — only depends on omni.domain.ports
│   ├── dashboard_service.py
│   ├── report_service.py
│   ├── catalog_service.py
│   ├── trigger_service.py
│   ├── automation_service.py  # persists + dispatches CRM/webhook/e-mail/WhatsApp/Telegram automation config
│   ├── auth_service.py         # password hashing (argon2id, legacy PBKDF2 still verifiable) + authenticate/register
│   ├── token_service.py         # JWT access token + opaque refresh token (multi-tenant claims: org_id/role/tier)
│   ├── session_token_service.py  # Streamlit-only "keep me logged in" (HMAC token in a URL param) — superseded
│   │                              by token_service.py once ui/ is replaced (Phase 1), kept until then
│   ├── liquidity_service.py
│   └── agents_service.py   # STUB — simulated AI/ML agents, no real model behind them (see Known limitations)
├── adapters/           # concrete implementations of the ports (the only layer that touches network/disk)
│   ├── market_data/     # yfinance + BRAPI fallback
│   ├── sentiment/        # Alternative.me (Fear & Greed)
│   ├── global_market/    # CoinGecko
│   ├── liquidity/        # Deribit (Crypto) and volume profile via yfinance (TradFi)
│   ├── reporting/        # PDF export (reportlab)
│   ├── notifications/    # WhatsApp, Telegram (Bot API), generic webhook, SMTP e-mail
│   ├── scheduling/        # report_scheduler.py — the real Auto-Pilot scheduler (APScheduler)
│   └── persistence/      # JsonXxxRepository (local fallback) + persistence/postgres/ (recommended)
└── config/
    └── settings.py       # credential defaults via environment variables

composition.py            # THE composition root: builds Infrastructure (Postgres if DATABASE_URL
                           # is set, else local JSON) shared by ui/main.py and scheduler_worker.py

ui/                     # the only layer that imports `streamlit`
├── main.py              # calls omni.composition.build_infrastructure() and assembles the panels
├── sidebar.py, state.py, styles.py, translations.py
└── panels/              # one module per visual block on the screen
```

## Dependency rule

- `domain` imports nothing from `application`, `adapters`, or `ui`.
- `application` only depends on the `Protocol`s defined in `domain/ports.py` — it
  never imports a concrete adapter. `omni/composition.py` is the single place that
  decides which concrete adapter to wire up.
- `ui` is the only layer that knows the app runs on Streamlit. Swapping the UI
  framework (e.g. turning this into an API) would mean rewriting only this folder.

## Persistence: Postgres vs. local JSON

`composition.build_infrastructure()` checks `DATABASE_URL`: if it's set, every
repository port (trigger config, automation settings, API credentials, users,
organizations/members, asset pools/categories, ML prediction logs) is backed by
a Postgres adapter under `omni/adapters/persistence/postgres/`. Schema is
managed by **Alembic** (`alembic upgrade head`, see `migrations/` at the repo
root) as an explicit deploy step — not applied automatically at runtime, since
an idempotent `CREATE TABLE IF NOT EXISTS` approach (the previous design)
survives initial creation but not iterative schema changes. If `DATABASE_URL`
isn't set, the app falls back to the `JsonXxxRepository` adapters (one flat
file per concern, gitignored) so it still runs with zero external infra for
local development — the UI shows a visible banner when running in this
fallback mode, since state won't survive a redeploy in it. Both implementations
satisfy the exact same ports, so the choice is purely a `composition.py`
wiring decision, not something the rest of the code needs to know about.

Use a **Postgres project dedicated to this app** (e.g. its own Neon project) —
don't reuse a database that already serves another project.

## Multi-tenancy

This is a product sold to multiple client companies, not a single-tenant
internal tool — every tenant-scoped port (`TriggerConfigRepositoryPort`,
`AutomationConfigRepositoryPort`, `CredentialsRepositoryPort`,
`AssetPoolRepositoryPort`, `MlPredictionLogRepositoryPort`) takes `org_id` as
an explicit first parameter. This is deliberately the *primary* isolation
mechanism (simple, unit-testable with fakes, works for background jobs with no
request context) — Postgres Row Level Security is planned as a *second*,
redundant layer once the API layer exists to set it per request (not enabled
yet; see the plan referenced below).

`organizations` (billing/branding: `tier`, `stripe_*`, `company_name`/
`cnpi_code`/`logo_url` for white-label) and `org_members` (`org_id`, `user_id`,
`role` ∈ owner/admin/analyst/viewer) are the two new tables this introduces.
**Tier vs. role are orthogonal, never conflated**: `organizations.tier` feeds
`catalog_service.tier_permissions(tier)` (billing plan — what the org paid
for), `org_members.role` feeds `omni/domain/rbac.py::role_capabilities(role)`
(in-org permission — what this specific person can do). A viewer at a Premium
org still can't edit triggers.

**`ui/` (Streamlit) has no concept of organization** — it's a single-user
interface from before this pivot. Rather than rewriting it to gain that
concept, the plan is to replace it with FastAPI + Next.js instead (see
`docs/TODO.md`); until that lands, every call from `ui/` threads a fixed
constant, `omni/domain/tenancy.LEGACY_ORG_ID`, through the now-`org_id`-taking
calls (`ui/state.py`, `ui/panels/config_panels.py`,
`ui/panels/agents_panel.py`). This is mechanical and temporary: it keeps the
still-running Streamlit app working unmodified in behavior while the rest of
the system becomes properly multi-tenant underneath it.

## Auto-Pilot scheduler

`omni/adapters/scheduling/report_scheduler.py` has a pure `check_and_dispatch(now,
infra)` function (no real clock/network — everything comes from the injected
`Infrastructure`, which is what makes it unit-testable) that, for a given
instant, checks every module's saved trigger config against the current
weekday/time and, on a match, builds the report content and dispatches it through
whichever channels are configured in Automations (e-mail via SMTP, generic
webhook, WhatsApp, Telegram), then marks that module as dispatched for that
minute to avoid double-firing.

`start_background_scheduler` wraps that in an APScheduler `BackgroundScheduler`
that ticks every minute, started once per process from `ui/main.py` (module-level
singleton guard). This is correct for a single-process deployment. For a
deployment that runs multiple app processes/workers, set
`OMNI_DISABLE_INLINE_SCHEDULER=1` (so the app doesn't start its own scheduler,
which would duplicate every dispatch) and run `scheduler_worker.py` as one
dedicated process instead — it reuses the exact same `check_and_dispatch` and
`composition.build_infrastructure()`.

## Why this matters here

Before the reorganization (see [`CHANGELOG.md`](./CHANGELOG.md)), everything — UI,
business logic, static data, and API calls — lived in two files totaling ~1400
lines, with no tests. That hid real bugs (duplicated and inconsistent data,
credentials that silently disappeared, no caching at all) that only surfaced
during a line-by-line review. The layering isn't just cosmetic: every bug that got
fixed corresponded to a responsibility that had been tangled up with another one.

## Known limitations (deliberately out of scope)

These two are the same *kind* of gap: both would require picking and integrating
an actual model/pipeline (not just wiring plumbing that's already there), which is
a product decision on its own, not a bug fix. Left for a dedicated follow-up:

- **AI/ML agents are mocks** (`omni/application/agents_service.py`) — text
  generated from a fixed template, no real model behind it. They're isolated to
  make a future swap easier (e.g. a real LLM call for the scriptwriter, real
  technical-indicator computation for the TA agent), but no real ML/LLM logic was
  implemented here.
- **YouTube Auto-Pilot is 100% UI mock** — no video rendering, no TTS, no YouTube
  API upload. Needs a YouTube Data API OAuth app plus a choice of TTS/render
  pipeline before it can do anything real.
