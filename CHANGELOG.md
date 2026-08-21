# 📜 Changelog - DOJOCHO

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [2.4.2] - 2026-08-21

### Adicionado
- **Roteiro de Deploy para Google Cloud**: Adicionado o documento final de deploy (`originais/Roteiro_de_Deploy_Corrigido.md`) contendo os alertas de segurança para backup do SQLite (`rioaiki.db`) e geração de chave `.env`.

### Alterado / Refatorado
- **Layout Responsivo em 2 Colunas no Dashboard**: Re-organizados os cards de **Graduações & Cores de Faixas** e **Aniversariantes do Mês** para exibição horizontal lado a lado no `page1_dashboard.html`.
- **Padronização Visual dos KPIs de Alunos e Senseis**: Atualizados os rótulos e distintivos nas páginas de Gestão e Dashboard para exibir a contagem de ativos e totais de forma transparente (`62 Ativos / 251 Totais`).

### Corrigido
- **Consistência nos KPIs de Alunos**: Eliminada a divergência visual entre os cartões do Painel Geral e as abas da página de Gestão (`/management`).
- **Correção Ortográfica**: Ajustada a grafia de "Practicantes" para "Praticantes" na aba de alunos da Gestão.

---

## [2.4.1] - 2026-08-21

### Adicionado
- **Suporte a Eixos Duplos (Dual Y-Axis) no Gráfico do Dashboard**: Adicionada escala secundária dedicada no lado direito (em tom azul) para exibir a evolução de **Alunos Ativos** proporcionalmente à **Frequência Mensal**.
- **Plano de Rollout para Produção**: Elaborado plano de implantação oficial (`implementation_plan.md`) cobrindo sanitização de banco, configuração de variáveis de ambiente (`JWT_SECRET_KEY`), HTTPS e rotina de backup.

### Alterado / Refatorado
- **Cálculo da Métrica de Alunos Ativos**: Alterada a curva azul no gráfico do dashboard de "Alunos Únicos Presentes" para o "Total de Alunos Ativos Matriculados Acumulados" até aquele mês com base no `start_date`.

### Corrigido
- **Visibilidade da Legenda do Gráfico**: Corrigida a cor do texto da legenda no `page1_dashboard.html` que estava fixada em branco tornando-a invisível no tema claro do sistema.

---

## [2.4.0] - 2026-08-21

### Adicionado
- **Gráfico Dinâmico de Duas Curvas no Dashboard**: Implementada rota `/api/dashboard/chart-data` para exibir simultaneamente o número de **Alunos Únicos (Ativos)** e a **Frequência Mensal (Presenças Totais)**.
- **Filtros Interativos no Gráfico**: Adicionados seletores de Dojo, período (mês inicial e final) e checkboxes para alternar a exibição das métricas em tempo real via AJAX.
- **Importação e Reconciliação em Lote de Alunos**: Script de automação para importar e cruzar 266 registros de alunos da planilha `Alunos Dojoweb.xlsx`, cadastrando alunos novos e vinculando-os automaticamente aos seus Dojos e Senseis correspondentes.

### Alterado / Refatorado
- **Restrição de Permissões de Dojo para Senseis**: Bloqueada a edição e exclusão de Dojos para Senseis que não sejam o responsável legal daquele Dojo específico.
- **Remoção de Ícone de Ajuda do Gráfico**: Retirado o ícone de dúvida/tooltip estático do cabeçalho do gráfico.

### Corrigido
- **Correção da Flag de Alunos Ativos**: Ajustada a lógica de parsing da coluna de status para evitar falso-positivo com a string "Inativo" contendo o termo "ativo".

---

## [2.3.3] - 2026-08-20

### Adicionado
- 

### Alterado / Refatorado
- 

### Corrigido
- 

---

## [2.3.2] - 2026-08-20

### Adicionado
- 

### Alterado / Refatorado
- 

### Corrigido
- 

---

## [2.3.1] - 2026-08-20

### Adicionado
- 

### Alterado / Refatorado
- 

### Corrigido
- 

---

## [2.3.0] - 2026-08-13

