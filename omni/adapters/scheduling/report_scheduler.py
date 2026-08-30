"""Scheduler real do Auto-Pilot.

Antes desta mudança, o painel "Gatilhos de Report" capturava dias/frequência/
horários mas nunca chamava trigger_service.save_trigger_configuration, e não
existia nenhum scheduler (cron/Celery/APScheduler/etc.) -- a geração
"automática" só acontecia quando um humano abria o app. `check_and_dispatch` é
a função pura que decide, para um instante `now`, quais módulos configurados
devem disparar agora e efetivamente despacha nos canais configurados em
Automações; `start_background_scheduler` é o único ponto que toca tempo
real/APScheduler.

Limitação conhecida: isso roda embutido no processo do Streamlit, guardado por
um singleton de módulo -- correto para um deploy de processo único. Em um
deploy com múltiplos processos/workers, cada um teria seu próprio scheduler e
duplicaria o disparo; nesse cenário, defina OMNI_DISABLE_INLINE_SCHEDULER=1 (o
app não inicia o scheduler embutido) e rode `scheduler_worker.py` como um
único processo dedicado.
"""

import logging
from datetime import datetime
from typing import List

from omni.application import automation_service, report_service

logger = logging.getLogger(__name__)

WEEKDAY_NAMES_PT = [
    "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo",
]


def check_and_dispatch(now: datetime, infra) -> List[str]:
    """`infra` é uma omni.composition.Infrastructure (ou qualquer objeto com os
    mesmos atributos/ports) -- todo efeito colateral de rede/banco vem dos
    adapters injetados nela, o que torna esta função testável com fakes.

    Multi-tenant: itera toda organização ativa (`org_repo.list_active_org_ids`)
    e, dentro de cada uma, todo módulo com gatilho configurado -- antes desta
    mudança, quando o conceito de organização não existia, isso lia
    `trigger_repo.load_all()` sem nenhum escopo de tenant."""
    results: List[str] = []
    weekday_name = WEEKDAY_NAMES_PT[now.weekday()]
    current_hm = now.strftime("%H:%M")
    dedup_marker = f"{now.strftime('%Y-%m-%d')} {current_hm}"

    for org_id in infra.org_repo.list_active_org_ids():
        all_configs = infra.trigger_repo.load_all(org_id)

        due_modules = [
            (modulo, config)
            for modulo, config in all_configs.items()
            if weekday_name in config.get("dias_semana", [])
            and current_hm in config.get("horarios", [])
            and config.get("last_dispatched_at") != dedup_marker
        ]
        if not due_modules:
            continue

        # Automação/credenciais são dados por organização, não por módulo --
        # carregados uma vez aqui fora, não a cada módulo (evita reabrir a
        # mesma conexão Postgres 2x quando uma org tem Crypto e TradFi
        # configurados no mesmo tick).
        automation = automation_service.load_automation_settings(infra.automation_repo, org_id)
        credentials = infra.credentials_repo.load(org_id)

        for modulo, config in due_modules:
            tickers = config.get("ativos_selecionados_tickers", [])

            quotes = (
                infra.market_data_port.fetch_quotes(
                    tuple(tickers), brapi_token=credentials.get("brapi_token", infra.settings.brapi_token)
                )
                if tickers
                else {}
            )
            sentiment = infra.sentiment_port.fetch_fear_greed()
            now_str = now.strftime("%d/%m/%Y às %H:%M:%S BRT")
            content = report_service.build_whatsapp_message(now_str, modulo, sentiment, quotes)

            dispatch_log = []

            emails = automation_service.split_targets(automation.auto_emails)
            if emails:
                _, msg = infra.email_port.send(emails, f"OMNI Auto-Pilot Report - {modulo}", content)
                dispatch_log.append(f"email: {msg}")

            for url in automation_service.split_targets(automation.auto_urls):
                _, msg = infra.webhook_port.post(url, {"modulo": modulo, "content": content}, auth_token=automation.crm_api_key)
                dispatch_log.append(f"webhook {url}: {msg}")

            whatsapp_credentials = {
                "instance_id": credentials.get("whatsapp_instance", infra.settings.whatsapp_instance),
                "token": credentials.get("whatsapp_token", infra.settings.whatsapp_token),
            }
            for number in automation_service.split_targets(automation.whatsapp_numbers):
                _, msg = infra.whatsapp_port.send(number, content, whatsapp_credentials)
                dispatch_log.append(f"whatsapp {number}: {msg}")

            telegram_credentials = {"bot_token": credentials.get("telegram_bot_token", infra.settings.telegram_bot_token)}
            for chat_id in automation_service.split_targets(automation.telegram_chat_ids):
                _, msg = infra.telegram_port.send(chat_id, content, telegram_credentials)
                dispatch_log.append(f"telegram {chat_id}: {msg}")

            infra.trigger_repo.mark_dispatched(org_id, modulo, dedup_marker)
            summary = f"[org {org_id[:8]}/{modulo}] disparado às {current_hm}"
            summary += ": " + " | ".join(dispatch_log) if dispatch_log else " (nenhum canal configurado em Automações)."
            results.append(summary)

    return results


_scheduler = None


def start_background_scheduler(infra) -> None:
    global _scheduler
    if _scheduler is not None:
        return
    if infra.settings.disable_inline_scheduler:
        logger.info("Inline Auto-Pilot scheduler disabled via OMNI_DISABLE_INLINE_SCHEDULER=1.")
        return

    from apscheduler.schedulers.background import BackgroundScheduler

    def _tick():
        try:
            for line in check_and_dispatch(datetime.now(), infra):
                logger.info("Auto-Pilot dispatch: %s", line)
        except Exception:
            logger.exception("Auto-Pilot scheduler tick failed")

    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(_tick, "interval", minutes=1, next_run_time=datetime.now())
    _scheduler.start()
    logger.info("OMNI Auto-Pilot scheduler started (checks every minute).")
