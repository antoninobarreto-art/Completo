# 📜 Resumo de Alterações - DOJOCHO v2.4.2 (21/08/26)

Este documento registra todas as evoluções, correções e melhorias de infraestrutura realizadas no sistema **DOJOCHO** no dia **21 de Agosto de 2026**.

---

## 1. 📊 Reformulação do Gráfico de Fluxo (Dashboard)
- **Curva de Alunos Ativos Acumulados**: Alterado o cálculo da linha azul no `/api/dashboard/chart-data` para contabilizar o crescimento histórico acumulado de alunos ativos com base no `start_date`.
- **Eixos Duplos (Dual Y-Axis)**: Implementada uma escala secundária dedicada no lado direito do gráfico (em tom azul) para Alunos (escala 0-70), permitindo comparação visual proporcional com a Frequência (escala 0-300).
- **Ajuste de Frequência Fictícia**: Purga de dados excedentes de presenças de teste, ajustando a média para um patamar realista entre 250 e 290 presenças mensais.
- **Visualização de Legendas**: Corrigida a cor do texto da legenda no `page1_dashboard.html` que estava branca sobre fundo claro.

---

## 2. 👥 Reconciliação dos Dados de Alunos e Dojos
- **Importação em Lote**: Importação oficial e vínculo de 266 alunos da planilha `Alunos Dojoweb.xlsx`.
- **Vínculos de Senseis e Dojos**: Associação dos alunos aos seus Dojos e aos Senseis responsáveis (ex: Fábio Castro associado ao Danketsu Dojo).
- **Consolidação de Status**: Separação precisa em **62 Alunos Ativos** e **189 Inativos** (**251 Alunos Totais**).

---

## 3. 🎨 Melhorias de Layout e UX no Dashboard
- **Layout Responsivo em 2 Colunas**: Re-organizados os cards **"Graduações & Cores de Faixas"** e **"Aniversariantes do Mês"** para exibição horizontal lado a lado no `page1_dashboard.html`, com rolagem interna e suporte a telas móveis.
- **Padronização dos KPIs**:
  - Eliminação da divergência de números entre a página de Gestão (`/management`) e o Dashboard (`/`).
  - Atualização dos distintivos para indicar claramente: **`62 Ativos / 251 Totais`**.
  - Correção ortográfica do texto de *"Practicantes"* para *"Praticantes"*.

---

## 4. 🚀 Preparação para Produção (`dojocho.com.br`)
- **Plano de Rollout (`Plano_de_Rollout_v2_4_1.md`)**: Estratégia oficial de migração e sanitização do banco.
- **Roteiro de Deploy Corrigido (`Roteiro_de_Deploy_Corrigido.md`)**: Inclusão de 3 avisos críticos de segurança para o deploy na VM do Google Cloud:
  1. Backup obrigatório do SQLite (`rioaiki.db`) antes de deletar a pasta antiga.
  2. Criação do arquivo `.env` com a variável `JWT_SECRET_KEY` obrigatória para autenticação.
  3. Manutenção da porta `8501` e permissão `chmod -R 777 app/static`.

---

## 5. 🏷️ Versionamento Semântico e Automação Git/GitHub
- Lançamento e testes bem-sucedidos das versões **`v2.4.0`**, **`v2.4.1`** e **`v2.4.2`**.
- Atualização da ferramenta CLI `scripts/bump_version.py` com a flag `--commit` para automação completa do fluxo: bump de versão, atualização de changelog, execução de testes, `git add`, `git commit`, `git tag` e `git push` para o GitHub (`origin/main`).
