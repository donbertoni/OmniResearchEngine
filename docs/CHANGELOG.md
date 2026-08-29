# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
