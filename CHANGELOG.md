# 📜 Changelog - DOJOCHO

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

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
