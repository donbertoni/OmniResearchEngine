# Fonte única de dados de catálogo (categorias e benchmarks).
#
# Antes desta reorganização, app.py e backend.py definiam CATEGORIES_TRADFI de forma
# duplicada e divergente (ex: o ticker da Totvs era "TOTVS3.SA" em um arquivo e
# "TOTS3.SA" no outro). O ticker correto na B3 é TOTS3, por isso é o valor mantido aqui.
CATEGORIES_TRADFI = {
    "1 - Bancos e Seguradoras": {
        "tag": "Banks",
        "assets": [
            ("Itaú Unibanco", "ITUB4.SA", "R$"),
            ("Banco do Brasil", "BBAS3.SA", "R$"),
            ("Bradesco PN", "BBDC4.SA", "R$"),
            ("BB Seguridade", "BBSE3.SA", "R$"),
        ],
    },
    "2 - Energia": {
        "tag": "Energy",
        "assets": [
            ("Petrobras PN", "PETR4.SA", "R$"),
            ("Petróleo Rio", "PRIO3.SA", "R$"),
            ("Equatorial", "EQTL3.SA", "R$"),
            ("CPFL Energia", "CPFE3.SA", "R$"),
        ],
    },
    "3 - Tech": {
        "tag": "Tech",
        "assets": [
            ("Totvs", "TOTS3.SA", "R$"),
            ("NVIDIA Corp", "NVDA", "$"),
            ("Apple Inc", "AAPL", "$"),
            ("Microsoft", "MSFT", "$"),
        ],
    },
    "4 - Commodities": {
        "tag": "Commodities",
        "assets": [
            ("Vale ON", "VALE3.SA", "R$"),
            ("Gerdau", "GGBR4.SA", "R$"),
            ("Cemig", "CMIG4.SA", "R$"),
            ("Klabin", "KLBN11.SA", "R$"),
        ],
    },
    "5 - Varejo": {
        "tag": "Retail",
        "assets": [
            ("Assaí", "ASAI3.SA", "R$"),
            ("Lojas Renner", "LREN3.SA", "R$"),
            ("Magazine Luiza", "MGLU3.SA", "R$"),
            ("RaiaDrogasil", "RADL3.SA", "R$"),
        ],
    },
    "6 - Logística e Infra.": {
        "tag": "Logistics",
        "assets": [
            ("Rumo", "RAIL3.SA", "R$"),
            ("Weg", "WEGE3.SA", "R$"),
            ("CCR", "CCRO3.SA", "R$"),
            ("Embraer", "EMBR3.SA", "R$"),
        ],
    },
    "7 - Agro e Indústria": {
        "tag": "Agro",
        "assets": [
            ("SLC Agrícola", "SLCE3.SA", "R$"),
            ("BRF", "BRFS3.SA", "R$"),
            ("Ambev", "ABEV3.SA", "R$"),
            ("JBS", "JBSS3.SA", "R$"),
        ],
    },
    "8 - FIIs e Imobiliário": {
        "tag": "Real Estate",
        "assets": [
            ("HGLG11", "HGLG11.SA", "R$"),
            ("KNRI11", "KNRI11.SA", "R$"),
            ("XPLG11", "XPLG11.SA", "R$"),
            ("MXRF11", "MXRF11.SA", "R$"),
        ],
    },
}

MACRO_BENCHMARKS = [
    {"key": "SPX", "ticker": "^GSPC", "label": "1. S&P 500 / SPX", "unit": "pts", "prefix": "", "badge": "Direct API"},
    {"key": "IBOV", "ticker": "^BVSP", "label": "2. Ibovespa / IBOV", "unit": "pts", "prefix": "", "badge": "Direct API"},
    {"key": "BRENT", "ticker": "BZ=F", "label": "3. Petróleo Brent", "unit": "USD", "prefix": "$ ", "badge": "Direct API"},
    {"key": "GOLD", "ticker": "GC=F", "label": "4. Ouro Spot", "unit": "USD", "prefix": "$ ", "badge": "Direct API"},
    {"key": "USDBRL", "ticker": "BRL=X", "label": "5. USD / BRL / Dólar Real", "unit": "pts", "prefix": "R$ ", "badge": "Direct API"},
]

