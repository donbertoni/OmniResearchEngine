from datetime import datetime

import streamlit as st

from omni.application import automation_service, catalog_service, trigger_service
from omni.application.automation_service import AutomationSettings
from omni.domain import tiers
from omni.domain.models import TierPermissions
from omni.domain.ports import (
    AutomationConfigRepositoryPort,
    CredentialsRepositoryPort,
    OrganizationRepositoryPort,
    TriggerConfigRepositoryPort,
)
from omni.domain.tenancy import LEGACY_ORG_ID

CRM_PLATFORMS = ["HubSpot", "Salesforce", "RD Station", "Outro Webhook/API"]
WEEKDAY_OPTIONS = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]


def render_config_window(
    tr: dict,
    modulo: str,
    active_categories: dict,
    current_asset_pool: list,
    pool_state_key: str,
    permissions: TierPermissions,
    trigger_repo: TriggerConfigRepositoryPort,
    automation_repo: AutomationConfigRepositoryPort,
    credentials_repo: CredentialsRepositoryPort,
    org_repo: OrganizationRepositoryPort,
) -> AutomationSettings:
    # Carregado incondicionalmente (não só quando a janela de Automações está
    # aberta): o botão de CRM Push e o disparo imediato nas Entregas precisam
    # da configuração persistida mesmo com a janela fechada.
    automation_settings = automation_service.load_automation_settings(automation_repo, LEGACY_ORG_ID)

    if not st.session_state.config_window:
        return automation_settings

    with st.container(border=True):
        col_w_title, col_w_close = st.columns([5, 1])
        with col_w_title:
            if st.session_state.config_window == "automations":
                st.subheader(f"⚙️ {tr['auto_config_title']}")
            elif st.session_state.config_window == "triggers":
                st.subheader(f"⚡ {tr['trig_config_title']}")
            elif st.session_state.config_window == "calibration":
                st.subheader(f"🎛️ {tr['calib_config_title']}")
        with col_w_close:
            if st.button(f"❌ {tr['close']}", use_container_width=True):
                st.session_state.config_window = None
                st.rerun()

        if st.session_state.config_window == "automations":
            automation_settings = _render_automations_tab(tr, automation_repo, automation_settings)
        elif st.session_state.config_window == "triggers":
            _render_triggers_tab(tr, modulo, active_categories, permissions, trigger_repo)
        elif st.session_state.config_window == "calibration":
            _render_calibration_tab(
                tr, modulo, active_categories, current_asset_pool, pool_state_key, permissions, credentials_repo, org_repo
            )

    st.markdown("---")
    return automation_settings


def _render_automations_tab(tr: dict, automation_repo: AutomationConfigRepositoryPort, current: AutomationSettings) -> AutomationSettings:
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.markdown(f"**{tr['payload_channels']}**")
        auto_emails = st.text_input(tr["email_notif"], value=current.auto_emails)
        auto_urls = st.text_input(tr["webhooks_url"], value=current.auto_urls)
        whatsapp_numbers = st.text_input(tr["auto_whatsapp_numbers"], value=current.whatsapp_numbers)
        telegram_chat_ids = st.text_input(tr["auto_telegram_chatids"], value=current.telegram_chat_ids)
    with col_a2:
        st.markdown(f"**{tr['crm_integration']}**")
        default_idx = CRM_PLATFORMS.index(current.crm_platform) if current.crm_platform in CRM_PLATFORMS else 0
        crm_platform = st.selectbox(tr["crm_platform"], CRM_PLATFORMS, index=default_idx)
        crm_api_key = st.text_input(tr["crm_apikey"], value=current.crm_api_key, type="password")

    new_settings = AutomationSettings(
        auto_emails=auto_emails,
        auto_urls=auto_urls,
        crm_platform=crm_platform,
        crm_api_key=crm_api_key,
        whatsapp_numbers=whatsapp_numbers,
        telegram_chat_ids=telegram_chat_ids,
    )

    if st.button(tr["save_automations_btn"], use_container_width=True):
        ok, msg = automation_service.save_automation_settings(automation_repo, LEGACY_ORG_ID, new_settings)
        (st.success if ok else st.error)(msg)
        return new_settings

    return current


