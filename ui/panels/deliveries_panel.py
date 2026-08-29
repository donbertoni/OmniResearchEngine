import streamlit as st

from omni.application import report_service
from omni.domain.ports import ReportExporterPort


def render_deliveries_panel(
    tr: dict,
    modulo: str,
    lang_key: str,
    now_str: str,
    company_name: str,
    cnpi_code: str,
    sentiment,
    active_display_categories: dict,
    quotes: dict,
    fmt_b2b: bool,
    fmt_yt: bool,
    fmt_wapp: bool,
    fmt_tg: bool,
    crm_platform: str,
    pdf_exporter: ReportExporterPort,
) -> None:
    st.subheader(f"📋 {tr['deliveries']}")
    st.caption(tr["deliveries_caption"])

    outputs_generated = []

    if fmt_b2b:
        content = report_service.build_b2b_report(
            modulo,
            company_name,
            cnpi_code,
            now_str,
            lang_key,
            sentiment,
            active_display_categories,
            quotes,
            is_category_enabled=lambda cat: st.session_state.get(f"chk_cat_{cat}", True),
            is_asset_enabled=lambda cat, ticker: st.session_state.get(f"chk_asset_{cat}_{ticker}", True),
        )
        outputs_generated.append(("B2B (Analytical Report)", content))

    if fmt_yt:
        outputs_generated.append(("B2C (YouTube)", report_service.build_youtube_script(now_str, modulo)))
    if fmt_wapp:
        outputs_generated.append(("B2C (WhatsApp)", report_service.build_whatsapp_message(now_str)))
    if fmt_tg:
        outputs_generated.append(("B2C (Telegram)", report_service.build_telegram_message(now_str)))

    if not outputs_generated:
        st.info("No output format selected in sidebar.")
        primary_output_text = "No content generated."
    else:
        if len(outputs_generated) == 1:
            title_out, primary_output_text = outputs_generated[0]
            st.text_area(title_out, value=primary_output_text, height=380)
        else:
            tabs = st.tabs([item[0] for item in outputs_generated])
            for idx, (title_out, content_text) in enumerate(outputs_generated):
                with tabs[idx]:
                    st.text_area(f"View {title_out}", value=content_text, height=350, key=f"txt_area_{idx}")
            primary_output_text = outputs_generated[0][1]

    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    with col_b1:
        st.download_button(
            "📥 TXT", data=primary_output_text, file_name=f"OMNI_Report_{modulo}_{lang_key}.txt",
            mime="text/plain", use_container_width=True,
        )
    with col_b2:
        json_data = report_service.export_to_json(modulo, lang_key, now_str, primary_output_text)
        st.download_button(
            "📥 JSON", data=json_data, file_name=f"OMNI_Report_{modulo}_{lang_key}.json",
            mime="application/json", use_container_width=True,
        )
    with col_b3:
        pdf_bytes = report_service.export_to_pdf(pdf_exporter, primary_output_text, company_name, now_str)
        st.download_button(
            "📥 PDF", data=pdf_bytes, file_name=f"OMNI_Report_{modulo}_{lang_key}.pdf",
            mime="application/pdf", use_container_width=True,
        )
    with col_b4:
        if st.button("🚀 CRM Push", use_container_width=True):
            st.toast(f"Autonomous payload dispatched via {crm_platform}!", icon="🎯")
