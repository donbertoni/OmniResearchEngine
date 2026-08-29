from omni.domain.models import LiquidityData
from omni.domain.ports import LiquidityDataPort


def get_liquidity_heatmap(
    modulo: str,
    base_price: float,
    crypto_port: LiquidityDataPort,
    tradfi_port: LiquidityDataPort,
) -> LiquidityData:
    port = crypto_port if modulo == "Crypto" else tradfi_port
    return port.fetch_liquidity_data(base_price)