def _render_triggers_tab(
    tr: dict,
    modulo: str,
    active_categories: dict,
    permissions: TierPermissions,
    trigger_repo: TriggerConfigRepositoryPort,
) -> None:
    saved_config = trigger_service.load_trigger_configuration(trigger_repo, LEGACY_ORG_ID, modulo)

    st.markdown(f"**Módulo Ativo:** `{modulo}`")
    st.markdown(f"**{tr['trig_days_title']}**")
    dias_semana = st.multiselect(
        tr["trig_days_label"],
        options=WEEKDAY_OPTIONS,
        default=saved_config.get("dias_semana", ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"]),
        key=f"trig_days_{modulo}",
    )
    st.markdown("---")
    st.markdown(f"**{tr['trig_freq_title']}**")
    freq_reports = st.slider(
        tr["trig_freq_label"], min_value=1, max_value=5, value=saved_config.get("frequencia", 2), key=f"trig_freq_{modulo}"
    )
    time_cols = st.columns(min(freq_reports, 5))
    default_times_str = saved_config.get("horarios") or ["09:00", "12:00", "15:00", "18:00", "21:00"]
    horarios = []
    for i in range(freq_reports):
        with time_cols[i % len(time_cols)]:
            def_t_str = default_times_str[i] if i < len(default_times_str) else "12:00"
            def_t = datetime.strptime(def_t_str, "%H:%M").time()
            picked = st.time_input(f"Horário Report {i + 1}", value=def_t, key=f"trig_time_{modulo}_{i + 1}")
            horarios.append(picked.strftime("%H:%M"))
    st.markdown("---")

    asset_limit = min(trigger_service.MAX_TRIGGER_ASSETS, permissions.max_free_tickers)
    st.markdown(f"**{tr['trig_assets_title']}**")
    st.caption(tr["trigger_limit_msg"].format(limit=asset_limit))
    all_module_assets = []
    for cat_name, cat_info in active_categories.items():
        for disp_name, ticker, _currency in cat_info["assets"]:
            all_module_assets.append((f"{disp_name} ({ticker}) — [{cat_name}]", ticker))
    label_to_ticker = dict(all_module_assets)
    asset_labels = [item[0] for item in all_module_assets]
    saved_labels = saved_config.get("ativos_selecionados_labels", [])
    default_labels = [lbl for lbl in saved_labels if lbl in asset_labels] or asset_labels[: min(5, len(asset_labels), asset_limit)]
    ativos_selecionados_labels = st.multiselect(
        tr["trig_assets_label"],
        options=asset_labels,
        max_selections=max(asset_limit, 0) or None,
        default=default_labels[:asset_limit] if asset_limit else [],
        key=f"trig_assets_{modulo}",
        disabled=asset_limit == 0,
    )

    if st.button(tr["save_triggers_btn"], use_container_width=True, key=f"save_triggers_{modulo}"):
        config_data = {
            "dias_semana": dias_semana,
            "frequencia": freq_reports,
            "horarios": horarios,
            "ativos_selecionados_labels": ativos_selecionados_labels,
            "ativos_selecionados_tickers": [label_to_ticker[lbl] for lbl in ativos_selecionados_labels if lbl in label_to_ticker],
            "max_free_tickers": permissions.max_free_tickers,
        }
        ok, msg = trigger_service.save_trigger_configuration(trigger_repo, LEGACY_ORG_ID, modulo, config_data)
        (st.success if ok else st.error)(msg)


def _render_calibration_tab(
    tr: dict,
    modulo: str,
    active_categories: dict,
    current_asset_pool: list,
    pool_state_key: str,
    permissions: TierPermissions,
    credentials_repo: CredentialsRepositoryPort,
    org_repo: OrganizationRepositoryPort,
) -> None:
    with st.form("calibration_form"):
        st.markdown(f"### {tr['calib_creds']}")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            brapi_token_input = st.text_input(tr["brapi_token"], value=st.session_state.get("brapi_token", ""), type="password")
            telegram_token_input = st.text_input(
                tr["telegram_bot_token_label"], value=st.session_state.get("telegram_bot_token", ""), type="password"
            )
        with col_c2:
            whatsapp_instance_input = st.text_input(tr["whatsapp_inst"], value=st.session_state.get("whatsapp_instance", ""))
            whatsapp_token_input = st.text_input(tr["whatsapp_token"], value=st.session_state.get("whatsapp_token", ""), type="password")

        if brapi_token_input and (" " in brapi_token_input or any(c in brapi_token_input for c in "\"'")):
            st.warning(tr["brapi_token_invalid"])

        company_name_input, cnpi_code_input = "", ""
        if permissions.allow_white_label:
            st.markdown("---")
            st.markdown(f"### {tr['white_label_title']}")
            current_org = org_repo.get_by_id(LEGACY_ORG_ID)
            col_wl1, col_wl2 = st.columns(2)
            with col_wl1:
                company_name_input = st.text_input(
                    tr["company_name_label"], value=(current_org.company_name if current_org else "")
                )
            with col_wl2:
                cnpi_code_input = st.text_input(
                    tr["cnpi_code_label"], value=(current_org.cnpi_code if current_org else "")
                )

        if not permissions.allow_customization:
            st.warning(tr["tier_locked_msg"].format(tier=tiers.FREE))
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            submitted_calib = st.form_submit_button(tr["save_params"], use_container_width=True)
            if submitted_calib:
                _save_credentials(credentials_repo, brapi_token_input, whatsapp_instance_input, whatsapp_token_input, telegram_token_input)
                st.toast("Credenciais atualizadas com sucesso!", icon="✅")
                st.session_state.config_window = None
                st.rerun()
            return

        st.markdown("---")
        st.markdown(f"### {tr['calib_assets']}")
        st.caption(tr["calib_assets_caption"])

        st.markdown(f"#### {tr['add_new_asset']}")
        col_na1, col_na2, col_na3 = st.columns(3)
        with col_na1:
            st.text_input(tr["friendly_name"], value="", placeholder="Ex: Ethereum", key="form_new_asset_name")
        with col_na2:
            st.text_input(tr["ticker_input"], value="", placeholder="Ex: ETH-USD", key="form_new_asset_ticker")
        with col_na3:
            st.selectbox(tr["currency_input"], ["$", "R$"], key="form_new_asset_curr")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        st.markdown(f"#### {tr['manage_assets']}")
        st.caption(tr["manage_assets_caption"])

        pool_labels_map = {f"{disp} ({tk}) [{cur}]": (disp, tk, cur) for disp, tk, cur in current_asset_pool}
        default_pool_labels = list(pool_labels_map.keys())

        st.multiselect(
            tr["pool_assets_label"],
            options=default_pool_labels,
            default=default_pool_labels,
            key=f"form_pool_multiselect_{modulo}",
        )

        st.markdown("---")
        st.markdown(f"### {tr['calib_cats']}")
        st.caption(tr["calib_cats_caption"])

        cat_action_mode = st.selectbox(tr["cat_action"], ["Gerenciar/Editar Existente", "Criar Nova Categoria"], key="form_cat_action_mode")

        cat_to_edit = None
        if cat_action_mode == "Criar Nova Categoria":
            st.text_input(tr["new_cat_name"], value="", placeholder="Ex: 9 - DeFi & Web3", key="form_new_cat_name")
            st.text_input(tr["new_cat_tag"], value="", placeholder="Ex: DeFi", key="form_new_cat_tag")
            pool_options = [f"{d} ({t}) [{c}]" for d, t, c in current_asset_pool]
            st.multiselect(tr["new_cat_assets"], options=pool_options, key="form_new_cat_assets_sel")
        else:
            cat_to_edit = st.selectbox(tr["cat_to_manage"], list(active_categories.keys()), key="calib_sel_cat")
            if cat_to_edit:
                c_data = active_categories[cat_to_edit]
                st.text_input(tr["rename_cat"], value=cat_to_edit, key="calib_rename_cat")
                current_cat_tickers = {t for _, t, _ in c_data["assets"]}
                pool_options = [f"{d} ({t}) [{c}]" for d, t, c in current_asset_pool]
                default_selected_pool = [f"{d} ({t}) [{c}]" for d, t, c in current_asset_pool if t in current_cat_tickers]
                st.multiselect(
                    tr["edit_cat_assets"],
                    options=pool_options,
                    default=default_selected_pool,
                    key=f"form_edit_cat_assets_sel_{cat_to_edit}",
                )
                st.checkbox(tr["delete_cat_flag"], value=False, key=f"form_delete_cat_{cat_to_edit}")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        submitted_calib = st.form_submit_button(tr["save_params"], use_container_width=True)

        if submitted_calib:
            _apply_calibration_submit(
                modulo,
                active_categories,
                pool_state_key,
                pool_labels_map,
                cat_action_mode,
                cat_to_edit,
                brapi_token_input,
                whatsapp_instance_input,
                whatsapp_token_input,
                telegram_token_input,
                credentials_repo,
                org_repo,
                company_name_input,
                cnpi_code_input,
            )


def _save_credentials(credentials_repo, brapi_token_input, whatsapp_instance_input, whatsapp_token_input, telegram_token_input) -> None:
    """Compartilhado entre o form completo de Calibragem e o form reduzido do
    tier Free (só credenciais) -- antes duplicado byte a byte nos dois."""
    st.session_state.brapi_token = brapi_token_input
    st.session_state.whatsapp_instance = whatsapp_instance_input
    st.session_state.whatsapp_token = whatsapp_token_input
    st.session_state.telegram_bot_token = telegram_token_input
    credentials_repo.save(LEGACY_ORG_ID, {
        "brapi_token": brapi_token_input,
        "whatsapp_instance": whatsapp_instance_input,
        "whatsapp_token": whatsapp_token_input,
        "telegram_bot_token": telegram_token_input,
    })


def _apply_calibration_submit(
    modulo: str,
    active_categories: dict,
    pool_state_key: str,
    pool_labels_map: dict,
    cat_action_mode: str,
    cat_to_edit: str,
    brapi_token_input: str,
    whatsapp_instance_input: str,
    whatsapp_token_input: str,
    telegram_token_input: str,
    credentials_repo: CredentialsRepositoryPort,
    org_repo: OrganizationRepositoryPort,
    company_name_input: str,
    cnpi_code_input: str,
) -> None:
    selected_pool_labels = st.session_state.get(f"form_pool_multiselect_{modulo}", [])
    updated_pool = catalog_service.apply_pool_selection(pool_labels_map, selected_pool_labels)

    n_name = st.session_state.get("form_new_asset_name", "").strip()
    n_tk = st.session_state.get("form_new_asset_ticker", "").strip().upper()
    n_cur = st.session_state.get("form_new_asset_curr", "$")
    updated_pool = catalog_service.add_asset_to_pool(updated_pool, n_name, n_tk, n_cur)

    st.session_state[pool_state_key] = updated_pool
    st.session_state[f"{pool_state_key}_dirty"] = True
    label_to_tuple = {f"{d} ({t}) [{c}]": (d, t, c) for d, t, c in updated_pool}

    if cat_action_mode == "Criar Nova Categoria":
        n_cat_n = st.session_state.get("form_new_cat_name", "").strip()
        n_cat_t = st.session_state.get("form_new_cat_tag", "").strip()
        chosen_labels = st.session_state.get("form_new_cat_assets_sel", [])
        chosen_tuples = [label_to_tuple[lbl] for lbl in chosen_labels if lbl in label_to_tuple]
        active_categories = catalog_service.upsert_new_category(active_categories, n_cat_n, n_cat_t, chosen_tuples)
    elif cat_to_edit:
        if st.session_state.get(f"form_delete_cat_{cat_to_edit}", False):
            active_categories = catalog_service.delete_category(active_categories, cat_to_edit)
        else:
            # Importante: a leitura de `chosen_labels` usa a key montada com o
            # cat_to_edit ORIGINAL (o mesmo usado ao renderizar o widget). O código
            # original lia essa key só depois de já ter renomeado a categoria, o que
            # fazia a seleção de ativos ser perdida (voltava a [] por default) toda
            # vez que um rename acontecia junto com uma edição de ativos.
            chosen_labels = st.session_state.get(f"form_edit_cat_assets_sel_{cat_to_edit}", [])
            chosen_tuples = [label_to_tuple[lbl] for lbl in chosen_labels if lbl in label_to_tuple]

            target_cat_name = st.session_state.get("calib_rename_cat", cat_to_edit)
            renamed = catalog_service.rename_category(active_categories, cat_to_edit, target_cat_name)
            active_categories = catalog_service.set_category_assets(active_categories, renamed, chosen_tuples)

    if modulo == "Crypto":
        st.session_state.custom_active_categories_crypto = active_categories
    else:
        st.session_state.custom_active_categories_tradfi = active_categories
    st.session_state[f"categories_{modulo}_dirty"] = True

    _save_credentials(credentials_repo, brapi_token_input, whatsapp_instance_input, whatsapp_token_input, telegram_token_input)

    if company_name_input or cnpi_code_input:
        org_repo.update(LEGACY_ORG_ID, {"company_name": company_name_input, "cnpi_code": cnpi_code_input})

    st.toast("Parâmetros atualizados com sucesso!", icon="✅")
    st.session_state.config_window = None
    st.rerun()
