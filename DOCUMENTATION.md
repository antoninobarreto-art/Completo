# 🥋 DOJOCHO - Documentação Técnica Completa do Sistema

**Sistema de Gerenciamento de Dojos, Praticantes, Aulas e Eventos de Aikido**  
**Versão**: 2.0 | **Data**: Julho / 2026 | **Licença**: Proprietária - Grupo RioAiki

---

## 📋 Sumário
1. [Visão Geral & Arquitetura](#1-visão-geral--arquitetura)
2. [Estrutura do Projeto](#2-estrutura-do-projeto)
3. [Modelo de Dados & Banco de Dados](#3-modelo-de-dados--banco-de-dados)
4. [Segurança, Autenticação & Permissões (RBAC & LGPD)](#4-segurança-autenticação--permissões-rbac--lgpd)
5. [Módulos do Sistema & Endpoints API](#5-módulos-do-sistema--endpoints-api)
6. [Componentes Visuais & Frontend (UI/UX)](#6-componentes-visuais--frontend-uiux)
7. [Guia de Instalação, Execução & Auditoria](#7-guia-de-instalação-execução--auditoria)

---

## 1. Visão Geral & Arquitetura

O **DOJOCHO** é uma plataforma web desenvolvida para a gestão integrada de dojos da organização de Aikido **RioAiki**. O sistema centraliza a administração de praticantes (alunos e senseis), controle de presença em treinos, solicitações de aulas por alunos visitantes de outros dojos, mural de classificados com controle de aprovação, e agenda oficial de eventos e exames de graduação com checklist de organização de tarefas.

### 🛠️ Stack Tecnológica
- **Backend**: Python 3.14 + FastAPI (Framework web assíncrono de altíssima performance).
- **ORM & Banco de Dados**: SQLAlchemy ORM + SQLite (`rioaiki.db`).
- **Template Engine**: Jinja2 (com filtros customizados como `date_br`).
- **Autenticação**: JSON Web Tokens (JWT) armazenados em cookies seguros `HttpOnly`.
- **Frontend**: Vanilla HTML5, Vanilla CSS3 (Design System Glassmorphic Neon Dark Mode) e Vanilla JavaScript ES6+.
- **Ícones & Tipografia**: FontAwesome 6 Pro & Google Fonts (Inter / Outfits).

---

## 2. Estrutura do Projeto

```
TesteAplicacao/
├── app/
│   ├── main.py                  # Ponto de entrada da aplicação FastAPI e middlewares
│   ├── database.py              # Conexão SQLite e sessão SQLAlchemy
│   ├── models.py                # Modelos ORM (User, Dojo, ClassSchedule, Event, etc.)
│   ├── seed.py                  # Carga inicial e povoamento de dados de teste
│   ├── utils.py                 # Funções auxiliares (format_date_br, etc.)
│   ├── routes/                  # Controladores de Rotas HTTP
│   │   ├── auth_routes.py       # Rotas de Login e Logout
│   │   ├── dashboard.py         # Tela de Visão Geral / Painel
│   │   ├── management.py        # Gestão de Dojos, Senseis e Alunos
│   │   ├── schedule.py          # Horários, Chamadas e Visitantes
│   │   ├── classifieds.py       # Classificados e Aprovações
│   │   └── events.py            # Eventos, Inscrições e Tarefas
│   ├── security/
│   │   └── auth.py              # Criptografia de senhas (Bcrypt) e geração JWT
│   ├── static/                  # Arquivos Estáticos (CSS, JS, Uploads)
│   │   ├── css/style.css        # Sistema de Estilos Glassmorphism
│   │   ├── js/app.js            # Interatividade Frontend e AJAX
│   │   └── uploads/             # Diretório seguro de mídias de upload
│   └── templates/               # Templates HTML Jinja2
│       ├── base.html            # Layout Base e Menu Lateral
│       ├── page1_dashboard.html # Painel Geral
│       ├── page2_management.html# Gestão de Dojos/Membros
│       ├── page3_schedule.html  # Horários & Frequência
│       ├── page4_classifieds.html# Mural de Classificados
│       ├── page5_events.html    # Eventos & Tarefas
│       └── login.html           # Tela de Autenticação
├── scratch/                     # Scripts de Automação, Migração e Auditoria
│   ├── check_db_schema.py       # Validação e migração de colunas SQLite
│   ├── audit_security_rbac.py   # Auditoria de controle de acesso (RBAC)
│   ├── audit_file_upload_security.py # Auditoria de uploads seguros
│   └── benchmark_performance.py # Benchmark de tempo de resposta e carga
├── rioaiki.db                   # Arquivo do banco de dados SQLite
└── requirements.txt             # Dependências Python do projeto
```

---

## 3. Modelo de Dados & Banco de Dados

O banco de dados SQLite utiliza o ORM SQLAlchemy. Abaixo estão as principais entidades e seus atributos:

### Detalhamento dos Campos Especiais:
- **`User.blood_type`**: Tipo sanguíneo (`A+`, `O-`, etc.).
- **`User.blood_transfusion_approved`**: Termo de autorização de procedimentos e transfusão emergencial de sangue.
- **`User.lgpd_consent`**: Aceite do termo de ciência e tratamento de dados (Lei 13.709/2018).
- **`EventTask`**: Checklist dinâmico de organização de eventos com data de conclusão prevista.

---

## 4. Segurança, Autenticação & Permissões (RBAC & LGPD)

### 🔐 Autenticação & Sessão
- As senhas são armazenadas utilizando hash **Bcrypt**.
- A autenticação gera um token **JWT** com validade temporária armazenado no cookie seguro `access_token` com política `HttpOnly`.

### 🛡️ Matriz de Controle de Acesso (RBAC)
| Recurso / Funcionalidade | ADMIN | SENSEI | ALUNO |
|---|:---:|:---:|:---:|
| Criar / Editar / Excluir Dojos | ✅ | ❌ | ❌ |
| Editar Qualquer Usuário | ✅ | ❌ (Apenas os seus) | ❌ (Apenas a si próprio) |
| Criar / Editar / Excluir Eventos | ✅ | ✅ (Eventos próprios) | ❌ |
| Marcar Frequência de Aulas | ✅ | ✅ | ❌ |
| Aprovar Visitantes e Classificados | ✅ | ✅ | ❌ |
| Publicar / Editar Anúncio nos Classificados | ✅ | ✅ | ✅ (Requer aprovação) |
| Inscrever-se em Eventos e Treinos | ✅ | ✅ | ✅ |

### 🔒 Proteção contra Vulnerabilidades (OWASP)
- **Upload Seguro de Mídias**: Validação de tamanho máximo (**5 MB** para imagens), restrição de extensão (`.png`, `.jpg`, `.jpeg`, `.webp`) e renomeação aleatória por `UUID4`.
- **SQL Injection**: Prevenido 100% via parametrização nativa do SQLAlchemy.
- **XSS (Cross-Site Scripting)**: Prevenido pelo Jinja2 auto-escaping ativado.

---

## 5. Módulos do Sistema & Endpoints API

### 🔑 Autenticação (`/api`)
- `GET /login`: Renderiza a tela de login.
- `POST /api/login`: Autentica credenciais e gera o cookie JWT.
- `GET /logout`: Invalida o cookie e redireciona para a página de login.

### 🏢 Gestão de Dojos e Membros (`/api/dojos` & `/api/users`)
- `GET /management`: Painel visual de Dojos, Senseis e Alunos.
- `POST /api/dojos/create`: Cadastra um novo Dojo (Admin).
- `POST /api/dojos/{id}/update`: Atualiza informações e foto do Dojo.
- `POST /api/users/create`: Cadastra novo aluno ou sensei com dados médicos e LGPD.
- `POST /api/users/{id}/update`: Edita informações cadastrais, faixa e contatos.
- `POST /api/users/{id}/toggle-status`: Alterna entre ativo/inativo.

### 📅 Agenda, Frequência e Visitantes (`/api/schedule` & `/api/sessions`)
- `GET /schedule`: Quadro de horários e registro de frequência.
- `POST /api/sessions/create`: Registra sessão de treino realizada.
- `POST /api/attendances/register`: Marca a presença do aluno na aula.
- `POST /api/guest-approvals/request`: Solicita autorização para aluno visitante.
- `POST /api/guest-approvals/{id}/status`: Aprova ou rejeita solicitação de visitante.

### 📢 Classificados (`/api/classifieds`)
- `GET /classifieds`: Mural público de anúncios.
- `POST /api/classifieds/create`: Submete anúncio para aprovação do Sensei.
- `POST /api/classifieds/{id}/status`: Aprova ou rejeita com justificativa.

### 🎯 Eventos & Tarefas (`/api/events`)
- `GET /events`: Agenda de seminários e exames.
- `POST /api/events/create`: Cria novo evento com checklist de tarefas.
- `POST /api/events/{id}/update`: Edita evento e auxiliares.
- `POST /api/events/{id}/tasks/{task_id}/toggle`: Marca/desmarca conclusão de tarefa.

---

## 6. Componentes Visuais & Frontend (UI/UX)

### 🎨 Design System Glassmorphic Neon
- **Tema**: Fundo escuro profundo com superfícies translúcidas e efeito *backdrop-filter blur*.
- **Paleta de Cores HSL**:
  - **Ciano (`#22d3ee`)**: Destaques primários, badges de faixa e botões de ação.
  - **Esmeralda (`#34d399`)**: Status ativos, confirmações e aprovações.
  - **Âmbar (`#f59e0b`)**: Destaques de Senseis, exames e horários.
  - **Rose (`#f43f5e`)**: Botões de exclusão, inativação e alertas médicos.

### 📷 Componente de Mídia 4-em-1
Em todos os formulários com foto (Perfil, Dojo, Eventos e Classificados), o usuário pode escolher entre 4 métodos:
1. **Upload de Arquivo Local** (Drag & Drop ou navegador de arquivos).
2. **URL da Web** (Link direto para imagem pública).
3. **Copiar & Colar (Cut & Paste / Ctrl+V)** (Cola imagens da área de transferência).
4. **Câmera / Webcam** (Captura em tempo real com pré-visualização).

---

## 7. Guia de Instalação, Execução & Auditoria

### 1. Instalação de Dependências
```bash
pip install fastapi uvicorn sqlalchemy jinja2 python-multipart pyjwt passlib bcrypt
```

### 2. Execução do Servidor em Desenvolvimento
```bash
uvicorn app.main:app --reload --port 8000
```
Acesse a aplicação no navegador em: `http://localhost:8000`

### 3. Execução dos Scripts de Auditoria Técnica
- **Auditoria de Permissões RBAC**:
  ```bash
  python scratch/audit_security_rbac.py
  ```
- **Auditoria de Uploads Seguros**:
  ```bash
  python scratch/audit_file_upload_security.py
  ```
- **Benchmark de Performance e Resposta**:
  ```bash
  python scratch/benchmark_performance.py
  ```

### 4. Rotina de Backup do Banco de Dados
O banco `rioaiki.db` **não é versionado no Git** (contém dados pessoais — LGPD). O backup é feito pela rotina automatizada:

- **Script**: `scripts/backup_db.py` — usa a API de backup online do SQLite (seguro com o app em execução), valida a integridade da cópia e mantém as **últimas 30 cópias** em `backups/` (pasta sincronizada ao OneDrive, fora do Git).
- **Agendamento**: tarefa **`RioAiki-Backup-Banco`** no Agendador de Tarefas do Windows, diariamente às **18:30** (executa ao ligar o PC se o horário for perdido).
- **Execução manual**: `python scripts/backup_db.py`
- **Log de operações**: `backups/backup.log`
- **Restauração**: parar o app e substituir `rioaiki.db` pela cópia desejada da pasta `backups/`.
