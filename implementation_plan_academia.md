# 📋 Plano de Implementação: Atualização dos Dojos com Coluna `academy`

## 📌 Contexto & Objetivo
Atualizar a estrutura e o banco de dados de Dojos do sistema **RioAiki DOJOCHO** (`rioaiki.db`) incorporando explicitamente o campo de **Academia** (`academy`) no modelo `Dojo`, além de atualizar os **Endereços Completos com CEP**, **Cidades** e os **Senseis Responsáveis** com base nos dados oficiais de **`DojoSenseiResponsavel.xlsx`**.

---

## 📊 Mapeamento dos Dados Extraídos (`DojoSenseiResponsavel.xlsx`)

| # | Dojo (Sistema / DB) | Campo `academy` | Endereço Completo & CEP | Cidade | Sensei Responsável (DB ID) |
|---|---|---|---|---|---|
| **1** | **Daiki Dojo Méier** (ID 14) | Academia All Defense | Rua Conego Tobias, 40, Méier, CEP: 20735-010 | Rio de Janeiro | Marcos Antonio de Almeida Alvaredo (ID 170) |
| **2** | **Daiki Dojo Teresópolis** (ID 11) | Academia de Artes Marciais Moacir Lopes | Av. Delfim Moreira, 103, 2º andar, Centro, CEP: 25953-230 | Teresópolis | Marcos Antonio de Almeida Alvaredo (ID 170) |
| **3** | **Danketsu Dojo** (ID 7) | Danketsu Dojo | Travessa Vereador Prudente Aguiar, 21, Centro, CEP: 25620-000 | Petrópolis | Fabio Castro da Silva Marques (ID 75) |
| **4** | **Dojo Ilha** (ID 8) | Jequiá Iate Clube | Praia do Zumbi, 28, Zumbi, CEP: 21930-150 | Rio de Janeiro | Mario Sergio Felix de Oliveira (ID 182) |
| **5** | **Hikari dojo** (ID 13) | Academia Top Defense | Rua Sorocaba, 258, Botafogo, CEP: 22271-110 | Rio de Janeiro | Marcelo Ribeiro de Britto (ID 163) |
| **6** | **Kaizen Dojō** (ID 18) | Academia Plotino Artes Marciais | Rua Pereira Nunes, 66, sala 301, Tijuca, CEP: 20540-132 | Rio de Janeiro | Joel Arthur Guimarães Junior (ID 121) |
| **7** | **Kurama Dera Dojo** (ID 12) | EISBE | Rua Bento Lisboa, 71, Catete, CEP: 22221-010 | Rio de Janeiro | Antonino Rodrigues Barreto Neto (ID 28) |
| **8** | **Ninjakan noite** (ID 16) | Ninjakan dojo | Estrada de Jacarepaguá, 6173, sala 204, Jacarepaguá, CEP: 22765-270 | Rio de Janeiro | Antonino Rodrigues Barreto Neto (ID 28) |
| **9** | **Midori Dojo Cefet Itaguaí** (ID 4) | Midori Dojo Cefet | Rodovia Mário Covas, lote J2, quadra J, Dist. Industrial, CEP: 23812-101 | Itaguaí | Gastão Luiz Videira Garcia Junior (ID 96) |
| **10** | **Nintai Budō** (ID 15) | Nintai Budo | Rua Visconde de Pirajá, 452, sala 201, Ipanema | Rio de Janeiro | Carlos Linhares Veloso Filho (ID 43) |

---

## 🛠️ Alterações Propostas

### 1. Modelo de Dados (`app/models.py`)

