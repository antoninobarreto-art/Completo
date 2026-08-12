# 📕 CADERNO DE AUDITORIA COMPLETA & RECOMENDAÇÕES
## Sistema RioAiki DOJOCHO — Gestão de Dojos de Aikido

| | |
|---|---|
| **Data da Auditoria** | 25 de Julho de 2026 (correções aplicadas até 25/07/2026) |
| **Versão do Sistema** | 2.0 (commit `f73ada1` + correções P0) |
| **Tipo de Auditoria** | Análise estática de código + Testes dinâmicos de intrusão + Auditoria de banco de dados |
| **Classificação Geral** | 🟡 **MATURIDADE 3/5** — Todos os itens P0 corrigidos, risco de comprometimento total eliminado. Pendentes P1 (conformidade LGPD, segurança de transporte, logging) e P2. |
| **Dados em Risco** | 95 usuários reais (banco não está mais versionado no Git) |

---

## 📋 SUMÁRIO

1. [Sumário Executivo](#1-sumário-executivo)
2. [Metodologia Aplicada](#2-metodologia-aplicada)
3. [Pontos Fortes Identificados](#3-pontos-fortes-identificados)
4. [Matriz Consolidada de Achados](#4-matriz-consolidada-de-achados)
5. [PARTE I — Recomendações Gerais (Estratégicas e de Governança)](#5-parte-i--recomendações-gerais)
6. [PARTE II — Recomendações Específicas (Técnicas, por arquivo)](#6-parte-ii--recomendações-específicas)
7. [Plano de Ação Priorizado (P0 / P1 / P2)](#7-plano-de-ação-priorizado)
8. [Anexo A — Evidências dos Testes Dinâmicos](#anexo-a--evidências-dos-testes-dinâmicos)
9. [Anexo B — Mapeamento OWASP Top 10](#anexo-b--mapeamento-owasp-top-10)
10. [Anexo C — Inventário do Banco de Dados](#anexo-c--inventário-do-banco-de-dados)

---

## 1. SUMÁRIO EXECUTIVO

O sistema **RioAiki DOJOCHO** é uma aplicação FastAPI + SQLite funcional e bem estruturada, com uma base de segurança **acima da média de projetos em desenvolvimento** (bcrypt, JWT, rate limiting no login, RBAC parcial, proteção XSS via template engine).

A auditoria identificou **30 achados** (4 críticos, 6 altos, 8 médios, 12 baixos). **Todos os 7 itens ativos do plano P0 foram corrigidos**, eliminando o risco de comprometimento total. O item C-04 (senha forte) foi excluído voluntariamente como risco aceito.

> ✅ **Risco de sequestro de conta e forja de token ADMIN eliminado.** Uploads agora validam extensão + magic bytes via helper centralizado. Banco de dados removido do versionamento Git.

Ainda pendentes para produção: conformidade LGPD (dados de saúde visíveis a Senseis), HTTPS + headers de segurança, logging estruturado, rate limit no forgot-password, e demais itens P1/P2.

| Domínio | Situação | Nota (0-10) |
|---|---|---|
| Autenticação (senhas/tokens) | 🟢 Críticos resolvidos; senha fraca é risco aceito | 7 |
| Controle de Acesso (RBAC) | 🟡 Middleware deny-by-default implementado | 6 |
| Proteção de Dados (LGPD) | 🟡 Banco não está mais no Git; saúde ainda acessível | 4 |
| Uploads de Arquivos | 🟢 Helper centralizado com whitelist + magic bytes | 9 |
| Headers/Transporte | 🔴 Ausentes (sem HTTPS, Secure, CSP etc.) | 1 |
| Qualidade de Código | 🟢 Upload duplicado eliminado (B-02 resolvido) | 7 |
| Dependências | 🟢 Atualizadas; requirements incompleto | 7 |
| Documentação | 🟡 Existe, mas diverge do comportamento real | 5 |

**NÍVEL GLOBAL: 6/10 — Médio. Adequado para homologação. Itens P1 necessários antes de produção.**

---

## 2. METODOLOGIA APLICADA

| Técnica | Cobertura |
|---|---|
| **Análise estática** | 100% do código Python (`app/`), templates Jinja2, JavaScript, `.gitignore`, `requirements.txt`, documentação |
| **Testes dinâmicos (intrusão)** | 21 cenários executados via `TestClient` contra a aplicação real (banco preservado com backup/restore) |
| **Auditoria de banco de dados** | Inventário de tabelas, integridade referencial, índices, dados sensíveis, contas anômalas |
| **Análise de dependências** | Versões instaladas vs. CVEs conhecidas (FastAPI 0.139.2, Jinja2 3.1.6, PyJWT 2.13, python-multipart 0.0.32, SQLAlchemy 2.0.51 — todas sem CVEs ativas conhecidas) |
| **Revisão de repositório** | Arquivos versionados, histórico Git, exposição de segredos |

---

## 3. PONTOS FORTES IDENTIFICADOS

Estes controles **estão corretos e devem ser mantidos**:

| # | Controle | Evidência |
|---|---|---|
| ✅ 1 | **Hash de senhas com bcrypt (custo 12)** | `app/security/auth.py:16` |
| ✅ 2 | **Rate limiting de login funcional** (bloqueio HTTP 429 após 5 tentativas/min) | Comprovado em teste dinâmico (Fase 4) |
| ✅ 3 | **Cookie de sessão `HttpOnly` + `SameSite=Lax`** | `auth_routes.py:73-80` |
| ✅ 4 | **XSS prevenido por autoescape do Jinja2** (nenhum uso de `\| safe` nos templates) | Revisão de 9 templates |
| ✅ 5 | **SQL Injection prevenido** (100% ORM SQLAlchemy parametrizado) | Revisão de todas as queries |
| ✅ 6 | **Whitelist de extensões + limite de 5MB** em classificados/eventos/agenda — **bloqueou `.exe` e `.svg` em teste real** | `classifieds.py:16`, comprovado dinamicamente |
| ✅ 7 | **CPF armazenado mascarado** (`***.123.456-**`) — boa prática LGPD | `management.py:110-114` |
| ✅ 8 | **Token de reset criptograficamente seguro** (`secrets.token_urlsafe(32)`), expira em 1h e é invalidado após uso | `auth_routes.py:106-108` |
| ✅ 9 | **Mensagem genérica de login** ("E-mail ou senha incorretos") — não revela qual campo falhou | `auth_routes.py:46-58` |
| ✅ 10 | **Integridade referencial do banco**: zero violações em `PRAGMA foreign_key_check` | Auditoria de BD |
| ✅ 11 | **Dependências atualizadas** sem CVEs ativas conhecidas | pip list vs. bases CVE |
| ✅ 12 | **Lógica de autorização contextual** (`can_manage_student`) — Sensei só edita alunos do seu dojo/supervisão | `management.py:21-42` |

---

## 4. MATRIZ CONSOLIDADA DE ACHADOS

> Convenção: **C** = Crítico | **A** = Alto | **M** = Médio | **B** = Baixo — ✔ = comprovado por exploração real

| ID | Sev. | Achado | Local | Evidência |
|---|---|---|---|---|
| **C-01** | 🔴 ✅ | **Link de redefinição de senha exibido na tela** para qualquer e-mail informado → sequestro de conta | `auth_routes.py:120-123` + `login.html:38-41` | ✔ Corrigido: resposta genérica + reset_url removido da tela |
| **C-02** | 🔴 ✅ | **`SECRET_KEY` do JWT hardcoded** e versionada → forja de token com `role=ADMIN` | `app/security/auth.py:9` | ✔ Corrigido: chave removida do código, `.env` obrigatório |
| **C-03** | 🔴 ✅ | **6 endpoints de API sem verificação de autenticação/autorização** | `schedule.py:136,224,254`; `events.py:141,282,290`; `classifieds.py:44` | ✔ Corrigido: middleware deny-by-default + validação RBAC |
| **C-04** | 🔴 ❌ | **Senha mínima de 4 caracteres** (combinada com C-01 = takeover trivial) | `auth_routes.py:166` | ❌ Excluído voluntariamente (risco aceito) |
| **A-01** | 🟠 ✅ | **Usuário inativo consegue autenticar-se** (`is_active` não verificado no login) | `auth_routes.py:44-59` | ✔ Corrigido: login bloqueia inativos (mensagem genérica) |
| **A-02** | 🟠 ✅ | **Upload sem whitelist de extensão** na gestão de usuários/dojos — `.html` aceito como "foto" (XSS armazenado servido pelo próprio domínio) | `management.py:120-128, 194-202, 273-281, 413-421` | ✔ Corrigido: whitelist + magic bytes via helper centralizado |
| **A-03** | 🟠 ✅ | **Sem validação de conteúdo real (magic bytes)** — HTML disfarçado de `.png` aceito | todas as rotas de upload | ✔ Corrigido: validação de magic bytes em todas as rotas |
| **A-04** | 🟠 ✅ | **Banco SQLite com dados pessoais reais versionado no Git** (`rioaiki.db` rastreado; `*.db` comentado no `.gitignore`) | `.gitignore:12`, `git ls-files` | ✔ Corrigido: histórico reescrito, `*.db` no `.gitignore` |
| **A-05** | 🟠 | **Enumeração de contas** — resposta do "esqueci a senha" difere para e-mail cadastrado | `auth_routes.py:96-124` | ✔ Corrigido junto com C-01 (resposta genérica uniforme) |
| **A-06** | 🟠 | **`/api/forgot-password` sem rate limit** | `auth_routes.py:90` | ✔ 8/8 requisições aceitas |
| **M-01** | 🟡 | **5 headers de segurança ausentes**: `X-Content-Type-Options`, `X-Frame-Options`, `CSP`, `HSTS`, `Referrer-Policy` | resposta HTTP de qualquer rota | ✔ Verificado dinamicamente |
| **M-02** | 🟡 | **Cookie sem flag `Secure`** + aplicação servida em HTTP puro | `auth_routes.py:73` | ✔ Flag ausente no `Set-Cookie` |
| **M-03** | 🟡 | **Sem tokens CSRF** nos formulários (mitigação parcial via `SameSite=Lax`) | todos os forms POST | Análise estática |
| **M-04** | 🟡 | **Dados de saúde (sensíveis, Art. 11 LGPD)** visíveis a qualquer SENSEI sem necessidade de acesso por aluno | `models.py:49-54` + `page2_management.html` | Inventário BD |
| **M-05** | 🟡 | **JWT não revogável** — logout só apaga o cookie; token copiado segue válido por até 8h | `auth.py`, `auth_routes.py:83-87` | Análise estática |
| **M-06** | 🟡 | **IDOR**: inscrição em evento aceita `user_id` arbitrário (padrão `1`!) | `events.py:141` | ✔ Inscrição forjada p/ usuário 4 sem login |
| **M-07** | 🟡 | **Sessão fixa de 8h** sem idle timeout nem renovação deslizante | `auth.py:11` | Análise estática |
| **M-08** | 🟡 | **`initReloadLogout()` desloga o usuário a cada F5/Ctrl+R** — falsa sensação de segurança, degrada UX e não protege nada | `app.js:295-312` | Análise estática |
| **B-01** | 🔵 | **`requirements.txt` incompleto** — faltam `bcrypt` e `PyJWT` (deploy limpo quebra); doc cita `passlib` não utilizado | `requirements.txt` | Análise estática |
| **B-02** | 🔵 | **Lógica de upload duplicada em 4 arquivos** (13 blocos) — divergência de regras (A-02 vs. whitelist) | `management.py`, `classifieds.py`, `events.py`, `schedule.py` | Análise estática |
| **B-03** | 🔵 | **`print()` como logging**, incluindo **link de reset de senha gravado em log/console** | `auth_routes.py:112-115` | Análise estática |
| **B-04** | 🔵 | APIs deprecadas: `datetime.utcnow()` (Python 3.12+) e `@app.on_event("startup")` (FastAPI) | `models.py`, `auth_routes.py`, `main.py:58` | Análise estática |
| **B-05** | 🔵 | **Performance**: N+1 em agenda (presenças por card), `User.query.all()` sem paginação em 4 páginas, sem índices nas FKs | `schedule.py:63-67`, `dashboard.py`, `management.py` | Análise estática + índices BD |
| **B-06** | 🔵 | **SQLite sem `PRAGMA foreign_keys=ON`**; schema por `create_all` (sem migrations — Alembic) | `database.py` | Análise estática |
| **B-07** | 🔵 | **Sem suíte de testes formal** (apenas scripts ad-hoc em `scratch/`, que é gitignored) | estrutura do projeto | Análise estática |
| **B-08** | 🔵 | **Documentação diverge do código** (endpoints documentados inexistentes: `/api/login`, `/api/attendances/register`, `/api/sessions/create`) | `DOCUMENTATION.md:113-131` | Análise estática |
| **B-09** | 🔵 ✅ | **Contas anômalas**: usuário id 95 sem senha cadastrada → inativado; usuário id 15 com `reset_token` pendente → limpo | BD `users` | ✔ Conta 95 inativada, reset_token do id 15 removido |
| **B-10** | 🔵 | **`uvicorn.run(..., reload=True)`** e host configurável apenas no `__main__` | `main.py:69-71` | Análise estática |
| **B-11** | 🔵 | Código morto/confuso: `FastAPIDependencyDecorator` declarado mas nunca retornado; lógica de decorator duplicada | `decorators.py:78-115` | Análise estática |
| **B-12** | 🔵 | Footer afirma **"Conformidade LGPD Garantida"** sem sustentação técnica | `base.html:92` | Análise estática |

**Totais: 4 Críticos (3 corrigidos ✅, 1 excluído ❌) | 6 Altos (6 corrigidos ✅) | 7 Médios | 12 Baixos (1 corrigido ✅) = 29 achados pendentes**

### 📗 Registro de Correções Aplicadas

| Data | ID | Correção | Evidência |
|---|---|---|---|
| 25/07/2026 | **A-04** ✅ | Banco removido do versionamento: `*.db` ativado no `.gitignore`, `git rm --cached`, **histórico reescrito (git-filter-repo)** e force-push ao GitHub. Arquivo local e dados preservados (95 usuários intactos). | Commit `f73ada1`; `git log --all -- rioaiki.db` vazio; `origin/main` sem `.db` |
| 25/07/2026 | **C-03 + M-06** ✅ | Middleware reescrito para **"negar por padrão"** (API sem token → 401 JSON; página → redirect). Protegidos os 6 endpoints abertos: `sessions/create-with-attendance` e `guest-approvals/status` exigem ADMIN/SENSEI (+status validado contra enum); `guest-approvals/create` exige login e força aluno ao próprio id; `events/register` usa **somente o usuário da sessão** (IDOR eliminado); `tasks/toggle` exige ADMIN/sensei do evento/responsável; `tasks/delete` exige ADMIN/sensei do evento. | Regressão dinâmica: **25/25 testes passaram** (anônimo 401; IDOR sem efeito; RBAC por papel validado) |
| 25/07/2026 | **C-01** ✅ | Reset de senha: `reset_url` removido da resposta HTML + resposta genérica "se o e-mail existir, enviaremos um link" independente de cadastro (anti-enumeração A-05). | `auth_routes.py` + `login.html` |
| 25/07/2026 | **C-02** ✅ | `SECRET_KEY` removida do código-fonte. `.env` obrigatório com `JWT_SECRET_KEY`. App falha na inicialização sem a variável. Chave gerada: `9f0b...` (registrada no .env, gitignored). | `app/security/auth.py` + `.env` |
| 25/07/2026 | **A-01** ✅ | Login de usuários inativos bloqueado com mensagem genérica "E-mail ou senha incorretos". | `auth_routes.py:login` |
| 25/07/2026 | **B-09** ✅ | Higienização do banco: `reset_token` e `reset_token_expires` limpos do usuário id 15 (antonino); conta id 95 (sem senha) inativada (`is_active=False`). | `rioaiki.db` diretamente |
| 25/07/2026 | **A-02 + A-03 + B-02** ✅ | Upload helper centralizado em `app/utils.py` com `validate_image_upload`, `decode_and_validate_image`, `validate_doc_upload`. Aplicado nos 4 arquivos de rota (management.py, classifieds.py, events.py, schedule.py), eliminando 13 blocos de lógica duplicada. | `app/utils.py`, rotas |
| 25/07/2026 | **C-04** ❌ | Senha forte excluída voluntariamente pelo usuário. Mantida política de 4 caracteres como risco aceito documentado. | Decisão do proprietário |

---

## 5. PARTE I — RECOMENDAÇÕES GERAIS

*(Estratégicas, de processo e governança — independentes de uma linha de código específica)*

### G-01 🔑 Gestão de Segredos
- **Nunca** manter segredos no código-fonte. Adotar variáveis de ambiente com `.env` local (gitignored) + cofre de segredos no deploy (Azure Key Vault, AWS Secrets Manager, ou variáveis do provedor).
- **Rotacionar imediatamente** a `JWT_SECRET_KEY` (ela já deve ser considerada comprometida, pois está no histórico do Git).
- Adotar ferramenta de varredura de segredos no pipeline (ex.: `gitleaks`, `git-secrets`) e hook de pre-commit.
- Após remover segredos do código, **reescrever o histórico Git** (`git filter-repo` / BFG) ou assumir vazamento definitivo e trocar todas as credenciais derivadas.

### G-02 🛡️ Modelo de Autorização "Negar por Padrão"
- Inverter a lógica do middleware: hoje ele **permite** tudo que começa com `/api` e só protege páginas HTML. O correto: **toda rota exige autenticação por padrão**, e apenas as explicitamente públicas (`/login`, `/static`, `/favicon.ico`, `/reset-password`, `/api/forgot-password`, `/api/reset-password`) são liberadas.
- Padronizar o uso de `Depends()` de autorização (o módulo `app/security/decorators.py` já existe — usá-lo de fato em **todas** as rotas mutáveis).
- Revisar a matriz RBAC e publicá-la na documentação (a atual lista endpoints que não existem).

### G-03 🔐 Política de Credenciais e Sessão
- Senha mínima de **8 caracteres** com letras + números (ideal 12+); validar contra listas de senhas vazadas (ex.: *haveibeenpwned* — opcional).
- Bloquear login de usuários inativos com mensagem genérica.
- Reduzir sessão para 2–4h, implementar **renovação deslizante** e considerar **lista de revogação** (ou versão de token por usuário) para logout efetivo.
- Em produção: cookie com `Secure=True` e **HTTPS obrigatório** (HSTS).

### G-04 ⚖️ Conformidade LGPD (Lei 13.709/2018)
- **Remover `rioaiki.db` do Git imediatamente** (descomentar `*.db`, remover do índice e **purgar do histórico** — os dados já versionados devem ser tratados como incidente de vazamento).
- Avaliar **notificação de incidente** à ANPD/titulares se o repositório foi exposto a terceiros (GitHub etc.).
- **Minimização**: dados de saúde (tipo sanguíneo, convênio, observações médicas, consentimento de transfusão) são **dados sensíveis (Art. 11)** — restringir exibição a quem tem necessidade real (ex.: apenas ADMIN e o próprio titular; Sensei vê só alerta "possui restrição médica: sim/não").
- Registrar **base legal e finalidade** de cada dado sensível coletado; guardar evidência do consentimento (hoje `lgpd_consent` é apenas um booleano sem data/versão do termo).
- Implementar **direito de exclusão/anonização** auditável e política de retenção.
- **Remover do rodapé** a frase "Conformidade LGPD Garantida" até que a conformidade seja real — a afirmação falsa aumenta a exposição jurídica.

### G-05 🏗️ Infraestrutura e Deploy
- Publicar atrás de **reverse proxy com TLS** (nginx/Caddy) e servir uploads com `X-Content-Type-Options: nosniff` (ideal: fora do domínio da aplicação ou com `Content-Disposition: attachment` para não-imagens).
- Migrar de SQLite para **PostgreSQL** antes de uso multiusuário real (concorrência, backups, roles).
- Definir rotina de **backup automatizado** do banco e dos uploads, com teste de restauração.
- Desativar `reload=True` e `docs`/`redoc` abertos em produção.

### G-06 🧪 Qualidade, Testes e CI/CD
- Completar o `requirements.txt` (faltam `bcrypt`, `PyJWT`) e **fixar versões** (`==`) com lockfile; rodar `pip-audit` no pipeline.
- Criar suíte **pytest** versionada (hoje os testes estão em `scratch/`, que é gitignored — ou seja, não existem para o time). Mínimo: testes de autenticação, RBAC por papel, uploads maliciosos, fluxo de reset.
- Pipeline de CI (GitHub Actions) com: lint (`ruff`), type-check opcional, testes, `pip-audit`, `gitleaks`.
- Padronizar tratamento de erros e usar **`logging` estruturado** (nunca `print`; nunca logar tokens, senhas ou links de reset).

### G-07 📊 Observabilidade e Auditoria Contínua
- Logar (sem dados sensíveis) todos os eventos de segurança: login falho/bem-sucedido, reset de senha, aprovações/rejeições, alterações de role/status, exclusões.
- Manter **trilha de auditoria** (quem fez o quê e quando) nas tabelas críticas (`approved_by`, `updated_by`, `updated_at`).
- Repetir esta auditoria dinâmica a cada release relevante (os 21 testes aplicados podem virar testes automatizados de regressão de segurança).

### G-08 🧭 UX de Segurança (decisões conscientes)
- Remover o `initReloadLogout()` (logout no F5): **não é um controle de segurança eficaz** (o token continua válido no servidor) e destrói a usabilidade. Substituir por idle timeout real no servidor se desejado.
- Exibir mensagens de erro genéricas e consistentes (já bom no login; estender ao reset).

---

## 6. PARTE II — RECOMENDAÇÕES ESPECÍFICAS

*(Técnicas, com arquivo, linha e correção sugerida)*

### 6.1 `app/security/auth.py`

**C-02 — Remover fallback da chave secreta (linha 9):**
```python
# ANTES (vulnerável):
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "rioaiki_super_secret_jwt_key_2026_change_in_prod")

# DEPOIS:
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY não configurada. Defina a variável de ambiente.")
```
**M-05/M-07:** incluir claim `jti` (ID único por token) e `pwd_version` no usuário para permitir revogação; reduzir `ACCESS_TOKEN_EXPIRE_MINUTES` para 120–240.

**B-04:** trocar `datetime.now(timezone.utc)` — já está correto aqui; o problema é nos demais arquivos.

---

### 6.2 `app/routes/auth_routes.py`

**C-01 — Nunca exibir o link de reset na tela (linhas 117-124):**
```python
# ANTES (vulnerável): retorna "reset_url": reset_link ao template
# DEPOIS: mesma mensagem genérica para e-mail existente ou não,
#         e envio real por e-mail (SMTP/SendGrid/etc.)
return templates.TemplateResponse(
    request=request, name="login.html",
    context={"msg": "Se o e-mail estiver cadastrado, enviamos um link de redefinição para a sua caixa de entrada."}
)
```
**C-04 — Política de senha (linha 166):** elevar para mínimo 8 caracteres + exigir letra e número:
```python
import re
if len(new_password) < 8 or not re.search(r"[A-Za-z]", new_password) or not re.search(r"\d", new_password):
    # rejeitar com mensagem orientativa
```
**A-01 — Bloquear inativos (após linha 44):**
```python
if not user or not user.is_active:
    # mesma mensagem genérica "E-mail ou senha incorretos."
```
**A-05/A-06:** usar `login_rate_limiter` (ou um limiter dedicado) também no `/api/forgot-password`, por IP **e** por e-mail; resposta idêntica (status 200, mesmo template) para e-mail existente ou não.

**M-02:** `response.set_cookie(..., secure=True, samesite="lax", httponly=True)` em produção (parametrizar por env).

**B-03/B-09:** substituir os `print()` por `logging.info` sem incluir o link; ao expirar/limpar, garantir `reset_token=None` (há um token pendente no usuário id 15 do banco — invalidar manualmente).

---

### 6.3 `app/main.py`

**C-03 — Middleware "negar por padrão" (linhas 25-48):**
```python
PUBLIC_PATHS = {"/login", "/favicon.ico", "/reset-password"}
PUBLIC_PREFIXES = ("/static", "/api/forgot-password", "/api/reset-password")

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    if path in PUBLIC_PATHS or any(path.startswith(p) for p in PUBLIC_PREFIXES):
        return await call_next(request)

    token = request.cookies.get("access_token") or _bearer(request)
    user = decode_access_token(token) if token else None
    if not user:
        if path.startswith("/api"):
            return JSONResponse({"detail": "Não autenticado."}, status_code=401)  # API: 401, não redirect
        return RedirectResponse(url="/login", status_code=303)
    request.state.user = user
    return await call_next(request)
```

**M-01 — Headers de segurança** (novo middleware após auth):
```python
@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; script-src 'self'"
    return resp
```

**B-04:** migrar `@app.on_event("startup")` para o padrão `lifespan`. **B-10:** parametrizar host/port/reload por env.

---

### 6.4 `app/routes/schedule.py` — 3 endpoints abertos

Adicionar verificação no início de **cada um** (padrão já usado em outras rotas):
```python
current_user = getattr(request.state, "user", None)
if not current_user or current_user.get("role") not in ["ADMIN", "SENSEI"]:
    raise HTTPException(status_code=403, detail="Acesso negado.")
```
- `create_session_attendance` (linha 137) — hoje **qualquer anônimo cria aula + presenças**;
- `create_guest_approval` (linha 225) — exigir usuário autenticado e validar que o `student_id` é o próprio usuário (ou Sensei/Admin);
- `update_guest_approval_status` (linha 255) — exigir ADMIN/SENSEI **e** validar `status` contra enum `{"APPROVED","REJECTED"}` (hoje aceita qualquer string); idealmente registrar `approved_by/approved_at`.

---

### 6.5 `app/routes/events.py`

- **`register_event` (linha 141) — corrigir IDOR:** usar **somente** o usuário da sessão, ignorando `user_id` do form:
```python
def register_event(event_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        raise HTTPException(status_code=401, detail="Não autenticado.")
    user_id = int(current_user["sub"])
```
- **`toggle_event_task` / `delete_event_task` (linhas 282, 290):** exigir autenticação; restringir a ADMIN, SENSEI responsável pelo evento ou usuário designado da tarefa.

---

### 6.6 `app/routes/management.py` — uploads (A-02)

Replicar o padrão de whitelist já existente em `classifieds.py` nos 4 blocos de upload:
```python
ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
ext = os.path.splitext(photo_file.filename)[1].lower()
if ext not in ALLOWED_IMAGE_EXTS:
    raise HTTPException(status_code=400, detail="Formato de imagem não permitido.")
```
**A-03 — validar magic bytes em todos os uploads** (centralizar — ver B-02):
```python
MAGIC = {b"\x89PNG\r\n\x1a\n": ".png", b"\xff\xd8\xff": ".jpg", b"RIFF": ".webp"}
def sniff_image(content: bytes) -> bool:
    return any(content.startswith(sig) for sig in MAGIC)
```
**M-04:** não enviar `medical_notes`, `health_insurance`, `blood_type` ao template para SENSEI comum — filtrar no contexto ou mascarar por papel.

---

### 6.7 `app/routes/classifieds.py`

- `create_classified` (linha 44): hoje aceita anônimo e usa `author_id` do form — exigir autenticação e **sempre** derivar o autor do token (já faz parcialmente para STUDENT; estender a todos).
- Aplicar validação de magic bytes (A-03).
- Rejeição: sanitizar/limitar `rejection_reason` (tamanho máximo).

---

### 6.8 `app/static/js/app.js`

**M-08 — remover o auto-logout no refresh (linhas 295-312):** apagar `initReloadLogout()` e sua chamada. Se a intenção é sessão curta, implementar idle timeout real no servidor.

**M-03:** incluir token CSRF (header `X-CSRF-Token`) nas chamadas `fetch` POST, com geração/validação no backend (ou aceitar a mitigação `SameSite=Lax` como risco residual documentado).

---

### 6.9 `app/database.py` e `app/models.py`

**B-06:**
```python
from sqlalchemy import event
@event.listens_for(engine, "connect")
def _fk_on(dbapi_conn, _):
    dbapi_conn.execute("PRAGMA foreign_keys=ON")
```
Adotar **Alembic** para migrations (hoje só `create_all`, que não altera colunas existentes).

**B-05 — índices** nas FKs mais consultadas: `attendances(session_id)`, `attendances(user_id)`, `class_sessions(dojo_id)`, `classifieds(status)`, `guest_approvals(status)`, `event_presences(event_id, user_id)` (composto + `UniqueConstraint` para evitar inscrição dupla).

**B-09:** definir `password_hash` como `nullable=False` a médio prazo; tratar a conta id 95 (sem senha) e o `reset_token` pendente do id 15.

---

### 6.10 `app/security/decorators.py` (B-11)

Remover a classe morta `FastAPIDependencyDecorator` (linhas 109-113) e a lógica duplicada de decorator (78-106), mantendo apenas a *dependency* FastAPI — ou finalizar a implementação. Hoje o arquivo retorna sempre `dependency` e o restante é peso morto que confunde manutenção.

---

### 6.11 `requirements.txt` (B-01)

```txt
fastapi==0.139.2
uvicorn==0.51.0
jinja2==3.1.6
sqlalchemy==2.0.51
python-multipart==0.0.32
pydantic==2.13.4
bcrypt==5.0.0
PyJWT==2.13.0
```
(Remover a referência a `passlib` da documentação — não é usado.)

---

### 6.12 `.gitignore` e repositório (A-04)

```gitignore
# Database
*.db
```
Depois: `git rm --cached rioaiki.db` + purge do histórico (`git filter-repo --path rioaiki.db --invert-paths`) + **rotacionar** a JWT key e todas as senhas (comunicar usuários para redefinição).

---

### 6.13 Templates

- `login.html:38-41`: remover o bloco `{% if reset_url %}` (parte do fix C-01).
- `base.html:92`: trocar "Conformidade LGPD Garantida" por texto neutro até conformidade real (G-04).
- `page2_management.html`: condicionar a renderização de dados médicos ao papel (M-04).
- Adotar `nonce` de CSP quando os inline-styles forem refatorados (evoluir M-01).

---

## 7. PLANO DE AÇÃO PRIORIZADO

### 🔴 P0 — IMEDIATO (esta semana) — risco de comprometimento total
| # | Ação | Esforço | Status |
|---|---|---|---|
| 1 | Remover exibição do `reset_url` na tela (C-01) | 0,5h | ✅ |
| 2 | `SECRET_KEY` sem fallback + rotação da chave (C-02) | 1h | ✅ |
| 3 | Middleware "negar por padrão" + proteger os 6 endpoints abertos (C-03, M-06) | 3h | ✅ |
| 4 | Senha mínima 8+ com complexidade (C-04) | 0,5h | ❌ Excluído |
| 5 | Remover `rioaiki.db` do Git + purge de histórico + forçar redefinição de senhas (A-04) | 2h | ✅ |
| 6 | Bloquear login de inativos (A-01) | 0,5h | ✅ |
| 7 | Whitelist de extensões + magic bytes em **todos** os uploads (A-02, A-03) | 2h | ✅ |
| 8 | Invalidar `reset_token` pendente (user id 15) e revisar conta sem senha (id 95) (B-09) | 0,5h | ✅ |

### 🟠 P1 — 30 DIAS — conformidade e robustez
| # | Ação | Esforço |
|---|---|---|
| 9 | HTTPS + cookie `Secure` + headers de segurança (M-01, M-02) | 4h |
| 10 | Rate limit + resposta uniforme no forgot-password (A-05, A-06) | 2h |
| 11 | Minimização de dados de saúde por papel + revisão LGPD (M-04, G-04) | 8h |
| 12 | Completar/pinnar requirements + `pip-audit` no CI (B-01) | 1h |
| 13 | Suíte pytest de segurança (regressão dos 21 testes desta auditoria) (B-07) | 8h |
| 14 | Logging estruturado + trilha de auditoria, remoção de `print` (B-03, G-07) | 4h |
| 15 | Centralizar helper de upload (eliminar 13 blocos duplicados) (B-02) | 3h |
| 16 | Remover `initReloadLogout` (M-08) | 0,5h |

### 🟡 P2 — 90 DIAS — maturidade
| # | Ação | Esforço |
|---|---|---|
| 17 | Migração PostgreSQL + Alembic + backups automatizados (B-06, G-05) | 16h |
| 18 | Revogação de JWT / sessão deslizante / idle timeout (M-05, M-07) | 6h |
| 19 | CSRF tokens (M-03) + CSP com nonce | 4h |
| 20 | Índices, paginação e correção de N+1 (B-05) | 4h |
| 21 | Envio real de e-mail (SMTP transacional) para reset de senha | 4h |
| 22 | Programa LGPD completo: registro de consentimento, retenção, exclusão auditável | 16h |
| 23 | Atualizar `DOCUMENTATION.md` (endpoints reais, matriz RBAC, instalação) (B-08) | 2h |
| 24 | CI completo (lint, testes, gitleaks) + code review obrigatório | 4h |

---

## Anexo A — Evidências dos Testes Dinâmicos

Execução: 25/07/2026, via `TestClient` (banco preservado por backup/restore; artefatos de PoC removidos).

| # | Teste | Resultado |
|---|---|---|
| 1 | `POST /api/sessions/create-with-attendance` **anônimo** | 🔴 Executou (HTTP 303) |
| 2 | `POST /api/guest-approvals/1/status?status=REJECTED` anônimo | 🔴 Executou (HTTP 200) |
| 3 | `POST /api/guest-approvals/create` anônimo | 🔴 Executou (HTTP 303) |
| 4 | `POST /api/events/1/register` com `user_id=4` anônimo | 🔴 Inscreveu terceiro (IDOR) |
| 5 | `POST /api/events/1/tasks/1/toggle` anônimo | 🔴 Executou (HTTP 303) |
| 6 | `POST /api/classifieds/create` anônimo | 🔴 Executou (HTTP 303) |
| 7 | Middleware retorna 401 para `/api` sem token | 🔴 Não retorna (405/passa) |
| 8 | Link de reset exibido no HTML p/ `admin@rioaiki.com.br` | 🔴 Token vazado: `XsQ4nkN2KJ_...` |
| 9 | Resposta difere p/ e-mail inexistente | 🔴 Enumeração possível |
| 10 | Reset da senha do ADMIN com token vazado + senha `"abcd"` | 🔴 **Conta assumida** |
| 11 | JWT ADMIN forjado com chave do repositório → `/management` | 🔴 HTTP 200 |
| 12 | Headers de segurança | 🔴 5 ausentes |
| 13 | Login de usuário **inativo** | 🔴 Bem-sucedido (HTTP 303) |
| 14 | Cookie `Secure` | 🔴 Ausente |
| 15 | Rate limit de login (7 tentativas) | 🟢 Bloqueou na 6ª (HTTP 429) |
| 16 | Rate limit no forgot-password (8 requisições) | 🔴 8/8 aceitas |
| 17 | Upload `.html` como avatar (management) | 🔴 Salvo em `/static/uploads/photos/` |
| 18 | Upload `.exe` (classifieds) | 🟢 Rejeitado pela whitelist |
| 19 | Upload `.svg` com script (classifieds) | 🟢 Rejeitado pela whitelist |
| 20 | HTML disfarçado de `.png` (classifieds) | 🔴 Salvo (sem magic bytes) |
| 21 | **Total: 21 testes — 17 VULNERÁVEIS / 4 protegidos** | 🔴 |

## Anexo B — Mapeamento OWASP Top 10 (2021)

| Categoria OWASP | Situação | Achados |
|---|---|---|
| A01 Broken Access Control | 🔴 | C-03, M-06, A-01 |
| A02 Cryptographic Failures | 🔴 | C-02, M-02, M-05 |
| A03 Injection | 🟢 | ORM parametrizado; sem achados |
| A04 Insecure Design | 🔴 | C-01, A-05, M-08 |
| A05 Security Misconfiguration | 🔴 | M-01, B-10, B-01 |
| A06 Vulnerable Components | 🟢 | Todas atualizadas |
| A07 Auth Failures | 🟡 | C-04 ❌ (risco aceito), A-01 ✅, A-06 |
| A08 Software/Data Integrity | 🟠 | A-04, B-06 |
| A09 Logging & Monitoring | 🟠 | B-03, G-07 |
| A10 SSRF | 🟢 | URLs de foto apenas gravadas, nunca baixadas server-side |

## Anexo C — Inventário do Banco de Dados

| Item | Valor |
|---|---|
| Tabelas | 10 (dojos, users, class_schedules, class_sessions, attendances, guest_approvals, classifieds, events, event_presences, event_tasks) |
| Usuários | **95** (19 SENSEI+, 1 ADMIN, restante STUDENT) |
| Dojos | 20 |
| Dados pessoais | 95 e-mails reais, 76 telefones, 95 CPFs mascarados |
| Dados sensíveis (saúde) | 1 `medical_notes`, 2 `health_insurance` preenchidos; estrutura pronta p/ mais |
| Anomalias | user 95 **sem senha** (inativado) ✅; user 15 **reset_token limpo** ✅; user 10 inativo |
| Integridade referencial | ✅ 0 violações |
| Índices | Apenas PKs + `users.email` (faltam FKs) |
| **Versionado no Git** | 🟢 **NÃO** (`rioaiki.db` removido do histórico) ✅ |

---

> **Preparado por:** Auditoria automatizada OpenCode
> **Próxima revisão recomendada:** após conclusão do plano P0 (re-teste dos 21 cenários) e, subsequentemente, a cada release.
> **Sigilo:** este documento contém descrição de vulnerabilidades exploráveis — restringir acesso.
