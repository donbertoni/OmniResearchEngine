# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] - 2026-08-29 (Phase 0: multi-tenant foundation)

First phase of the multi-tenant SaaS migration (see
`docs/ARCHITECTURE.md#multi-tenancy` for the full design and phased plan).
Streamlit keeps running unmodified in behavior throughout.

### Added
- `organizations` and `org_members` tables/models
(`omni/domain/models.py::Organization`, `OrgMember`), plus
`OrganizationRepositoryPort`/`OrgMemberRepositoryPort` (Postgres + JSON
adapters).
- `omni/domain/rbac.py::role_capabilities(role)` — in-org permission axis
  (owner/admin/analyst/viewer), orthogonal to the existing tier/billing axis.
- `omni/application/token_service.py` — JWT (RS256) access tokens + opaque
  refresh tokens with multi-tenant claims (`org_id`, `role`, `tier`). Not wired
  into `ui/` yet (Streamlit keeps using `session_token_service.py`) — laid down
  now so Phase 1's API doesn't have to redesign the token format later.
- `auth_service.py` password hashing upgraded PBKDF2 → argon2id, with
  transparent re-hash on next successful login for existing hashes (no forced
  password resets).
- Alembic (`alembic.ini`, `migrations/`) replaces the old idempotent
  `schema.sql`-applied-on-boot approach (`connection.py::ensure_schema`,
  removed) with a versioned migration (`0001_multitenant_schema`).
- `omni/domain/tenancy.py::LEGACY_ORG_ID` — the fixed organization every
  Streamlit call uses until the UI is replaced (Phase 1).

### Changed
- Every tenant-scoped port (`TriggerConfigRepositoryPort`,
  `AutomationConfigRepositoryPort`, `CredentialsRepositoryPort`,
  `AssetPoolRepositoryPort`, `MlPredictionLogRepositoryPort`) and its
  Postgres/JSON adapters now take `org_id` as an explicit first parameter.
- `trigger_service.py`/`automation_service.py` thread `org_id` through
  unchanged (bodies untouched, only signatures).
- `report_scheduler.check_and_dispatch` now loops over every active
  organization (`org_repo.list_active_org_ids()`) instead of assuming a single
  global tenant.

### Fixed
- `trigger_service.save_trigger_configuration`'s max-assets-per-trigger limit
  check read `config_data["ativos_selecionados"]`, a key that was never set
  (the actual key is `"ativos_selecionados_tickers"`) — the limit silently
  never triggered regardless of how many assets were selected.

## [Unreleased] - 2026-08-29

Closes almost every gap listed in [`TODO.md`](./TODO.md) (P0 through P3), except
the two documented in "Known limitations" in [`ARCHITECTURE.md`](./ARCHITECTURE.md)
(real AI/ML agents, YouTube Auto-Pilot) — both need a model/pipeline decision of
their own, not just plumbing.

### Added
- **Real Auto-Pilot scheduler**: the "Gatilhos de Report" panel now has a working
  Save button, and `omni/adapters/scheduling/report_scheduler.py` (APScheduler,
  ticking every minute) actually dispatches reports on the configured
  days/times/assets through whichever channels are configured in Automations.
  `scheduler_worker.py` runs it as a standalone process for multi-worker deploys.
- **Postgres persistence** (`omni/adapters/persistence/postgres/`, schema in
  `schema.sql`) for users, trigger configs, automation settings, API credentials,
  asset pools/categories, and ML prediction logs — used automatically when
  `DATABASE_URL` is set; falls back to local JSON files otherwise (with a visible
  UI banner warning that state won't survive a redeploy in that mode). See
  `omni/composition.py` and `.env.example`.
- **Real login** (`omni/application/auth_service.py`): PBKDF2-hashed passwords,
  actual signup/login forms, tier read from the persisted user record instead of
  guessed from an e-mail substring. "Manter-se conectado" now really persists a
  signed session token (`session_token_service.py`) instead of being decorative.
- **Tier permissions actually enforced**: Free tier can no longer open the
  Calibration customization form; the trigger "monitored assets" selector is
  capped to the tier's `max_free_tickers`.
- **Real outbound integrations**: `GenericWebhookAdapter` (CRM Push and
  scheduled webhooks now make a real HTTP POST instead of showing a toast),
  `SmtpEmailAdapter` (real e-mail via SMTP), `TelegramNotificationAdapter` (real
  Telegram Bot API send — was a static string with zero integration before).
  Automations panel fields (e-mails, webhook URLs, WhatsApp numbers, Telegram
  chat IDs, CRM platform/API key) are now persisted and actually read by both the
  manual "Disparo Imediato" buttons and the scheduler.
- Adapter failures are now visible: the dashboard shows an explicit warning
  banner listing which symbols came back with no real quote, instead of silently
  showing `0`.
- `.github/workflows/ci.yml` runs `pytest` on every push/PR.
- Test coverage for everything above: `auth_service`, `automation_service`,
  `report_scheduler.check_and_dispatch`, `session_token_service`.

### Removed
- `custom_data_api_key`: dead field (captured in the Calibration form, passed
  down to `MarketDataPort.fetch_quotes(..., custom_api_key=...)`, but no adapter
  ever read it). Removed end-to-end rather than wired to a nonexistent feature.
- `determine_tier`'s e-mail-substring heuristic (`admin@x.com` → Premium) —
  replaced by the real tier stored on the authenticated user.

## [Unreleased] - 2026-08-27

### Changed
- Full reorganization of the project into a hexagonal architecture (still a single
  monolith, no microservices): `omni/domain`, `omni/application`, `omni/adapters`,
  `ui/`. See [`ARCHITECTURE.md`](./ARCHITECTURE.md).
- `app.py` and `backend.py` (a single ~1400-line script) were replaced by modules
  isolated by responsibility; `backend.py` was removed.

### Fixed
- `CATEGORIES_TRADFI` was duplicated and inconsistent between `app.py` and
  `backend.py` (wrong ticker `TOTVS3.SA`). Unified in `omni/domain/catalog.py`
  with the correct ticker `TOTS3.SA`.
- Credentials (BRAPI token, WhatsApp instance/token) entered in the Calibration
  panel were discarded on the rerun right after saving — they never actually got
  used. They now persist in `session_state`.
- Typo bug in the TradFi asset pool initialization (checked one key, wrote to a
  different one), which reset the pool on every rerun.
- `reportlab` was used to generate PDFs but wasn't declared in
  `requirements.txt` — without the library installed, the PDF download silently
  became plain text. Added to dependencies.
- WhatsApp sending (`send_whatsapp_report`) always returned success without ever
  making the actual request. It now fails honestly when not configured
  (`WHATSAPP_API_BASE_URL`) and performs a real POST when configured.
- No external API call was cached — every dashboard interaction re-fetched
  everything, and the "Refresh" button had no effect at all. Added
  `st.cache_data(ttl=60)` at the data entry point.
- Editing a category's assets in the same submit that renamed it wiped the asset
  selection (it read the wrong form state key).

### Added
- `pytest` test suite for the pure domain/application functions: number/percentage
  formatting, asset catalog, and report assembly.
- `requirements-dev.txt` for development dependencies (pytest).
- `pytest.ini` (pytest cache moved to `.cache/pytest_cache`).

### Removed
- `custom_tickers`: dead feature, declared but never wired to any UI input.
- Duplicate `config.toml` at the project root (the real theme always came from
  `.streamlit/config.toml`, which was already the file actually in use).