#### [MODIFY] [models.py](file:///c:/Users/DELL/OneDrive%20-%20Cerensa%20Tecnologia%20da%20Informa%C3%A7%C3%A3o%20S%20A/Documentos/IA/Vibe%20Coding/TesteAplicacao/app/models.py)
- Adicionar a coluna `academy` à classe `Dojo`:
  ```python
  class Dojo(Base):
      __tablename__ = "dojos"

      id = Column(Integer, primary_key=True, index=True)
      name = Column(String, nullable=False)
      academy = Column(String, nullable=True)  # <-- Nova Coluna!
      address = Column(String, nullable=False)
      city = Column(String, nullable=False, default="Rio de Janeiro")
      ...
  ```

---

### 2. Rotas & Interface (`app/routes/management.py` e `app/templates/page2_management.html`)

#### [MODIFY] [management.py](file:///c:/Users/DELL/OneDrive%20-%20Cerensa%20Tecnologia%20da%20Informa%C3%A7%C3%A3o%20S%20A/Documentos/IA/Vibe%20Coding/TesteAplicacao/app/routes/management.py)
- Atualizar os endpoints `/api/dojos/create` e `/api/dojos/{dojo_id}/update` para receber o parâmetro `academy: str = Form(None)` e salvar/atualizar o campo no banco de dados.

#### [MODIFY] [page2_management.html](file:///c:/Users/DELL/OneDrive%20-%20Cerensa%20Tecnologia%20da%20Informa%C3%A7%C3%A3o%20S%20A/Documentos/IA/Vibe%20Coding/TesteAplicacao/app/templates/page2_management.html)
- Adicionar o campo "Academia" nos modais de criação e edição de Dojos:
  - Novo input `<input type="text" id="dojo-academy" name="academy" class="form-input" placeholder="Ex: Academia Top Defense">`.
  - Novo input `<input type="text" id="edit-dojo-academy" name="academy" class="form-input">` no modal de edição.
  - Atualizar a função JS `openEditDojoModal` para preencher `edit-dojo-academy`.
- Exibir a informação de Academia nos cards de listagem de Dojos (ababaixo ou ao lado do nome do Dojo).

#### [MODIFY] [page1_dashboard.html](file:///c:/Users/DELL/OneDrive%20-%20Cerensa%20Tecnologia%20da%20Informa%C3%A7%C3%A3o%20S%20A/Documentos/IA/Vibe%20Coding/TesteAplicacao/app/templates/page1_dashboard.html)
- Exibir o nome da academia juntamente com o dojo nos cards laterais do dashboard (ex: *Dojo (Academia)*).

---

### 3. Migration & Carga de Dados (`scratch/update_dojos_from_excel.py`)

#### [NEW] [update_dojos_from_excel.py](file:///c:/Users/DELL/OneDrive%20-%20Cerensa%20Tecnologia%20da%20Informa%C3%A7%C3%A3o%20S%20A/Documentos/IA/Vibe%20Coding/TesteAplicacao/scratch/update_dojos_from_excel.py)
- Script Python idempotente que:
  1. Executa a alteração da tabela SQLite (`ALTER TABLE dojos ADD COLUMN academy VARCHAR;`) caso a coluna ainda não exista.
  2. Popula os campos `academy`, `address`, `city` e `responsible_sensei_id` nos registros existentes de acordo com o arquivo `DojoSenseiResponsavel.xlsx`.
  3. Atualiza a supervisão dos alunos vinculados aos dojos alterados (`supervisor_sensei_id = responsible_sensei_id`).

---

## 🧪 Plano de Verificação

### 1. Migração & Banco de Dados
- Executar `update_dojos_from_excel.py` e verificar a criação da coluna `academy` no SQLite sem perda de dados.
- Consultar a tabela `dojos` via script de verificação para validar o preenchimento de todos os 10 dojos.

### 2. Validação Web
- Testar a criação de um novo Dojo em `/management` com o campo Academia preenchido.
- Testar a edição de um Dojo existente em `/management` alterando o nome da Academia e Endereço.
- Verificar a exibição nos cards da listagem de Dojos em `page2_management.html` e nos cards laterais do Dashboard (`page1_dashboard.html`).
