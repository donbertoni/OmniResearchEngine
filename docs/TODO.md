# Gaps Funcionais & To-Dos

Lista do que a UI do app hoje *dá a entender* que faz mas na verdade não faz (ou só
faz pela metade), encontrada durante a reorganização do código (ver
[`ARCHITECTURE.md`](./ARCHITECTURE.md) e [`CHANGELOG.md`](./CHANGELOG.md)). É sobre
comportamento faltando/incompleto, não sobre estilo de código.

Legenda de prioridade:
- **P0** — quebra uma promessa central do produto (Auto-Pilot, entrega automática).
- **P1** — uma feature visível não faz nada ou faz a coisa errada silenciosamente.
- **P2** — funciona, mas incompleto ou sem rede de segurança.
- **P3** — menor / limpeza, baixo impacto pro usuário.

## P0 — A promessa central de "Auto-Pilot" não está implementada

- [ ] **Gatilhos de Report não disparam nada.** O painel "Gatilhos de Report"
  (dias da semana, frequência, horários, ativos monitorados) renderiza e captura
  input, mas não tem botão de salvar e nunca chama
  `trigger_service.save_trigger_configuration`. `JsonTriggerConfigRepository` e
  `trigger_service.py` existem e têm teste, mas estão completamente desconectados —
  nada lê essa configuração de volta, e não existe nenhum scheduler
  (cron/Celery/APScheduler/etc.) que dispararia um relatório nos horários
  configurados. Hoje, a geração "automática" de relatório só acontece quando um
  humano abre o app e olha o dashboard.
- [ ] **Nenhum canal de entrega envia algo automaticamente.** Mesmo que existisse
  um agendamento, não há nenhum job que chamaria o `report_service` + empurraria o
  resultado pra e-mail/CRM/WhatsApp/Telegram sem um humano clicar num botão antes.

## P1 — Feature visível não faz nada ou finge que fez

- [ ] **Login não autentica de verdade.** O campo de senha nunca é validado; o
  tier do plano é inferido por substring do e-mail digitado
  (`admin`/`white`/`free`). Qualquer um pode digitar `admin@x.com` e ganhar o tier
  Premium White-Label. Ok pra demo, não ok se isso deveria travar feature paga.
- [ ] **Permissões de tier são calculadas mas nunca aplicadas.**
  `catalog_service.tier_permissions()` retorna `allow_customization` e
  `max_free_tickers`, mas nada na UI de fato bloqueia um usuário "Free" de
  customizar categorias ou adicionar tickers ilimitados. O gate existe só no papel.
- [ ] **Botão CRM Push não empurra nada.** Clicar nele só mostra um toast
  ("Autonomous payload dispatched via {crm_platform}!"). Nenhuma requisição HTTP é
  feita, nenhum webhook é chamado, apesar do painel de Automações coletar
  plataforma de CRM, API key e URLs de webhook exatamente pra isso.
- [ ] **Campos do painel de Automações são capturados mas nunca usados.** E-mails
  e URLs de webhook digitados no painel de Automações não são salvos em lugar
  nenhum e nada nunca envia e-mail ou faz POST pra um webhook.
- [ ] **Saída de Telegram é um placeholder estático.** `build_telegram_message`
  sempre retorna as mesmas duas linhas independente de módulo/cotações/sentimento
  — não existe integração nenhuma com a API de Bot do Telegram, diferente do
  WhatsApp que ao menos tem um adapter real agora (mesmo que desconfigurado por
  padrão).
- [ ] **YouTube Auto-Pilot (IA Diretora de Arte) é 100% mock de UI.** Selecionar
  template/voz/visibilidade e clicar em "Renderizar e Disparar" só mostra um toast
  de sucesso. Nenhum vídeo é renderizado, nenhum TTS roda, nada é publicado no
  YouTube.

## P2 — Funciona, mas incompleto ou inseguro

- [ ] **Agentes de IA/ML são simulados.** Os agentes Roteirista, Preditivo (ML) e
  Análise Técnica (`omni/application/agents_service.py`) retornam
  texto/valores de template fixo, não saída real de modelo. Já marcados como
  `STUB` explícito no código — listado aqui também como gap de produto, não só
  comentário de código.
- [ ] **Falha de adapter é invisível pro usuário final.** Falhas de rede/API agora
  são logadas (`logging.warning`, antes eram engolidas em silêncio), mas a UI
  ainda só mostra `0`/`--` sem nenhum aviso visível tipo "BRAPI está fora" ou
  "Order book da Deribit indisponível, mostrando dado sintético." O usuário não
  consegue distinguir dado real de valor de fallback hardcoded.
- [ ] **Estado não sobrevive a um restart do app.** Pools de ativos, categorias
  customizadas e logs de predição de ML vivem só em `st.session_state` (por
  sessão/processo do navegador). Reiniciar o processo do Streamlit ou a sessão de
  um usuário apaga qualquer customização.
- [ ] **Sem CI automatizado.** A suíte de `pytest` existe mas nada roda ela
  automaticamente em push/PR — uma regressão pode ser mergeada silenciosamente.

## P3 — Menor / limpeza

- [ ] **`custom_data_api_key` é um campo morto.** Capturado no formulário de
  Calibragem e passado adiante em
  `MarketDataPort.fetch_quotes(..., custom_api_key=...)`, mas nenhum adapter lê
  esse valor. Ou conecta em algo, ou remove o campo.
- [ ] **Sem validação de input no campo de token BRAPI.** `BrapiMarketDataAdapter`
  remove um possível prefixo `token=` defensivamente, mas não há feedback pro
  usuário se o token estiver malformado/inválido — ele só falha silenciosamente
  ao buscar cotações da B3.
- [ ] **Checkbox "Manter-se conectado" é decorativo.** Sem persistência de sessão
  além do que o próprio Streamlit já faz pra aba do navegador.
- [ ] **Sem lista documentada das variáveis de ambiente.**
  `omni/config/settings.py` lê `BRAPI_TOKEN`, `CUSTOM_DATA_API_KEY`,
  `WHATSAPP_INSTANCE_ID`, `WHATSAPP_TOKEN`, `WHATSAPP_API_BASE_URL`, mas isso não
  está escrito em lugar nenhum fora do código-fonte (ex: um `.env.example`).