CATEGORIES_CRYPTO = {
    "1 - ETFs": {
        "tag": "ETFs",
        "assets": [("IBIT (BlackRock)", "IBIT", "$"), ("FBTC (Fidelity)", "FBTC", "$"), ("ETHA (Ethereum)", "ETHA", "$"), ("BITO (Futures)", "BITO", "$")],
    },
    "2 - Treasury": {
        "tag": "Treasury",
        "assets": [("MicroStrategy", "MSTR", "$"), ("Marathon Digital", "MARA", "$"), ("Riot Platforms", "RIOT", "$"), ("Coinbase Global", "COIN", "$")],
    },
    "3 - Mineração e Hashrate": {
        "tag": "Mining",
        "assets": [("CleanSpark", "CLSK", "$"), ("Hut 8", "HUT", "$"), ("Bitfarms", "BITF", "$"), ("Iris Energy", "IREN", "$")],
    },
    "4 - Volume Spot (24 hs)": {
        "tag": "Spot Vol",
        "assets": [("BTCUSDT", "BTC-USD", "$"), ("ETHUSDT", "ETH-USD", "$"), ("SOLUSDT", "SOL-USD", "$"), ("BNBUSDT", "BNB-USD", "$")],
    },
    "5 - Volume Futuros (24 hs)": {
        "tag": "Derivatives",
        "assets": [("BTC Perp", "BTC-USD", "$"), ("ETH Perp", "ETH-USD", "$"), ("SOL Perp", "SOL-USD", "$"), ("BNB Perp", "BNB-USD", "$")],
    },
    "6 - Open Interest": {
        "tag": "Open Interest",
        "assets": [("BTC OI Base", "BTC-USD", "$"), ("ETH OI Base", "ETH-USD", "$"), ("SOL OI Base", "SOL-USD", "$"), ("AVAX OI Base", "AVAX-USD", "$")],
    },
    "7 - DeFi e Layer 1s": {
        "tag": "DeFi & L1",
        "assets": [("UNI (Uniswap)", "UNI7083-USD", "$"), ("AAVE (Aave)", "AAVE-USD", "$"), ("LINK (Chainlink)", "LINK-USD", "$"), ("AVAX (Avalanche)", "AVAX-USD", "$")],
    },
    "8 - Stablecoins": {
        "tag": "Stablecoins",
        "assets": [("USDT / USD", "USDT-USD", "$"), ("USDC / USD", "USDC-USD", "$"), ("USDT / BRL", "BRL=X", "R$"), ("DAI / USD", "DAI-USD", "$")],
    },
}

CRYPTO_BENCHMARKS = [
    {"key": "BTC", "ticker": "BTC-USD", "label": "1. Bitcoin / BTC", "prefix": "$ ", "badge": "Direct API"},
    {"key": "ETH", "ticker": "ETH-USD", "label": "2. Ethereum / ETH", "prefix": "$ ", "badge": "Direct API"},
    {"key": "BTC_D", "type": "global_api", "sub_key": "btc_d", "label": "3. Bitcoin Dominance / BTC.D", "badge": "CoinGecko API"},
    {"key": "USDT_D", "type": "global_api", "sub_key": "usdt_d", "label": "4. Tether Dominance / USDT.D", "badge": "CoinGecko API"},
    {"key": "FEAR_GREED", "type": "fng_api", "label": "5. Bitcoin Fear & Greed Index", "badge": "Alternative.me API"},
]


def build_initial_asset_pool(categories: dict) -> list:
    """Achata as categorias num pool de ativos únicos, preservando a primeira ocorrência de cada ticker."""
    pool = []
    seen = set()
    for cat_info in categories.values():
        for disp, ticker, currency in cat_info["assets"]:
            if ticker not in seen:
                pool.append((disp, ticker, currency))
                seen.add(ticker)
    return pool


def get_asset_source(ticker: str) -> str:
    return "BRAPI" if ".SA" in ticker else "Yahoo"


def get_benchmark_source(item: dict) -> str:
    if item.get("type") == "fng_api":
        return "Alternative.me"
    if item.get("type") == "global_api":
        return "CoinGecko"
    return "Yahoo"
