"""Agentes de IA/ML do terminal.

STUB: nenhuma das funções abaixo chama um modelo de ML ou LLM real. Elas reproduzem
o comportamento simulado que já existia no app original (texto fixo/gerado por
template), só que isoladas aqui para que uma implementação real possa substituí-las
no futuro sem tocar na camada de UI.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def default_prediction_logs() -> list:
    return [
        {"timestamp": "21/08/2026 18:00", "asset": "BTC-USD", "prediction": "Alta (Bullish)", "confidence": "78.4%", "status": "Acerto ✅"},
        {"timestamp": "20/08/2026 12:00", "asset": "ES=F", "prediction": "Neutro / Consolidação", "confidence": "82.1%", "status": "Acerto ✅"},
    ]


def generate_script(lang_key: str, target_asset: str, tone: str, price: float, change: float) -> str:
    logger.debug("agents_service.generate_script is a stub - no real LLM is called")
    return f"""[OMNI AGENT SCRIPTWRITER - {lang_key}]
Asset: {target_asset} | Price: {price} | Change: {change}%
Tone: {tone}
--------------------------------------------------
[00:00 - Intro]: Welcome investors, OMNI Research delivering high-performance insights for {target_asset}.
[00:30 - Core Analysis]: The asset registers a variation of {change}%, backed by recent institutional flows.
[01:15 - Conclusion]: Keep your technical stops calibrated according to previous reports.
"""


def run_ml_inference(asset: str) -> dict:
    logger.debug("agents_service.run_ml_inference is a stub - no real model is called")
    return {
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "asset": asset,
        "prediction": "Alta Direcional (Momentum Positivo)",
        "confidence": "81.9%",
        "status": "Em Monitoramento 🔄",
    }


def run_ta_scan(asset: str, timeframe: str) -> dict:
    logger.debug("agents_service.run_ta_scan is a stub - no real chart pattern scan is performed")
    return {
        "asset": asset,
        "timeframe": timeframe,
        "pattern": "Potencial *Cup and Handle* em formação",
        "breakout_level": "$78,500.00 (Crypto) / 5,950.00 pts (TradFi)",
        "targets": ["$82,000.00", "$86,500.00", "$92,000.00"],
        "stop_loss": "$74,800.00",
    }
