"""Processo dedicado para o scheduler do Auto-Pilot.

Use isso (em vez do scheduler embutido no processo do Streamlit) quando o
deploy roda múltiplos processos/workers do app -- nesse caso, defina
OMNI_DISABLE_INLINE_SCHEDULER=1 para que o app não duplique o disparo, e rode
este worker como um único processo separado (ex: outro serviço/dyno/container).

Uso: `python scheduler_worker.py`
"""

import logging
import time
from datetime import datetime

from omni.adapters.scheduling.report_scheduler import check_and_dispatch
from omni.composition import build_infrastructure

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("omni.scheduler_worker")


def main() -> None:
    infra = build_infrastructure()
    logger.info("OMNI Auto-Pilot worker started (Postgres=%s). Checking every 60s.", infra.using_postgres)
    while True:
        try:
            for line in check_and_dispatch(datetime.now(), infra):
                logger.info(line)
        except Exception:
            logger.exception("Scheduler tick failed")
        time.sleep(60)


if __name__ == "__main__":
    main()
