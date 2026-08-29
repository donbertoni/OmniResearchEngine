# Architecture

OmniResearchEngine is a single monolith (one Streamlit app, `streamlit run app.py`),
organized internally into layers in a hexagonal (ports & adapters) style. There are
no microservices or separate processes — the point of the split is to isolate
business logic and external integrations from the UI layer, and to make the logic
testable without having to run Streamlit.

## Layers

```
app.py                  # thin entrypoint: from ui.main import run; run()
omni/
├── domain/             # pure models and rules — imports nothing from the other layers
│   ├── models.py        # Quote, MarketSentiment, GlobalCryptoStats, LiquidityData, TierPermissions
│   ├── formatting.py     # fmt_num, fmt_pct
│   ├── catalog.py        # single source of truth for categories/benchmarks (CATEGORIES_*, *_BENCHMARKS)
│   └── ports.py           # Protocols the application layer uses to talk to the outside world
├── application/        # testable orchestration — only depends on omni.domain.ports
│   ├── dashboard_service.py
│   ├── report_service.py
│   ├── catalog_service.py
│   ├── trigger_service.py
│   ├── liquidity_service.py
│   └── agents_service.py   # STUB — simulated AI/ML agents, no real model behind them
├── adapters/           # concrete implementations of the ports (the only layer that touches network/disk)
│   ├── market_data/     # yfinance + BRAPI fallback
│   ├── sentiment/        # Alternative.me (Fear & Greed)
│   ├── global_market/    # CoinGecko
│   ├── liquidity/        # Deribit (Crypto) and volume profile via yfinance (TradFi)
│   ├── reporting/        # PDF export (reportlab)
│   ├── notifications/    # WhatsApp dispatch
│   └── persistence/      # trigger config persistence in JSON
└── config/
    └── settings.py       # credential defaults via environment variables

ui/                     # the only layer that imports `streamlit`
├── main.py              # composition root: instantiates the adapters and assembles the panels
├── sidebar.py, state.py, styles.py, translations.py
└── panels/              # one module per visual block on the screen
```

## Dependency rule

- `domain` imports nothing from `application`, `adapters`, or `ui`.
- `application` only depends on the `Protocol`s defined in `domain/ports.py` — it
  never imports a concrete adapter. The composition root (`ui/main.py`) is the one
  that decides which adapter to use.
- `ui` is the only layer that knows the app runs on Streamlit. Swapping the UI
  framework (e.g. turning this into an API) would mean rewriting only this folder.

## Why this matters here

Before the reorganization (see [`CHANGELOG.md`](./CHANGELOG.md)), everything — UI,
business logic, static data, and API calls — lived in two files totaling ~1400
lines, with no tests. That hid real bugs (duplicated and inconsistent data,
credentials that silently disappeared, no caching at all) that only surfaced
during a line-by-line review. The layering isn't just cosmetic: every bug that got
fixed corresponded to a responsibility that had been tangled up with another one.

## Known limitations (not fixed in this reorganization)

- **Login doesn't actually authenticate** — the password field is never validated
  against anything; the plan tier is inferred from a substring match on the typed
  email. It's decorative.
- **AI/ML agents are mocks** (`omni/application/agents_service.py`) — text
  generated from a fixed template, no real model behind it. They're isolated to
  make a future swap easier, but no real ML/LLM logic was implemented.
