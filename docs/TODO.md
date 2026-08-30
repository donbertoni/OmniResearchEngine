# Gaps Funcionais & To-Dos

**2026-08-29 (mais recente):** decisão tomada de virar produto multi-tenant
vendável (não mais ferramenta interna single-tenant) — ver
[`ARCHITECTURE.md`](./ARCHITECTURE.md#multi-tenancy) para o desenho e o
roadmap faseado (Fase 0: schema multi-tenant + Alembic + auth real, já
concluída; Fase 1: FastAPI + Next.js atingindo paridade com o Streamlit,
painel por painel; Fase 2: RBAC completo, billing via Stripe, Sentry, RLS;
Fase 3: SSO, domínio customizado por cliente, só então revisitar os itens
"Deferred" abaixo). O Streamlit continua rodando normalmente durante as Fases
0/1 (migração incremental, não big-bang).

Lista do que a UI do app hoje *dá a entender* que faz mas na verdade não faz (ou só
faz pela metade), encontrada durante a reorganização do código (ver
[`ARCHITECTURE.md`](./ARCHITECTURE.md) e [`CHANGELOG.md`](./CHANGELOG.md)). É sobre
comportamento faltando/incompleto, não sobre estilo de código.

**Atualização 2026-08-29:** todos os itens P0-P3 abaixo foram fechados nesta
rodada (ver entrada correspondente no CHANGELOG) — persistência real via
Postgres (com fallback local em JSON), scheduler de Auto-Pilot de verdade, login
real, tiers aplicados, e integrações reais de CRM/webhook/e-mail/WhatsApp/
Telegram. Os únicos dois itens que ficaram de fora estão na seção "Deferred" no
fim deste arquivo — ambos exigem uma decisão de produto/modelo própria, não só
plumbing.

Legenda de prioridade:
- **P0** — quebra uma promessa central do produto (Auto-Pilot, entrega automática).
- **P1** — uma feature visível não faz nada ou faz a coisa errada silenciosamente.
- **P2** — funciona, mas incompleto ou sem rede de segurança.
- **P3** — menor / limpeza, baixo impacto pro usuário.

## P0 — A promessa central de "Auto-Pilot" não está implementada

- [x] **Gatilhos de Report não disparam nada.** Resolvido: o painel agora tem um
  botão de salvar de verdade (`trigger_service.save_trigger_configuration`,
  persistido via Postgres/JSON) e `omni/adapters/scheduling/report_scheduler.py`
  (APScheduler, checando a cada minuto) dispara o report nos dias/horários
  configurados.
- [x] **Nenhum canal de entrega envia algo automaticamente.** Resolvido: o
  scheduler chama de verdade `report_service` + os adapters de e-mail (SMTP),
  webhook genérico, WhatsApp e Telegram configurados em Automações.

## P1 — Feature visível não faz nada ou finge que fez

- [x] **Login não autentica de verdade.** Resolvido: `auth_service.py` valida
  senha via hash PBKDF2; tier vem do usuário persistido, não de substring do
  e-mail.
- [x] **Permissões de tier são calculadas mas nunca aplicadas.** Resolvido: Free
  tier não abre mais o formulário de customização da Calibragem; o seletor de
  ativos monitorados nos Gatilhos é limitado a `max_free_tickers`.
- [x] **Botão CRM Push não empurra nada.** Resolvido: `GenericWebhookAdapter` faz
  um POST HTTP de verdade para as URLs configuradas em Automações, com o
  resultado real (sucesso/falha por URL) exibido na UI.
- [x] **Campos do painel de Automações são capturados mas nunca usados.**
  Resolvido: persistidos via `AutomationConfigRepositoryPort` e lidos de volta
  tanto pelo disparo manual quanto pelo scheduler.
- [x] **Saída de Telegram é um placeholder estático.** Resolvido:
  `TelegramNotificationAdapter` chama a API real de Bot do Telegram; o conteúdo
  da mensagem agora usa sentimento/cotação reais, igual ao WhatsApp.
- [ ] **YouTube Auto-Pilot (IA Diretora de Arte) é 100% mock de UI.** Ver seção
  "Deferred" no fim deste arquivo.

## P2 — Funciona, mas incompleto ou inseguro

- [ ] **Agentes de IA/ML são simulados.** Ver seção "Deferred" no fim deste
  arquivo.
- [x] **Falha de adapter é invisível pro usuário final.** Resolvido:
  `dashboard_service.fetch_dashboard_snapshot` agora retorna `warnings`, exibido
  como um banner explícito no dashboard listando quais símbolos vieram sem
  cotação real.
- [x] **Estado não sobrevive a um restart do app.** Resolvido: pools de ativos,
  categorias customizadas, logs de predição de ML, credenciais, config de
  gatilhos/automações e usuários agora persistem via Postgres (ou JSON local
  como fallback single-processo) em vez de só `st.session_state`.
- [x] **Sem CI automatizado.** Resolvido: `.github/workflows/ci.yml` roda
  `pytest` em todo push/PR.

## P3 — Menor / limpeza

- [x] **`custom_data_api_key` é um campo morto.** Resolvido: removido de ponta a
  ponta (nenhum adapter tinha implementação real pra ele).
- [x] **Sem validação de input no campo de token BRAPI.** Resolvido: a
  Calibragem mostra um aviso visível quando o token tem espaços/aspas suspeitas.
- [x] **Checkbox "Manter-se conectado" é decorativo.** Resolvido: persiste um
  token assinado (HMAC) que sobrevive a um refresh da mesma aba/link — ver
  `session_token_service.py` para o limite real documentado (não é um cookie
  cross-device).
- [x] **Sem lista documentada das variáveis de ambiente.** Resolvido:
  `.env.example` na raiz do projeto.

## Deferred (fora do escopo desta rodada — decisão de produto/modelo, não bug fix)

- **Agentes de IA/ML são simulados** (`omni/application/agents_service.py`) —
  texto/valores de template fixo. Uma implementação real pede: (a) para o
  Roteirista, uma chamada de LLM de verdade; (b) para o Preditivo/TA, um
  pipeline real de indicadores técnicos e/ou modelo estatístico sobre o
  histórico de preços. Nenhum dos dois é wiring — são escolhas de modelo/dado
  que merecem sua própria conversa.
- **YouTube Auto-Pilot (IA Diretora de Arte) é 100% mock de UI.** Precisa de uma
  app OAuth na YouTube Data API, escolha de motor de TTS e de pipeline de
  renderização de vídeo antes de fazer qualquer coisa real.