### Adicionado
- **Botão de Sair na Interface Mobile**: Botão de logout (`/logout`) integrado no topo do cabeçalho móvel e como aba fixa na barra inferior de navegação.
- **Suporte a Tema Claro no Menu Inferior e Rodapé Mobile**: Estilização Glassmorphic clara, bordas e contraste de ícones adaptados para Tema Claro em smartphones.
- **Headers de Segurança HTTP**: Middleware global adicionando `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` e `Referrer-Policy`.

### Alterado / Refatorado
- **Integridade Referencial SQLite**: Adicionada execução automática de `PRAGMA foreign_keys=ON` em todas as conexões SQLAlchemy.
- **Indexação de Banco de Dados**: Adicionado `index=True` em todas as colunas de chave estrangeira (`ForeignKey`) do ORM para otimização de consultas.
- **Migração do Ciclo de Vida FastAPI**: Atualizada a inicialização do app para o padrão moderno `lifespan` com `@asynccontextmanager`.
- **Padronização de Logging & Timezone**: Substituído o uso de `print()` por `logging` estruturado e migrado `datetime.utcnow()` para `datetime.now(timezone.utc)`.
- **Remoção de Logout no Refresh**: Removida a rotina `initReloadLogout()` no frontend para evitar encerramento de sessão em atualizações de página (F5 / Ctrl+R).

---

## [2.2.1] - 2026-08-13

### Adicionado
- **Botão de Alternância de Tema Mobile**: Inserida a funcionalidade de alternância de Tema Claro/Escuro diretamente na Barra Inferior Mobile e no cabeçalho.

### Corrigido
- **Fidelidade Visual das Cores de Faixas**: Ajustado o estilo do botão da Faixa Amarela (`5º Kyu`) na tabela de graduações com `!important` e sobreposição de especificidade CSS no mobile.
- **Cache-Busting de Recursos Estáticos**: Inseridos parâmetros `?v=2.2.0` / `?v=2.2.1` no `style.css` e `app.js` para garantir atualização imediata nos navegadores móveis.

---

## [2.2.0] - 2026-08-13

### Adicionado
- **Navegação Responsiva Mobile (Bottom Bar)**: Barra inferior de acesso rápido com 5 abas principais para dispositivos móveis (`< 768px`).
- **Suporte Multi-Dispositivo Touch-First**: Reestruturação das tabelas para cards empilhados e ergonomia touch para botões/modais em smartphones e tablets.
- **Arquivos de Implantação GCP Cloud**: Criação do serviço `dojocho.service` (systemd) e guia de deployment `gcp_deploy_guide.md` para Máquina Virtual no Google Cloud Platform.

### Alterado
- **Atualização de Versão Centralizada**: Versão alterada de `2.1.0` para `2.2.0` no `version.py`, API `GET /api/version` e footer da UI.

---

## [2.1.0] - 2026-08-13

### Adicionado
- **Módulo Financeiro**: Gestão completa de mensalidades, taxas de exames de graduação e controle de adimplência/inadimplência.
- **Importador de Graduação (Faixa Preta)**: Script de importação em lote com suporte para Dan, registros diplomáticos e histórico de exames.
- **API de Versão**: Endpoint público `GET /api/version` fornecendo metadados e versão atualizada da aplicação.
- **Exibição de Versão na UI**: Badge identificador de versão (`v2.1.0`) visível no rodapé principal da interface web.

### Alterado
- **Documentação e Padrão de Arquitetura**: Atualização do `DOCUMENTATION.md` para refletir os novos modelos financeiro e de versão.

---

## [2.0.0] - 2026-07-01

### Adicionado
- Reformulação visual completa em **Glassmorphism Neon Dark Mode**.
- Sistema de Presença e Chamada Digital por Aula.
- Mural de Classificados do Dojo com fluxo de aprovação por Senseis/Admin.
- Gestão de Eventos, Exames de Faixa e checklist organizacional.
- Autenticação baseada em JWT com controle RBAC (ADMIN, SENSEI, STUDENT).

---

## [1.0.0] - 2026-01-10

### Adicionado
- Lançamento inicial da plataforma DOJOCHO para cadastro de dojos e praticantes de Aikido.
